def procesar_nota_de_voz(voice_note, context, update, copying_message):
    if voice_note.mime_type != "audio/ogg":
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)
        mensaje = "Lo siento, solo puedo procesar notas de voz tomadas directamente desde Telegram ⚠"
        update.message.reply_text(mensaje)
        return mensaje

    if voice_note.duration > 30:
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=copying_message.message_id)
        mensaje = "Lo siento, no puedo procesar notas de voz de más de 30 segundos 😒"
        update.message.reply_text(mensaje)
        return mensaje

def B():
    print("Función B ejecutada.")