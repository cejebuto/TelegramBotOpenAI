import os
import requests
from dotenv import load_dotenv
# Carga las variables de entorno del archivo .env
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def traduce_request(update, context,source_language = 'es',target_language = 'en'):

    api_key = GOOGLE_API_KEY
    if api_key is None:
        update.message.reply_text("Lo siento, no tengo una API key de Google para poder traducir")
        return False

    prompt_es = ' '.join(context.args)

    if not prompt_es:
        update.message.reply_text(
            "Se necesita un texto para poder traducir 🤓")
        return False

    # Envía el mensaje "Traduciendo..." y guarda el objeto del mensaje en una variable
    translating_message = update.message.reply_text("Traduciendo...")

    # Traduce el texto del español al inglés usando la función 'translate'
    prompt_en = translate(prompt_es, source_language, target_language)
    if prompt_en is None:
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=translating_message.message_id)
        update.message.reply_text("Lo siento, hubo un error al traducir el texto.")
        return False

    # Elimina el mensaje "Traduciendo..." una vez que se haya traducido el texto
    context.bot.delete_message(chat_id=update.message.chat_id, message_id=translating_message.message_id)

    return prompt_en

# No usar directamente esta función
def translate(text, source_language, target_language):
    api_key = GOOGLE_API_KEY

    if api_key == '':
        print(f"Falta la API key de Google.")
        return None

    url = "https://translation.googleapis.com/language/translate/v2"
    params = {
        "q": text,
        "source": source_language,
        "target": target_language,
        "key": api_key,
    }
    response = requests.post(url, params=params)
    try:
        if response.status_code == 200:
            result = response.json()
            translated_text = result["data"]["translations"][0]["translatedText"]
            return translated_text
        else:
            raise Exception(f"Error en la solicitud: {response.status_code}")
    except Exception as e:
        print(f"Error al traducir el texto: {e}")
        return None