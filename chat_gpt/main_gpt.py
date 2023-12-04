import sys
import logging.config
import openai

from dataclasses import dataclass
from backend.repository import ListMessageRepository
from settings import LogConfig, OPENAI_TOKEN

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('')

openai.api_key = OPENAI_TOKEN


def test_ai():
    messages = [
        # {'role': 'system', 'content': 'You are a chatbot'},
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'What is the imaginary numbers?'},
    ]
    try:
        answer = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=messages)
        logger.debug(answer)
        return answer
    except Exception as e:
        logger.error(str(e)[:100])
        sys.exit(1)


@dataclass(frozen=True)
class Roles:
    """Role must started with 'You are ...' """
    ChatGPT: str = 'You are a chatbot'
    ASSISTANT: str = 'You are a helpful assistant.'


@dataclass(frozen=True)
class Models:
    """Avalible models open AI"""
    GPT_turbo: str = 'gpt-3.5-turbo'


class ChatParser:
    """The main input is the messages parameter.
        Messages must be an array of message objects,
            where each object has a role (either "system", "user", or "assistant")
            and content (the content of the message).
        Conversations can be as short as 1 message or fill many pages.

    Example:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
    """

    __instance = None

    def __new__(cls, response):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, responce):
        self.responce = responce
        self.answer = ''
        self._finish_reason = responce['choices'][0]['finish_reason']
        self._index = responce['choices'][0]['index']
        self.role = responce['choices'][0]['message']['role']
        self.created = responce['created']
        self.id = responce['id']
        self.model = responce['model']
        self.object = responce['object']
        self.usage = responce['usage']

    @property
    def message(self):
        tokens = self.responce['choices'][0]['message']['content']
        for token in tokens:
            self.answer += token
        return self.answer


# TODO: Need to use the Chain of Responsibility pattern
class User:
    def __init__(self, user_id):
        self.database = RedisBackend()
        if not in self.database.users(user_id):
            user_id = self.database.users.create(user_id)
        self.user_id = user_id

    def list_chats(self) -> list:
        return self.database.chats(self.user_id)


""" The schema of conversation:

>>> database = RedisBackend()
>>> user = User(user_id)
>>> user.list_chats() # print chats id
>>> chat_id = user.last_chat()
>>> 
>>> chat = Chat(chat_id)
>>> chat.list_messages()
>>> message_id = chat.last_message()
>>>
>>> message = Message(last_message_id=message_id)
>>> application = Application()
>>>
>>> # while True:
>>> answer = application.ask_question()
>>> print(answer)
>>> message.save(answer, message.id)
>>> message.id
>>> message.content
>>> message.text
"""

class Database:
    def __init__(self, database):
        self.users = UserRepository(database)
        self.chats = ChatRepository(database)
        self.dialogs = DialogRepository(database)



class ChatRepository:
    def __init__(self, database):
        self.database = database

    def create(self, chat_id):
        self.database.connection.execute(f'INSERT INTO {self.database.users(chat_id)}')
        return chat_id
    def list_chats(self):
        return self.database.connection.execute(f'SELECT * FROM {self.database.users}')
    def __call__(self, *args, **kwargs):
        return self.list_chats()
    __contains__ = __call__

class Chat:
    def __init__(self, chat_id):
        if chat_id not in self.database.chats():
            chat_id = self.database.chats.create(chat_id)
        self.chat_id = chat_id

    def new_dialog(self, role: Roles):
        star_message = self.__create_role(role)

    def __create_role(self, role):
        self.message_role = {'role': 'system', 'content': role}

    def list_dialogs() -> list:
        pass


class Dialog:
    def __init__(self, dialog_id):
        if not in self.database.dialogs(dialog_id):
            dialog_id = self.database.dialogs.create(dialog_id)
        self.dialog_id = dialog_id

    def ask_question(self):
        pass

    def message(self):
        pass

    def print_dialog(self):
        pass


class CreateResponce:

    def __init__(self, role):
        self.VAULT = ListMessageRepository()
        self._user_message = {'role': 'user', 'content': 'Hello!'}
        self.question = None
        # It's the start message
        self.create_role(role)
        self.VAULT.add(self.message_role)

    def create_role(self, role):
        self.message_role = {'role': 'system', 'content': role}

    @property
    def message(self):
        return self._user_message

    @message.setter
    def message(self, question):
        self._create_message(question)

    def _create_message(self, question):
        self._user_message = {'role': 'user', 'content': question}
        self.save(self._user_message)

    def save(self, message):
        logger.debug(self.VAULT)
        if len(self.VAULT) >= 250:
            del self.VAULT[0]
        self.VAULT.add(message)

    def ask(self):
        try:
            answer = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=list(self.VAULT), temperature=0)
            logger.debug(answer)
            parser = ChatParser(answer)
            self.answer = parser.message
            self.save({'role': 'system', 'content': self.answer})
            return self.answer
        except Exception as e:
            logger.error(str(e)[:100])
            sys.exit(1)

    def print_dialog(self):
        for dialog in self.VAULT:
            if dialog['role'] == 'system':
                speaker = 'ChatGPT'
            else:
                speaker = 'You'
            print()
            print(f'{speaker}: {dialog["content"]}')
