import os
import tempfile
import openai
from pydub import AudioSegment
from dotenv import load_dotenv


# Carga las variables de entorno del archivo .env
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def validate_voice_note(context, update, copying_message):
    # Obtiene la información del archivo de la nota de voz
    voice_note = update.message.voice

    chat_id = update.message.chat_id
    message_id = copying_message.message_id

    # Define la lista de verificaciones
    check_list = [(voice_note.mime_type != "audio/ogg",
                   "Lo siento, solo puedo procesar notas de voz tomadas directamente desde Telegram ⚠"),
                  (voice_note.duration > 30,
                   "Lo siento, no puedo procesar notas de voz de más de 30 segundos 😒")]

    # Realiza las verificaciones
    for check, mensaje in check_list:
        if check:
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            update.message.reply_text(mensaje)
            return False  # Retorna False si no se pudo validar

    # Retorna True si pasó todas las verificaciones
    return True


def download_and_convert_voice_notes(update):
    try:
        temp_dir = os.path.join(os.getcwd(), "temp")

        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Descarga la nota de voz en un archivo temporal
        with tempfile.NamedTemporaryFile(delete=True, suffix=".ogg", dir=temp_dir) as voice_note_file:
            update.message.voice.get_file().download(out=voice_note_file)
            voice_note_file.flush()

            # Convierte la nota de voz a formato wav
            ogg_audio = AudioSegment.from_file(voice_note_file.name, format="ogg")
            wav_file_name = os.path.join(temp_dir, "voice_note.wav")
            ogg_audio.export(wav_file_name, format="wav")
            return wav_file_name

    except Exception as e:
        print(f"Error al descargar y convertir la nota de voz: {str(e)}")
        return False

def transcribe_voice_note(voice_note_file_path, context, update, copying_message):
    openai.api_key = OPENAI_API_KEY

    try:
        with open(voice_note_file_path, 'rb') as voice_note_file:
            transcript = openai.Audio.transcribe("whisper-1", voice_note_file)
            text = transcript.get("text")

        # Elimina el mensaje "Escuchando..." una vez que se haya recibido la respuesta
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)

        if text is None:
            try:
                context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)
            except Exception as e:
                print(f"Error al eliminar el mensaje 'Escuchando...': {e}")
            update.message.reply_text("Lo siento, no pude transcribir la nota de voz. Inténtalo de nuevo.")
            return False

        return text

    except Exception as e:
        print(f"Error al transcribir la nota de voz: {e}")
        return False

