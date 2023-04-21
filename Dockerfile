# Use una imagen de Python oficial como base
FROM python:3.9-slim

# Establezca el directorio de trabajo
WORKDIR /app

# Copie los archivos de requisitos
COPY requirements.txt .

# Instale las dependencias y ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --no-cache-dir -r requirements.txt

# Copie el resto de los archivos de la aplicación
COPY . .

# Exponga el puerto en el que se ejecutará la aplicación (opcional)
EXPOSE 8000

#Argumento
ARG RUN_MODE

# Inicie el bot de Telegram
CMD ["/bin/sh", "-c", "if [ \"$RUN_MODE\" = \"hupper\" ]; then hupper -m chatGPT_CJBT_bot; else python3 chatGPT_CJBT_bot.py; fi"]

