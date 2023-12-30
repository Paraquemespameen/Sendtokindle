#!/usr/bin/python3
"""Archivo pincipal para instanciar los correos y llamar al bot"""
import os
import logging
from dotenv import load_dotenv
from correo import CorreoEnviar
from send_bot import ReenvioBot

# Cargar variables desde archivo .env
load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(name)s - %(levelname)s - %(message)s",
    level=logging.ERROR
)

# Valores en el archivo .env
usuarios = [int(os.getenv("ID_UNO")), int(os.getenv("ID_DOS"))]

#Instanciado de correos
correo_uno = CorreoEnviar(
    correo_from=os.getenv("EMAIL_FROM"),
    correo_pass=os.getenv("EMAIL_PASSWORD"),
    correo_to=os.getenv("EMAIL_TO_UNO"),
    smtp_server=os.getenv("SMTP_SERVER"),
    smtp_port=int(os.getenv("SMTP_PORT"))
)

correo_dos = CorreoEnviar(
    correo_from=os.getenv("EMAIL_FROM"),
    correo_pass=os.getenv("EMAIL_PASSWORD"),
    correo_to=os.getenv("EMAIL_TO_DOS"),
    smtp_server=os.getenv("SMTP_SERVER"),
    smtp_port=int(os.getenv("SMTP_PORT"))
)

#Diccionario con correos
correo_destino = {
    "Uno": correo_uno,
    "Dos": correo_dos,
    "default": correo_uno  # Seleccionamos uno por defecto
}

bot = ReenvioBot(
    token=os.getenv("TELEGRAM_TOKEN"),
    id_usuarios_permitidos=usuarios,
    correo_destino=correo_destino
)

if __name__ == "__main__":
    bot.run()
