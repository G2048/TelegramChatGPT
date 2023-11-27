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


class Printer(ABC):
    @abstractmethod
    def print_dialog(self):
        pass


class ConsolePrinter(Printer):
    def __init__(self):
        self.__res()

    @classmethod
    def __res(cls):
        cls.printer = print

    def print_dialog(self, message):
        self.printer(message)


console_printer = ConsolePrinter()
print = console_printer.print_dialog

# Test data
user_data = dict(username='@Nikitelegram', first_name='IX', telegram_id=5432, description='admin')

database = sqlite.SqliteDatabase(KindDB.test).create()


class Application:

    def __init__(self, database: sqlite.SqliteDatabase, user_data: dict):
        self.chatgpt = ChatGPT()
        self.user = UserRepository(database)
        self.chat = ChatRepository(database)
        self.dialog = DialogRepository(database)
        self.user_data = user_data
        self.SERVICE_MESSAGE = {'pint dialog': self.print_dialogs, 'history': self.print_dialogs,
                                'exit': exit, 'new': self.new_chat, 'choose': self.choose_chat
                                }
        self.conversation = self.generate_conversation()
        self.check_exist_user()
        self.check_exist_chat()
        self.chat_name = None

    def check_exist_user(self):
        self.user_id = self.user.get_id(self.user_data['telegram_id'])
        if self.user_id is None:
            self.user_id = self.user.add(**self.user_data)

    def check_exist_chat(self):
        all_chats = self.chat.list_by_user_id(self.user_id)
        # Start a new conversation for creating a new chat
        if all_chats is None:
            self.chat_id = self.new_chat(self.user_id)
        # Else choose the chat
        else:
            self.chat_id = self.choose_chat()
            self.conversation.send(None)
        self.user_data.update({'chat_id': self.chat_id})

    def print_dialogs(self, chat_id):
        last_conversation = self.dialog.list_by_chat_id(chat_id)
        # last_message = dialog.last_by_id(chat_id)['content']
        # Print all conversation
        for last in last_conversation:
            print(f'{last["role"]}: {last["content"]}')
            self.chatgpt.create_message(last['role'], last['content'])

    def generate_conversation(self):
        while True:
            message = input('>>> ')
            if message in self.SERVICE_MESSAGE:
                self.SERVICE_MESSAGE[message]()
                continue
            else:
                answer = self.chatgpt.ask_question(message)
            print('\n{}\n'.format(answer))
            chat_id = yield message, answer
            self.dialog.add(chat_id, message, 'user')
            self.dialog.add(chat_id, answer, 'system')

    def new_chat(self, user_id):
        self.conversation = self.generate_conversation()
        self.chatgpt.new_dialog(Roles.chatgpt)
        print('Start conversation:')
        question, answer = self.conversation.send(None)
        chat_name = question[:20]
        chat_id = self.chat.add(user_id, chat_name)
        self.dialog.add(chat_id, question, 'user')
        self.dialog.add(chat_id, answer, 'system')
        return chat_id

    def choose_chat(self):
        chats = self.chat.list_by_user_id(self.user_id)
        for chat_num, data_chat in enumerate(chats):
            chat_num += 1
            self.user_data.update({chat_num: data_chat['id']})
            print(f'{chat_num}. Current chat: {data_chat["name"]}')

        print('Choose the chat number!')
        chat_num = input('>>> ')
        chat_id = self.user_data[int(chat_num)]
        self.print_dialogs(chat_id)
        return chat_id

    def dialog(self):
        while True:
            try:
                self.conversation.send(self.chat_id)
            except KeyboardInterrupt:
                exit()


# Start here
def main():
    chat = Application(database, user_data)
    chat.dialog()


if __name__ == '__main__':
    main()
