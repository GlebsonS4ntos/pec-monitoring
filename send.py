import telegram
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import csv

def armazenar_usuario(usuarioId):
    if not os.path.exists("usuarios.txt"):
        with open("usuarios.txt", "w") as f:
            f.write(f"{usuarioId}\n")
    else:
        with open("usuarios.txt", "r") as f:
            usuarios = f.read().splitlines()

        if str(usuarioId) not in usuarios:
            with open("usuarios.txt", "a") as f:
                f.write(f"{usuarioId}\n")

def obter_usuarios():
    if not os.path.exists("usuarios.txt"):
        return []
    else:
        with open("usuarios.txt", "r") as f:
            return f.read().splitlines()

def limpar_usuario(usuario):
    with open("usuarios.txt", "r") as f:
        usuarios = f.read().splitlines()

    with open("usuarios.txt", "w") as f:
        for u in usuarios:
            if u != str(usuario): 
                f.write(f"{u}\n")

async def enviar_mensagem(mensagem):
    from telegram.error import TelegramError

    bot = telegram.Bot(token=os.getenv("TELEGRAM_TOKEN"))
    for usuario in obter_usuarios():
        try:
            await bot.send_message(chat_id=usuario, text=mensagem)
        except TelegramError as e:
            limpar_usuario(usuario)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    armazenar_usuario(user.id)

    await update.message.reply_html(
    rf"Olá {user.mention_html()}, seja bem-vindo! Aqui você será notificado sempre que algum serviço da {os.getenv('ENTERPRISE')} apresentar instabilidade ou ficar fora do ar, além de ser avisado quando os serviços forem normalizados. Use /help para ver os comandos disponíveis."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = ""

    with open('service_urls.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for linha in reader:
            if linha[2] == "false":
                message += f"{linha[0]} - Offline ❌ \n"
            else:
                message += f"{linha[0]} - Online ✅ \n"
            
    
    await update.message.reply_html(
        message,
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Use /status para se informar sobre o status atual dos serviços. Obs: a última verificação ocorreu, no máximo, há 10 segundos.")


async def run_bot():
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("help", help))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()