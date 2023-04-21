import os
from dotenv import load_dotenv
import logging
from collections import deque
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
import tempfile
from pydub import AudioSegment
import json


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carga las variables de entorno del archivo .env
load_dotenv()

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

GPT_API_URL = 'https://api.openai.com/v1/chat/completions'
GPT_HEADERS = {
    'Authorization': f'Bearer {OPENAI_API_KEY}',
    'Content-Type': 'application/json',
}

# Carga los IDs de usuario permitidos desde un archivo JSON
with open('allowed_user_ids.json', 'r') as f:
    ALLOWED_USER_IDS = json.load(f)

# Almacena el historial de mensajes para cada usuario
message_history = {}


def error_handler(update: Update, context: CallbackContext) -> None:
    logging.error(f'Error en la actualización {update} causado por {context.error}')


def generate_image(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id in ALLOWED_USER_IDS:
        prompt = ' '.join(context.args)

        if not prompt:
            update.message.reply_text(
                "Por favor, ingresa un texto después del comando /imagina, como '/imagina un gato blanco siamés'.")
            return

        # Envía el mensaje "Copiando..." y guarda el objeto del mensaje en una variable
        copying_message = update.message.reply_text("Imaginando...")

        # Configura tus credenciales de OpenAI
        openai.api_key = OPENAI_API_KEY

        # Genera la imagen con DALL·E
        response = openai.Image.create(
            prompt=prompt,
            n=2,
            size="512x512"  # Puedes cambiar el tamaño según tus necesidades
        )

        # Elimina el mensaje "Imaginando..." una vez que se haya recibido la respuesta
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)

        image_url = response['data'][0]['url']

        # Envía la imagen generada al chat de Telegram
        update.message.reply_photo(photo=image_url)

    else:
        # Si el ID de usuario no está en la lista de ID permitidos, envía un mensaje de error
        update.message.reply_text("Lo siento, este bot es privado y solo está disponible para usuarios autorizados.")

def transcribe_voice_note(voice_note_file):
    openai.api_key = OPENAI_API_KEY

    try:
        transcript = openai.Audio.transcribe("whisper-1", voice_note_file)
        text = transcript.get("text")
        return text
    except Exception as e:
        print(f"Error al transcribir la nota de voz: {e}")
        return None


def start(update: Update, context: CallbackContext):
    update.message.reply_text('¡Hola! Envía un mensaje y usaré ChatGPT para responderte. :)')


def chat_gpt_request(user_id, user_message):
    openai.api_key = OPENAI_API_KEY

    # Recupera el historial de mensajes del usuario o crea uno nuevo si no existe
    user_history = message_history.get(user_id, deque(maxlen=12))
    user_history.append({"role": "user", "content": user_message})
    message_history[user_id] = user_history

    # Convierte el objeto deque en una lista antes de pasarlo a la API
    user_history_list = list(user_history)

    # Asegura que la instrucción del sistema esté presente en el historial de mensajes
    system_instruction = {
        "role": "system",
        "content": "Eres un asistente virtual que habla con modismos."
    }

    messages_with_instruction = [system_instruction] + user_history_list

    # Realiza la solicitud a la API de ChatCompletion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # messages=user_history_list,
        messages=messages_with_instruction,
        temperature=0.7,
        max_tokens=200,
        n=1
    )

    # Extrae y devuelve la respuesta generada por el modelo
    model_response = response.choices[0].message.content
    return model_response


def chat_response(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id in ALLOWED_USER_IDS:
        # Comprueba si el mensaje es una nota de voz
        if update.message.voice:

            print("Procesando nota de voz")

            # Envía el mensaje "Escuchando..." y guarda el objeto del mensaje en una variable
            copying_message = update.message.reply_text("Escuchando...")

            # Obtiene la información del archivo de la nota de voz
            voice_note = update.message.voice

            # Imprime el mime_type y la duración de la nota de voz
            #print("MIME Type:", voice_note.mime_type)
            #print("Duration:", voice_note.duration)

            temp_dir = os.path.join(os.getcwd(), "temp")

            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Descarga la nota de voz en un archivo temporal
            with tempfile.NamedTemporaryFile(delete=True, suffix=".ogg", dir=temp_dir) as voice_note_file:
                update.message.voice.get_file().download(out=voice_note_file)
                voice_note_file.flush()
                voice_note_file.seek(0)

                # Convierte la nota de voz a formato wav
                ogg_audio = AudioSegment.from_file(voice_note_file.name, format="ogg")
                with tempfile.NamedTemporaryFile(delete=True, suffix=".wav", dir=temp_dir) as wav_file:
                    ogg_audio.export(wav_file.name, format="wav")
                    wav_file.flush()
                    wav_file.seek(0)

                    input_text = transcribe_voice_note(wav_file)

            # Elimina el mensaje "Escuchando..." una vez que se haya recibido la respuesta
            context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)

            if input_text is None:
                try:
                    context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)
                except Exception as e:
                    print(f"Error al eliminar el mensaje 'Escuchando...': {e}")

                update.message.reply_text("Lo siento, no pude transcribir la nota de voz. Inténtalo de nuevo.")
                return

        elif update.message.text:
            input_text = update.message.text
        else:
            return

        # Envía el mensaje "Copiando..." y guarda el objeto del mensaje en una variable
        copying_message = update.message.reply_text("Copiando...")

        # Realiza la solicitud a Chat GPT
        response = chat_gpt_request(user_id, input_text)

        # Elimina el mensaje "Copiando..." una vez que se haya recibido la respuesta
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)

        # Guarda la respuesta del modelo en el historial de mensajes
        message_history[user_id].append({"role": "assistant", "content": response})

        update.message.reply_text(response)
    else:
        update.message.reply_text("Lo siento, este bot es privado y solo está disponible para usuarios autorizados.")



def main():
    updater = Updater(TELEGRAM_API_TOKEN)

    dp = updater.dispatcher
    dp.add_error_handler(error_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("imagina", generate_image, pass_args=True))
    #dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat_response))
    dp.add_handler(MessageHandler((Filters.text | Filters.voice) & ~Filters.command, chat_response))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
