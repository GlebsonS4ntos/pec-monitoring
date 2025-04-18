import telegram
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

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
        rf"Olá {user.mention_html()}, seja bem-vindo! Aqui você será notificado sempre que algum serviço da Marques Consult apresentar instabilidade ou ficar fora do ar — e também quando tudo voltar ao normal.",
        reply_markup=ForceReply(selective=True),
    )

async def run_bot():
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    application.add_handler(CommandHandler("start", start))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()