#####     G-BOT
#BOT IMAGEN

import os
import base64
import telebot
from groq import Groq
from dotenv import load_dotenv
from PIL import Image
import io
import requests

load_dotenv()

# Configuración
TOKEN_BOT_TELEGRAM = os.getenv('TELEGRAM_BOT_TOKEN')
CLAVE_API_GROQ = os.getenv('GROQ_API_KEY')

if not TOKEN_BOT_TELEGRAM:
    raise ValueError("TELEGRAM_BOT_TOKEN no está configurado")
if not CLAVE_API_GROQ:
    raise ValueError("GROQ_API_KEY no está configurado")

# Inicialización
bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)
cliente_groq = Groq(api_key=CLAVE_API_GROQ)

# Convierte imagen a base64
def imagen_a_base64(ruta_o_bytes_imagen):
    """Convierte una imagen a base64"""
    try:
        if isinstance(ruta_o_bytes_imagen, bytes):
            return base64.b64encode(ruta_o_bytes_imagen).decode('utf-8')
        else:
            with open(ruta_o_bytes_imagen, "rb") as archivo_imagen:
                return base64.b64encode(archivo_imagen.read()).decode('utf-8')
    except Exception as e:
        print(f"Error al convertir imagen a base64: {e}")
        return None

# Envía imagen a Groq para describirla
def describir_imagen_con_groq(imagen_base64):
    """Envía la imagen a Groq y obtiene la descripción"""
    try:
        completado_chat = cliente_groq.chat.completions.create(
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text",
                     "text": "Por favor, describe esta imagen de manera detallada en español."},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{imagen_base64}"}}
                ]
            }],
            model="llama-3.2-11b-vision-preview",
            temperature=0.7,
            max_tokens=1000
        )
        return completado_chat.choices[0].message.content
    except Exception as e:
        print(f"Error al describir imagen con Groq: {e}")
        return None

# /start
@bot.message_handler(commands=['start'])
def enviar_bienvenida(mensaje):
    """Mensaje de bienvenida"""
    texto_bienvenida = """
¡Hola! 👋 Soy un bot que describe imágenes.

📸 Envíame una imagen y te daré una descripción detallada.
🤖 Uso Groq AI para analizar las imágenes.
Usa /help para más información.
"""
    bot.reply_to(mensaje, texto_bienvenida)

# /help
@bot.message_handler(commands=['help'])
def enviar_ayuda(mensaje):
    """Mensaje de ayuda"""
    texto_ayuda = """
🔧 **Comandos:**
/start - Inicia el bot
/help - Muestra esta ayuda

📸 Envía una imagen y recibirás una descripción detallada.
"""
    bot.reply_to(mensaje, texto_ayuda)

# Manejo de imágenes
@bot.message_handler(content_types=['photo'])
def manejar_foto(mensaje):
    """Procesa imágenes enviadas"""
    try:
        bot.reply_to(mensaje, "📸 Imagen recibida. Analizando... ⏳")
        foto = mensaje.photo[-1]
        info_archivo = bot.get_file(foto.file_id)
        archivo_descargado = bot.download_file(info_archivo.file_path)
        imagen_base64 = imagen_a_base64(archivo_descargado)

        if not imagen_base64:
            bot.reply_to(mensaje, "❌ Error al procesar la imagen.")
            return

        descripcion = describir_imagen_con_groq(imagen_base64)
        if descripcion:
            respuesta = f"🤖 **Descripción:**\n\n{descripcion}"
            bot.reply_to(mensaje, respuesta, parse_mode='Markdown')
        else:
            bot.reply_to(mensaje, "❌ No pude analizar la imagen.")
    except Exception as e:
        print(f"Error al procesar imagen: {e}")
        bot.reply_to(mensaje, "❌ Error al procesar la imagen.")

# Otros mensajes
@bot.message_handler(func=lambda mensaje: True)
def manejar_otros_mensajes(mensaje):
    """Maneja mensajes que no son imágenes"""
    bot.reply_to(mensaje, """
📝 Solo puedo procesar imágenes por ahora.
📸 Envía una imagen o usa /help.
""")

if __name__ == '__main__':
    print("🤖 Bot iniciado...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error al iniciar el bot: {e}")
