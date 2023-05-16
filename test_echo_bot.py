import asyncio
import logging
import os
import argparse
from main_gpt import *

from pprint import pprint
from dotenv import load_dotenv
from telegram import (
    Update, Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
    MenuButtonCommands,
    CallbackQuery,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters, 
    CallbackQueryHandler
)
# import Daemon from demon


load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')


help_log = 'without the -l option write to telegram.log otherwise print to file'
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--dry-run', action='store_true')
parser.add_argument('-f', '--log', action='store', default='telegram.log', const='', nargs='?', help=help_log)
parser.add_argument('-l', '--log-level', action='store', type=int)
parser.add_argument('-tl', '--time-live', action='store', default=None, help='Time to live the process')
args = parser.parse_args()


FORMAT = '%(asctime)s::%(levelname)s::%(message)s'
logging.basicConfig(filename=args.log, format=FORMAT, level=args.log_level)
logger = logging.getLogger(__name__)

STOP = '0'
CHAT = '1'
START = '2'
CALL_START = '3'

role = Roles().ASSISTANT
ask_to_ai = Create_Responce(role)
logging.debug(ask_to_ai)


async def tip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Text on button and return "pattern" for CallbackQueryHandler(function, pattern) inside the state dictionary
    # For more details see https://docs.python-telegram-bot.org/en/stable/examples.inlinekeyboard2.html
    button1 = InlineKeyboardButton('Get Started!', callback_data=str(START))
    keyboard = [[button1]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text='Start Chat', reply_markup=reply_markup)

    logging.info(f'Current state: {START} and {CHAT}')
    return START


async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initializing conversation with ChatGPT"""
    keyboard = [['START']]

    # Recidved text for user
    if not update.message:
        return CHAT

    await update.message.reply_text(
        'Conversation with ChatGPT is starting...',
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            # one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    return CHAT


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Stop conversation...')
    return STOP


async def echofn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if not message == 'START':

        ask_to_ai.message = f'{update.message.text}'
        ask_to_ai.create_message()
        request = ask_to_ai.ask()
        logging.debug(f'Requets to ChatGPT: {request}')

        parser = ChatParser(request)
        answer = parser.message()
        ask_to_ai.safe_dialog(answer)


        logging.info(f'{update.message}')
        logging.info(f'{answer}')
        await update.message.reply_text(answer)


def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    tip_handler = CommandHandler('help', tip)
    start_handler = CommandHandler('start', start_conversation)
    call_start = CallbackQueryHandler(start_conversation, pattern="^" + str(START) + "$")
    stop_handler = CommandHandler('stop', stop)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echofn)

    conv_handler = ConversationHandler(
        entry_points=[start_handler],
        states = {
            START: [
                start_handler,
                # call_start,
            ],
            # CALL_START: [
            #     start_handler,
            # ],
            CHAT: [
                echo_handler,
            ],
        },
        fallbacks=[
            stop_handler, 
            start_handler,
            call_start,
        ],
    )
    logging.info(f'Current state: {START} and {CHAT}')

    application.add_handler(tip_handler)
    application.add_handler(conv_handler)
    application.run_polling()




if __name__ == '__main__':
    main()
    # d = Daemon(testfn)
    # d.start()
    # d.kill(15)
 
