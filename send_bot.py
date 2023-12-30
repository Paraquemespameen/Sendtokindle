"""Bot de telegram para captar archivo y enviarlo por correo a un destinatario"""

import json
from telegram import Update, BotCommand
from telegram.ext import (Application, ApplicationBuilder, CommandHandler,
                        ContextTypes, MessageHandler, filters)
from correo import CorreoEnviar


class ReenvioBot:
    def __init__(self, token, id_usuarios_permitidos, correo_destino):
        self.token = token
        self.id_usuarios_permitidos = id_usuarios_permitidos
        self.correo_destino = correo_destino
        self.correo_en_uso = "default"

        async def post_init(application: Application) -> None:
            #función para crear el botón de menú, haciendo una lista con el json
            with open("./texto/comandos.json", "r", encoding="UTF-8") as c:
                self.comando = list(json.load(c).items())

            await application.bot.set_my_commands(self.comando)
            
        self.app = ApplicationBuilder().token(self.token).post_init(post_init).build()  

        # Añadimos los comandos de uso
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("info", self.info))
        self.app.add_handler(CommandHandler("destino",
                                                    self.correo_selec))
        self.app.add_handler(MessageHandler(filters.ATTACHMENT,
                                                    self.archivo_manejo))
        
        #Para manejar los mensajes con el JSON
        with open("./texto/mensajes.json", "r", encoding="UTF-8") as f:
            self.mensaje = json.load(f)

    def is_user_allowed(self, user_id):
        #Función para control de usuario
        self.user_id = user_id
        return user_id in self.id_usuarios_permitidos

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        #Comando /start
        self.name = update.message.from_user.name
        self.user_id = update.message.from_user.id
        if self.is_user_allowed(self.user_id):
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                            text=self.mensaje["Bienvenida"].format(self.name))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                            text=self.mensaje["Acceso denegado"].format(self.name))
    
    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        #Comando /info
        self.user_id = update.message.from_user.id
        if self.is_user_allowed(self.user_id):
            #Partido en dos mensajes, uno para informar comandos y otro para citar correo en uso
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                            text=self.mensaje["Info"])
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                            text=self.mensaje["Default"].format(self.correo_en_uso))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                            text=self.mensaje["Acceso denegado"].format(self.name))

    async def correo_selec(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        #Cambio de correo de destino, menú /correo_selec
        self.args = context.args
        if self.args:
            self.correo_nuevo = self.args[0]
            if self.correo_nuevo in self.correo_destino:
                #Comprobación redundante por si está mal escrito
                self.correo_en_uso = self.correo_nuevo
                texto = self.mensaje["Correo destino"].format(self.correo_en_uso)
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                                text=texto)
            else:
                texto=self.mensaje["Seleccionado no incluido"].format(self.correo_nuevo)
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                                text=texto)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                            text=self.mensaje["No seleccionado"])

    async def archivo_manejo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        #Captación y envío de archivo por correo
        self.user_id = update.message.from_user.id
        if self.is_user_allowed(self.user_id):
            self.file_name = update.message.document.file_name  # El nombre original del archivo
            try:
                self.file_id = update.message.document.file_id
                self.file_get = await context.bot.get_file(self.file_id)
                #hay que guardarlo en el disco, porque en la memoria no lo he conseguido
                await self.file_get.download_to_drive(f'{self.file_name}')
            except:
                texto = self.mensaje["Archivo interno"]
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                        text=texto)            
            #Envío y mensajes
            correodestino = self.correo_destino.get(self.correo_en_uso)
            if correodestino:
                CorreoEnviar.enviar_correo(self, f'{self.file_name}', self.file_name, correodestino)
                filename=self.file_name
                texto = self.mensaje["Enviado"].format(filename, correodestino.correo_to)
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                        text=texto)
            else:
                await context.bot.send_message(self.mensaje["Error envío"])

    def run(self):
        # Start the Bot
        self.app.run_polling()
        self.app.shutdown()
