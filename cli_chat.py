import logging.config

from dataclasses import dataclass
from backend import sqlite
from settings import LogConfig
from chat_gpt.chat import ChatGPT, Roles
from backend.repository import UserRepository, ChatRepository, DialogRepository

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('consolemode')
logger.setLevel(10)


@dataclass
class KindDB:
    memory = ':memory:'
    test = 'testdb.db'


# Test data
user_data = dict(username='@Nikitelegram', first_name='IX', telegram_id=5432, description='admin')

chatgpt = ChatGPT()
database = sqlite.SqliteDatabase(KindDB.test).create()
user = UserRepository(database)
chat = ChatRepository(database)
dialog = DialogRepository(database)


def conversation():
    answer = ''
    message = input('>>> ')
    if message == 'exit':
        exit()
    if message in ['print dialog', 'history']:
        for role, content in chatgpt.list_dialogs():
            print(f'{role}: {content}')
    else:
        answer = chatgpt.ask_question(message)
    print()
    print(answer)
    print()
    return message, answer


# Start here
user_id = user.get_id(user_data['telegram_id'])
if user_id is None:
    user_id = user.add(**user_data)

all_chats = chat.list_by_user_id(user_id)

# Start a new conversation for creating a new chat
role = 'system'
if all_chats is None:
    chatgpt.new_dialog(Roles.chatgpt)
    print('Start conversation:')
    question, answer = conversation()
    chat_name = answer[:20]
    chat_id = chat.add(user_id, chat_name)
    dialog.add(chat_id, question)
    dialog.add(chat_id, answer, role)
# Else choose the chat
else:
    for chat_num, data_chat in enumerate(all_chats):
        chat_num += 1
        user_data.update({chat_num: data_chat['id']})
        print(f'{chat_num}. Current chats: {data_chat["name"]}')

    print('Choose the chat number!')
    chat_num = input('>>> ')
    chat_id = user_data[int(chat_num)]
    last_conversation = dialog.list_by_chat_id(chat_id)
    last_message = dialog.last_by_id(chat_id)['content']
    # Print all conversation
    for last in last_conversation:
        print(f'{last["role"]}: {last["content"]}')
        chatgpt.create_message(last['role'], last['content'])

user_data.update({'chat_id': chat_id})
while True:
    try:
        question, answer = conversation()
        dialog.add(user_data['chat_id'], question)
        dialog.add(user_data['chat_id'], answer, role)
    except KeyboardInterrupt:
        exit()
