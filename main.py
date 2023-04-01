import asyncio
import logging
from os import getenv, fork
from pprint import pprint
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import argparse


load_dotenv()
TOKEN = getenv('TELEGRAM_TOKEN')


help_log = 'without the -l option write to telegram.log otherwise print to file'
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--test', action='store_true')
parser.add_argument('-l', '--log', action='store', default='telegram.log', const='', nargs='?', help=help_log)
args = parser.parse_args()


FORMAT = '%(asctime)s::%(levelname)s::%(message)s'
logging.basicConfig(filename=args.log, format=FORMAT, level=logging.INFO)


class daemon():

    def __init__(self,):
        pass


def demonification(fn):
    def wrapper(*args):
        pid = fork()

        if not pid:
            logging.info(f'Pid is {pid}')
            logging.info('Start daemon!')
            fn()
        else:
            exit(0)
    return wrapper







async def echofn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.reply_text
    # message = f'{update.message.from_user.first_name} say: {update.message.text}'
    logging.info(f'{update.message}')
    logging.info(f'{message}')
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='MarkdownV2')
    await context.bot.forward_message(chat_id=update.effective_chat.id, from_chat_id=update.effective_chat.id, 
                                      message_id=update.message.message_id)


@demonification
def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()
    # start_handler = CommandHandler('start', startfn)
    start_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echofn)
    application.add_handler(start_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
