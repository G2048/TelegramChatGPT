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
    MenuButtonCommands
)
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler
)
# import Daemon from demon


load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')


help_log = 'without the -l option write to telegram.log otherwise print to file'
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--dry-run', action='store_true')
parser.add_argument('-l', '--log', action='store', default='telegram.log', const='', nargs='?', help=help_log)
parser.add_argument('-tl', '--time-live', action='store', default=None, help='Time to live the process')
args = parser.parse_args()


FORMAT = '%(asctime)s::%(levelname)s::%(message)s'
logging.basicConfig(filename=args.log, format=FORMAT, level=logging.DEBUG)



async def echofn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # message = update.message.reply_text # For straight forward message
    message = f'{update.message.from_user.first_name} say: {update.message.text}'
    logging.info(f'{update.message}')
    logging.info(f'{message}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='MarkdownV2')

    # For straight forward message
    # await context.bot.forward_message(chat_id=update.effective_chat.id, from_chat_id=update.effective_chat.id, 
                                      # message_id=update.message.message_id)


async def startfn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    subkeyboard = [InlineKeyboardButton('subbutton 1', callback_data='Yes!')]
    keyboard = [
        [
            InlineKeyboardButton("button 1", callback_data='pushed'),
            InlineKeyboardButton("button 2", callback_data="pushed button 2!"),
        ],
        # [ InlineKeyboardMarkup('button', subkeyboard) ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose:', reply_markup=reply_markup)


async def buttonfn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f'Select option: {query.data}')




def main_chat() -> None:
    role = Roles().ChatGPT
    ask_to_ai = Create_Responce(role)
    ask_to_ai.message = 'What is the imaginary numbers?'
    ask_to_ai.create_message()
    answer = ask_to_ai.ask()

    application = ApplicationBuilder().token(TOKEN).build()
    start_handler = CommandHandler('start', startfn)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echofn)


    application.add_handler(start_handler)
    # application.add_handler(echo_handler)
    application.run_polling()




def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()
    start_handler = CommandHandler('start', startfn)
    # start_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echofn)
    button_handler = CallbackQueryHandler(buttonfn)

    application.add_handler(start_handler)
    application.add_handler(button_handler)
    application.run_polling()




if __name__ == '__main__':
    main()
    # d = Daemon(testfn)
    # d.start()
    # d.kill(15)
 
