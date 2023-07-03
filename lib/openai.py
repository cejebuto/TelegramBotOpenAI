import os
import tempfile
import openai
from pydub import AudioSegment
from dotenv import load_dotenv
from collections import deque


# Carga las variables de entorno del archivo .env
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MODEL_GPT = os.getenv('MODEL_GPT')

#Todo , sacar todas las reply_text para un modulo diferente o por defecto arriba.


def request_by_text(input_text,message_history,update, context):
    """
        @function request_by_text
        @param input_text: String
        @param update: Update
        @param context: CallbackContext
        @return: String
    """
    # Envía el mensaje "Respondiendo..." y guarda el objeto del mensaje en una variable
    copying_message = update.message.reply_text("Respondiendo...")

    # Obtiene el ID de usuario del mensaje
    user_id = update.message.from_user.id

    # Realiza la solicitud a Chat GPT
    response = chat_gpt_request(user_id, input_text,message_history)

    # Elimina el mensaje "Respondiendo..." una vez que se haya recibido la respuesta
    context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)

    # Guarda la respuesta del modelo en el historial de mensajes
    message_history[user_id].append({"role": "assistant", "content": response})

    update.message.reply_text(response)


def generate_image_request(update, context, translated_prompt=None):

    if translated_prompt is None:
        prompt = ' '.join(context.args)

        if not prompt:
            update.message.reply_text(
                "Por favor, ingresa un texto después del comando /imagina, /i como '/imagina un gato blanco siamés'.")
            return
    else:
        prompt = translated_prompt

    # Envía el mensaje "Imaginando..." y guarda el objeto del mensaje en una variable
    copying_message = update.message.reply_text("Imaginando...")

    # Configura tus credenciales de OpenAI
    openai.api_key = OPENAI_API_KEY

    try:
        # Genera la imagen con DALL·E
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"  # Puedes cambiar el tamaño según tus necesidades (256x256, 512x512, 1024x1024)
        )
    except Exception as e:
        print(f"Error al generar la imagen: {e}")
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)
        update.message.reply_text(
            "Lo siento, no puedo generar una imagen con ese contenido debido a que Open AI no me deja hacerlo 😒 ")
        return

    # Elimina el mensaje "Imaginando..." una vez que se haya recibido la respuesta
    context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)

    # Itera sobre las imágenes generadas en la respuesta
    for image_data in response['data']:
        image_url = image_data['url']

        # Envía la imagen generada al chat de Telegram
        update.message.reply_photo(photo=image_url)


def create_and_send_image(context, photo_path, update, copying_message):
    try:
        # Genera la variación de la imagen con OpenAI
        with open(photo_path, "rb") as image_file:
            response = openai.Image.create_variation(
                image=image_file,
                n=1,
                size="512x512"
            )
    except Exception as e:
        print(f"Error al generar la imagen: {e}")
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)
        update.message.reply_text(
            "Lo siento, no puedo generar una imagen similar debido a que Open AI no me deja hacerlo 😒")
        return

    # Itera sobre las imágenes generadas en la respuesta
    for image_data in response['data']:
        image_url = image_data['url']

        # Envía la imagen generada al chat de Telegram
        update.message.reply_photo(photo=image_url)

    context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)


#No usar directamente esta función
def chat_gpt_request(user_id, user_message,message_history):

    openai.api_key = OPENAI_API_KEY
    model_gpt = MODEL_GPT

    # Recupera el historial de mensajes del usuario o crea uno nuevo si no existe
    user_history = message_history.get(user_id, deque(maxlen=12))
    user_history.append({"role": "user", "content": user_message})
    message_history[user_id] = user_history

    # Convierte el objeto deque en una lista antes de pasarlo a la API
    user_history_list = list(user_history)

    # Asegura que la instrucción del sistema esté presente en el historial de mensajes
    system_instruction = {
        "role": "system",
        "content": "Eres un asistente virtual que dice solo información exacta y detalada."
    }

    messages_with_instruction = [system_instruction] + user_history_list

    # Realiza la solicitud a la API de ChatCompletion
    response = openai.ChatCompletion.create(
        model=model_gpt,
        messages=messages_with_instruction,
        temperature=0.7,
        max_tokens=200,
        n=1
    )

    # Extrae y devuelve la respuesta generada por el modelo
    model_response = response.choices[0].message.content
    return model_response