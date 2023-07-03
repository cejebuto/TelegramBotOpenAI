import os

import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

#mis propias librerias
from lib.audio import validate_voice_note, download_and_convert_voice_notes, transcribe_voice_note
from lib.openai import request_by_text,generate_image_request
from lib.google import traduce_request
from lib.allowed_user import is_user_allowed

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carga las variables de entorno del archivo .env
load_dotenv()
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

# Almacena el historial de mensajes para cada usuario
message_history = {}

def error_handler(update: Update, context: CallbackContext) -> None:
    logging.error(f'Error en la actualización {update} causado por {context.error}')

#esto es un decorador
def message_type_middleware(func):
    def inner(update: Update, context: CallbackContext):
        message_type = None
        if update.message.voice:
            message_type = 'voice'
        elif update.message.photo:
            message_type = 'photo'
        elif update.message.text:
            message_type = 'text'
        else:
            return

        return func(update, context, message_type)

    return inner

#OFUNCIONES DEL MENU PRINCIPAL
#esta es la opcion de imaginar /imagina
def generate_image(update, context, translated_prompt=None):

    if not is_user_allowed(update):
        update.message.reply_text("Lo siento, este bot es privado y solo está disponible para usuarios autorizados.")
        update.message.reply_text("/help para ayuda")
        return

    generate_image_request(update, context, translated_prompt=None)

#esta es la opcion de traducir e imaginar /i
def traduce_generate_image(update: Update, context: CallbackContext):

    if not is_user_allowed(update):
        update.message.reply_text("Lo siento, este bot es privado y solo está disponible para usuarios autorizados.")
        update.message.reply_text("/help para ayuda")
        return

    # Traduzco el contenido del mensaje
    prompt_en = traduce_request(update, context)
    if not prompt_en:
        return

    # Llama a generate_image con el texto traducido
    generate_image_request(update, context, translated_prompt=prompt_en)

#esta es la opcion de ayuda /help
def help (update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not is_user_allowed(update):
        update.message.reply_text("Solicita acceso a @cejebuto con tu ID de usuario de Telegram : " + str(user_id))
        return
    update.message.reply_text("Este bot usa ChatGPT para generar respuestas a tus mensajes. Puedes usarlo para chatear con un bot de IA. ")
    update.message.reply_text("Puedes usar /imagina para generar imágenes a partir de texto. ")
    update.message.reply_text("Puedes usar /i para traducir el texto a inglés y luego generar imágenes. ")

#esta es la opcion de bienvenida /start
def start(update: Update , context: CallbackContext):
    if not is_user_allowed(update):
        update.message.reply_text("Lo siento, este bot es privado y solo está disponible para usuarios autorizados.")
        update.message.reply_text("/help para ayuda")
        return
    update.message.reply_text('¡Hola! Envía un mensaje y usaré ChatGPT para responderte 😁 ')

#Este es el controlador , recibe voz, imgen o texto
@message_type_middleware
def chat_response(update: Update, context: CallbackContext,message_type):

    switch_cases = {
        'voice': handle_voice,
        'photo': handle_photo,
        'text': handle_text
    }
    switch_cases.get(message_type, lambda u, c: None)(update, context)

#FUNCIONES DE CONTROLADORES PRINCIPALES
#Texto
def handle_text(update: Update, context: CallbackContext):
    #Obtenemos el texto del mensaje
    input_text = update.message.text
    request_by_text(input_text, message_history, update, context)

#Voz
def handle_voice(update: Update, context: CallbackContext):
    print("Procesando nota de voz")

    # Envía el mensaje "Escuchando..." y guarda el objeto del mensaje en una variable
    copying_message = update.message.reply_text("Escuchando...")

    # Compruebo la nota de voz
    if not validate_voice_note(context, update, copying_message):
        return

    # Guardo la nota de voz y la convierto
    wav_file = download_and_convert_voice_notes(update)
    if not wav_file:
        return

    # Transcribo la nota de voz
    input_text = transcribe_voice_note(wav_file, context, update, copying_message)
    if not input_text:
        return

    request_by_text(input_text,message_history, update, context)

#Imagen
def handle_photo(update: Update, context: CallbackContext):
    update.message.reply_text("Foto")

#MAIN
def main():
    updater = Updater(TELEGRAM_API_TOKEN)

    dp = updater.dispatcher
    dp.add_error_handler(error_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("imagina", generate_image, pass_args=True))
    dp.add_handler(CommandHandler("i", traduce_generate_image, pass_args=True))
    dp.add_handler(MessageHandler((Filters.text | Filters.voice | Filters.photo) & ~Filters.command, chat_response))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
