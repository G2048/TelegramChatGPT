import asyncio
import logging
from os import getenv
from pprint import pprint
from dotenv import load_dotenv
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters


load_dotenv()
TOKEN = getenv('TELEGRAM_TOKEN')

FORMAT = '%(asctime)s::%(levelname)s::%(message)s'
logging.basicConfig(filename='telegram.log', format=FORMAT, level=logging.INFO)



async def startfn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = f'{update.message.from_user.first_name} say: {update.message.text}'
    logging.info(f'{update.message}')
    logging.info(f'{message}')
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='MarkdownV2')
    await context.bot.forward_message(chat_id=update.effective_chat.id, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)




if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    # start_handler = CommandHandler('start', startfn)
    start_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), startfn)
    application.add_handler(start_handler)
    application.run_polling()
