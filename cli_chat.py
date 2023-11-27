from abc import ABC, abstractmethod
from dataclasses import dataclass
from backend import sqlite
from settings import LogConfig
from chat_gpt.chat import ChatGPT, Roles
from backend.repository import UserRepository, ChatRepository, DialogRepository


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


def print_dialogs():
    for role, content in chatgpt.list_dialogs():
        print(f'{role}: {content}', )


def generate_conversation():
    while True:
        message = input('>>> ')
        if message in SERVICE_MESSAGE:
            SERVICE_MESSAGE[message]()
            continue
        else:
            answer = chatgpt.ask_question(message)
        print('\n{}\n'.format(answer))
        chat_id = yield message, answer
        dialog.add(chat_id, message, 'user')
        dialog.add(chat_id, answer, 'system')


def new_chat(user_id):
    conversation = generate_conversation()
    chatgpt.new_dialog(Roles.chatgpt)
    print('Start conversation:')
    question, answer = conversation.send(None)
    chat_name = question[:20]
    chat_id = chat.add(user_id, chat_name)
    dialog.add(chat_id, question, 'user')
    dialog.add(chat_id, answer, 'system')
    return chat_id


def choose_chat(chats):
    for chat_num, data_chat in enumerate(chats):
        chat_num += 1
        user_data.update({chat_num: data_chat['id']})
        print(f'{chat_num}. Current chat: {data_chat["name"]}')

    print('Choose the chat number!')
    chat_num = input('>>> ')
    chat_id = user_data[int(chat_num)]
    last_conversation = dialog.list_by_chat_id(chat_id)
    last_message = dialog.last_by_id(chat_id)['content']
    # Print all conversation
    for last in last_conversation:
        print(f'{last["role"]}: {last["content"]}')
        chatgpt.create_message(last['role'], last['content'])
    return chat_id


SERVICE_MESSAGE = {'pint dialog': print_dialogs, 'history': print_dialogs,
                   'exit': exit, 'new': new_chat, 'choose': choose_chat
                   }


class Printer(ABC):
    @abstractmethod
    def print_dialog(self):
        pass


# class ConsolePrinter(Printer):
#     def __init__(self):
#         self.__res()
#     @classmethod
#     def __res(cls):
#         cls.printer = print
#
#     def print_dialog(self, message):
#         self.printer(message)
#
#
# console_printer = ConsolePrinter()
# print = console_printer.print_dialog


# Start here
def main():
    conversation = generate_conversation()
    user_id = user.get_id(user_data['telegram_id'])
    if user_id is None:
        user_id = user.add(**user_data)

    all_chats = chat.list_by_user_id(user_id)
    # Start a new conversation for creating a new chat
    if all_chats is None:
        chat_id = new_chat(user_id)
    # Else choose the chat
    else:
        chat_id = choose_chat(all_chats)
        conversation.send(None)

    user_data.update({'chat_id': chat_id})
    while True:
        try:
            conversation.send(chat_id)
        except KeyboardInterrupt:
            exit()


if __name__ == '__main__':
    main()
