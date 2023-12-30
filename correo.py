"""Creación de un correo electrónico y envío por GMAIL"""

import os
import smtplib
from email.message import EmailMessage

class CorreoEnviar:
    def __init__(self, correo_from, correo_pass, correo_to, smtp_server, smtp_port):
        self.correo_from = correo_from
        self.correo_password = correo_pass
        self.correo_to = correo_to
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def enviar_correo(self, archivo: str, nombre_archivo: str, correo_destino) -> None:
        # Crear mensaje de correo
        msg = EmailMessage()
        msg.set_content("Ver archivo adjunto")

        msg['From'] = correo_destino.correo_from
        msg['To'] = correo_destino.correo_to
        msg['Subject'] = f"Archivo desde el bot: {nombre_archivo}"

        # Adjuntar el archivo al correo con el nombre original
        with open(archivo, 'rb') as file:
            msg.add_attachment(file.read(),
                                maintype="application",
                                subtype="epub+zip",
                                filename=nombre_archivo)
        os.remove(archivo)
        
        # Conectar el servidor con SSL y enviar el correo
        with smtplib.SMTP_SSL(correo_destino.smtp_server, correo_destino.smtp_port) as server:
            server.login(correo_destino.correo_from, correo_destino.correo_password)
            server.send_message(msg)
            