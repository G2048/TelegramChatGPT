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

STOP ='0'
CHAT ='1'
START ='2'
CALL_START ='3'
MIDDLE ='4'
MENU ='5'
GREETINGS = """Hello! I am an AI language model designed to assist and communicate with users. I am programmed to understand and respond to natural language queries and provide helpful responses. My purpose is to make tasks easier and more efficient for users."""


role = Roles().ASSISTANT
ask_to_ai = Create_Responce(role)
logging.debug(ask_to_ai)


async def tip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Text on button and return "pattern" for CallbackQueryHandler(function, pattern) inside the state dictionary
    # For more details see https://docs.python-telegram-bot.org/en/stable/examples.inlinekeyboard2.html
    button1 = InlineKeyboardButton('Get Started!', callback_data='/start')
    keyboard = [[button1]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text='Start Chat', reply_markup=reply_markup)

    logging.info(f'Current state: {START} and {CHAT}')
    return START


# Stop Sending messages to GPT and clear the VAULT of messages
async def stop2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop the conversation with ChatGPT"""
    ask_to_ai.VAULT = []
    keyboard = [['/start']]

    await update.message.reply_text(
        'Stop conversation...',
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            input_field_placeholder='STOP',
        ),
    )
    await update.message.delete()
    return START


async def conversation_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['STOP'], ['Change the Dialoge']]

    keyboard_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)
    await update.message.delete()
    await update.message.reply_text(
        'Conversation keyboard',
        reply_markup=keyboard_markup
    )
    return MIDDLE


async def start_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """It's start menu for choise of dialogue and starting of conversation"""
    keyboard = [['START'], ['Get the list of Dialoge']]

    keyboard_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)
    await update.message.delete()
    await update.message.reply_text(
        'Menu of choise',
        reply_markup=keyboard_markup
    )
    return MIDDLE


async def proxy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    logging.info(f'Start echo function. Message: {message}')

    ask_to_ai.message = f'{update.message.text}'
    ask_to_ai.create_message()
    request = ask_to_ai.ask()
    logging.debug(f'Requets to ChatGPT: {request}')

    parser = ChatParser(request)
    answer = parser.message()
    ask_to_ai.safe_dialog(answer)


    logging.info(f'{update.message}')
    logging.info(f'{answer}')
    await update.message.reply_markdown_v2(answer)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    await update.message.reply_text(message)
    logging.info(f'Start echo function. Message: {message}')


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    await update.message.reply_text('Bye!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def middle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get, handle and route from start menu"""
    message = update.message.text

    if message == 'START':
        keyboard = [['STOP'], ['Change the Dialoge']]

        # Get the keyboard along to conversation
        keyboard_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)
        await update.message.reply_text('Start conversation with ChatGPT!', reply_markup=keyboard_markup)

        # await update.message.delete()
        await update.message.reply_text(GREETINGS)
        return CHAT

    elif message == 'Change the Dialoge':
        # Here will be placed a keyboard
        return MENU


def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    tip_handler = CommandHandler('help', tip)
    start_handler = CommandHandler('start', start_keyboard)
    # keyboard_handler = MessageHandler(filters.Regex('^(START|Change the Dialoge)$') & ~(filters.COMMAND | filters.Regex('^STOP$')), conversation_keyboard)
    middle_handler = MessageHandler(filters.Regex('^(START|Change the Dialoge)$') & ~(filters.COMMAND | filters.Regex('^STOP$')), middle)
    # call_start = CallbackQueryHandler(start_conversation, pattern="^" + str('START') + "$")
    stop_handler = CommandHandler('stop', stop)
    # forward_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), proxy_message)
    forward_handler = MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex('^STOP$')), echo)
    stop_handler = MessageHandler(filters.Regex('^STOP$'), stop)

    conv_handler = ConversationHandler(
        entry_points=[start_handler,],
        states = {

            START: [
            ],

            MIDDLE: [
                middle_handler,
            ],

            # CALL_START: [
            #     start_handler,
            # ],

            CHAT: [
                forward_handler,
            ],

            MENU: [

            ],
        },

        fallbacks=[ 
            stop_handler,
        ],
    )
    logging.info(f'Current state: {START} and {CHAT}')

    # application.add_handler(stop_handler)
    application.add_handler(tip_handler)
    application.add_handler(conv_handler)
    application.run_polling()




if __name__ == '__main__':
    main()
    # d = Daemon(testfn)
    # d.start()
    # d.kill(15)
 
