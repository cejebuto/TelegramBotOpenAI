# ChatGPT Telegram Bot

Este repositorio contiene el código fuente para un bot de Telegram basado en ChatGPT de OpenAI.

## Requisitos

Debe tener una cuenta de Telegram y un bot de Telegram configurado. Puede encontrar instrucciones para crear un bot de Telegram en [este enlace](https://core.telegram.org/bots#6-botfather).

También debe tener una clave de API de OpenAI. Puede encontrar instrucciones para obtener una clave de API de OpenAI en [este enlace](https://platform.openai.com/account/api-keys).

## Configuración

1. Copie `.env.example` a un nuevo archivo llamado `.env`.
2. Complete las variables de entorno en el archivo `.env`:

```
TELEGRAM_API_TOKEN=<your_telegram_api_token>
OPENAI_API_KEY=<your_openai_api_key>
MODEL_GPT=<model_gpt> (el modelo que desee usar)
GOOGLE_API_KEY=<your_google_api_key> (opcional para usar traductor)
```

3. Copie `allowed_user_ids.json.example` a `allowed_user_ids.json` y separe por comas los id's de telegram que desee permitir que usen el bot:
```
[
    <your_telegram_user_id>,
    <your_telegram_user_id>,
]
```
- Puede encontrar su id de telegram en @userinfobot


## Construcción de la imagen Docker

1. Construye la imagen de Docker:

```sh
docker build -t chatgpt_bot .
```

## Ejecución

### Linux / macOS / Windows

```bash
docker run --rm -it --env-file .env chatgpt_bot
```

## Desarrollo

### con hupper (actualización en caliente)

#### Linux / macOS 

```bash
docker run --rm -it --env-file .env -v $(pwd):/app -e RUN_MODE=hupper chatgpt_bot
```

#### Windows

```bash
docker run --rm -it --env-file .env -v ${PWD}:/app -e RUN_MODE=hupper chatgpt_bot
```


## Uso en Telegram

**Uso común**

- `<texto>`: Genera texto a partir de lo que se solicite.
- `<audio>`: Acepta notas de voz y genera texto a partir de ellas.
- `<imagenes>`: Acepta imagenes y el bot crea una similar


**Comandos disponibles:**

- `/imagina <texto>`: Genera imágenes a partir de texto.
- `/i <texto>`: Traduce el texto a inglés y luego genera imágenes.
- `/help`: Muestra la ayuda.
- `/start`: Mensaje de bienvenida.


---

Sigue las instrucciones anteriores para configurar y ejecutar el bot de Telegram con ChatGPT. Puedes ejecutarlo con o sin hupper, según tus preferencias y necesidades.


## Licencia
GNU General Public License v3.0