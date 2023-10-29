from chat_gpt.main_gpt import *

from telegram import (
    Update, InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
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



END = ConversationHandler.END
CHAT ='1'
START ='2'
CHOOSE ='3'
MIDDLE ='4'
MENU ='5'
GREETINGS = """Hello! I am an AI language model designed to assist and communicate with users. I am programmed to understand and respond to natural language queries and provide helpful responses. My purpose is to make tasks easier and more efficient for users."""


role = Roles().ASSISTANT
ask_to_ai = CreateResponce(role)
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
    keyboard = [['STOP'], ['Change the Dialoge'], ['Save the conversation']]

    keyboard_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)
    await update.message.delete()
    await update.message.reply_text(
        'Conversation keyboard',
        reply_markup=keyboard_markup
    )


async def start_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """It's start menu for choise of dialogue and starting of conversation"""
    keyboard = [['START'], ['Get the list of Dialogues']]

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
    logging.info(f'Midlle: {message}')

    if message == 'START':
        keyboard = [['STOP'], ['Change the Dialogue']]

        # Get the keyboard along to conversation
        keyboard_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)
        await update.message.reply_text('Start conversation with ChatGPT!', reply_markup=keyboard_markup)

        await update.message.reply_text(GREETINGS)
        return CHAT

    if message in ['Get the list of Dialogues', 'Change the Dialogue']:
        # Here will be placed a keyboard
        logging.info('Get choose of dialogue')
        return MENU


COUNT = 0

# Must need to make pagination
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """It's the first keyboard in order to accept the first message from the Reply keboard"""
    # message = update.message.text
    # logging.info(f'Message inside MENU: {message}')

    # Forward and bacward buttons must be dynamic!
    next_button = InlineKeyboardButton('Next   →', callback_data='next_page')
    back_button = InlineKeyboardButton('← Backward', callback_data='back_page')
    choose_button = InlineKeyboardButton('Choose', callback_data='choose')
    hide_button = InlineKeyboardButton('Hide', callback_data='hide')

    keyboard = [[hide_button, choose_button], [back_button, next_button]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text='Get data From DataBase', reply_markup=reply_markup)
    return CHOOSE


async def selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """It's the Pagination-keyboard for user interaction"""

    # Forward and bacward buttons must be dynamic!
    next_button = InlineKeyboardButton('Next   →', callback_data='next_page')
    back_button = InlineKeyboardButton('← Backward', callback_data='back_page')
    count_button = InlineKeyboardButton(f'{COUNT}/1000', callback_data='_')

    choose_button = InlineKeyboardButton('Confirm', callback_data='choose')
    hide_button = InlineKeyboardButton('Hide', callback_data='hide')
    keyboard = [[hide_button], [back_button, count_button, next_button], [choose_button]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text='Get data From DataBase', reply_markup=reply_markup)
    return CHOOSE

# Pagination...
async def incr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global COUNT
    COUNT += 1
    logging.info(f'Count is {COUNT}')
    return await selection(update, context)

async def decr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global COUNT
    COUNT -= 1
    logging.info(f'Count is {COUNT}')
    return await selection(update, context)

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global COUNT
    await update.callback_query.edit_message_text(f'Choose is {COUNT}')
    return END



def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    tip_handler = CommandHandler('help', tip)
    start_handler = CommandHandler('start', start_keyboard)
    middle_handler = MessageHandler(~(filters.COMMAND | filters.Regex('^(STOP|forward)$')), middle) #conversation_keyboard)
    menu_handler = MessageHandler(filters.Regex('^(Get the list of Dialogues|Change the Dialogue)$') & ~(filters.COMMAND | filters.Regex('^STOP$')), menu)
    stop_handler = CommandHandler('stop', stop)
    # forward_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), proxy_message)
    forward_handler = MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex('^STOP$') | filters.Regex('^Change the Dialogue$')), echo)
    stop_handler = MessageHandler(filters.Regex('^STOP$'), stop)


    selection_handler = ConversationHandler(
        entry_points=[menu_handler],
        states = {
        CHOOSE: [
                CallbackQueryHandler(incr, pattern='next_page'),
                CallbackQueryHandler(decr, pattern='back_page'),
                CallbackQueryHandler(decr, pattern='^hide$'),
                ]

        },
        fallbacks = [CallbackQueryHandler(choose, pattern='^choose$'),],
        map_to_parent={END: MIDDLE}
    )

    conv_handler = ConversationHandler(
        entry_points=[start_handler,],
        states = {

            MIDDLE: [
                middle_handler,
            ],

            CHAT: [forward_handler, middle_handler,],
            MENU: [selection_handler],
        },

        fallbacks=[stop_handler, ],
    )

    logging.info(f'Current state: {START} and {CHAT}')

    # application.add_handler(stop_handler)
    application.add_handler(tip_handler)
    # application.add_handler(selection_handler)
    application.add_handler(conv_handler)
    application.run_polling()




if __name__ == '__main__':
    main()
    # d = Daemon(testfn)
    # d.start()
    # d.kill(15)
 
