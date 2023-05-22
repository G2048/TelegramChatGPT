import asyncio
import logging
import os
import argparse

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
    ConversationHandler, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler
)


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





async def startfn(update: Update):
    button1 = InlineKeyboardButton('button 1', callback_data='button 1')
    button2 = InlineKeyboardButton('button 2', callback_data='button 2')
    button3 = InlineKeyboardButton('button 3', callback_data='button 3')
    keyboard1 = [button1, button2, button3]
    keyboard2 = [button1, button2, button3]
    keyboards = [keyboard1, keyboard2]

    reply_markup = InlineKeyboardMarkup.from_column(keyboard1)
    reply_markup = InlineKeyboardMarkup(keyboards)
    # reply_markup = InlineKeyboardMarkup.from_row(keyboard1)
    # reply_markup = InlineKeyboardMarkup.from_button(button1)
    await update.message.reply_text('Please choose:', reply_markup=reply_markup)
    await update.callback_query.edit_message_text(text='', reply_markup=reply_markup)


async def choose1(update: Update):
    button1 = InlineKeyboardButton('button 4', callback_data='button 4')
    button2 = InlineKeyboardButton('button 5', callback_data='button 5')
    button3 = InlineKeyboardButton('button 6', callback_data='button 6')
    keyboard1 = [button1, button2, button3]
    keyboards = [keyboard1,]

    reply_markup = InlineKeyboardMarkup.from_column(keyboard1)
    reply_markup = InlineKeyboardMarkup(keyboards)
    # reply_markup = InlineKeyboardMarkup.from_row(keyboard1)
    # reply_markup = InlineKeyboardMarkup.from_button(button1)
    await update.message.reply_text('Please choose:', reply_markup=reply_markup)
    await update.callback_query.edit_message_text(text='', reply_markup=reply_markup)


async def buttonfn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f'Select option: {query.data}')





def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()


    start_handler = CommandHandler('start', startfn)
    button_handler = CallbackQueryHandler(buttonfn)
    conversation_handler = ConversationHandler(entry_points=[start_handler], states={} , fallbacks=[start_handler])


    application.add_handler(conversation_handler)
    # application.add_handler(start_handler)
    # application.add_handler(button_handler)
    application.run_polling()




if __name__ == '__main__':
    main()
