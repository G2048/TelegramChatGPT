import sys
import logging.config
import openai

from dataclasses import dataclass
from  backend.repository import ListMessageRepository
from settings import LogConfig, OPENAI_TOKEN


logging.config.dictConfig(LogConfig)
logger = logging.getLogger('')


def test_ai():
    openai.api_key = OPENAI_TOKEN
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


class CreateResponce:

    def __init__(self, role):
        self.VAULT = ListMessageRepository()
        openai.api_key = OPENAI_TOKEN
        self.create_role(role)
        self.user_message = None
        self.question = None
        self.VAULT.add(self.message_role)

    def create_role(self, role):
        self.message_role = {'role': 'system', 'content': role}

    @property
    def message(self):
        if self.message is not None:
            # self.user_message = [self.message_role, {'role': 'user', 'content': self.question}]
            # return self.user_message
            return self.message
        else:
            return 'Hello World!'

    @message.setter
    def message(self, question):
        self.question = question

    def create_message(self):
        self.VAULT.add({'role': 'user', 'content': self.question})
        logger.debug(self.VAULT)
        self.user_message = list(self.VAULT)

    def safe_dialog(self, answer):
        if len(self.VAULT) >= 250:
            del self.VAULT[0]

        self.VAULT.add({'role': 'system', 'content': answer})

    def ask(self):
        try:
            answer = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=self.user_message, temperature=0)
            logger.debug(answer)
            return answer
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
