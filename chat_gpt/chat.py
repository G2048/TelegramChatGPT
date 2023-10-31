import sys
import logging.config
import openai

from dataclasses import dataclass
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
        self.answer = responce['choices'][0]['message']['content']
        self._finish_reason = responce['choices'][0]['finish_reason']
        self._index = responce['choices'][0]['index']
        self.role = responce['choices'][0]['message']['role']
        self.created = responce['created']
        self.id = responce['id']
        self.model = responce['model']
        self.object = responce['object']
        self.usage = responce['usage']


class ChatGPT:

    def __init__(self, temperature=0):
        self.VAULT = []
        self._user_message = {}
        self._answer = {}
        self.temperature = temperature

    # It's the start message
    def new_dialog(self, role: Roles, model: Models = Models.GPT_turbo):
        # Role is start message
        self.model = model
        self.answer = role

    def fill_messages(self, messages: list):
        self.VAULT.extend(messages)

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, answer):
        self._answer = {'role': 'system', 'content': answer}
        self.save(self._answer)

    def ask_question(self, question):
        self.message = question
        return self.ask()

    def list_dialogs(self) -> tuple:
        for dialog in self.VAULT:
            yield (dialog['role'], dialog['content'])

    @property
    def message(self):
        return self._user_message

    @message.setter
    def message(self, question):
        self._user_message = {'role': 'user', 'content': question}
        self.save(self._user_message)

    def save(self, message):
        logger.debug(self.VAULT)
        if len(self.VAULT) >= 250:
            del self.VAULT[0]
        self.VAULT.append(message)

    def __create_message(self, role, message):
        self.save({'role': role, 'content': message})

    def ask(self):
        try:
            answer = openai.ChatCompletion.create(model=self.model, messages=self.VAULT,
                                                  temperature=self.temperature
                                                  )
            logger.debug(answer)
            self._parser = ChatParser(answer)
            self.answer = self._parser.answer
            # self.__create_message(self._parser.role, self._parser.answer)
            return self._parser.answer
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
