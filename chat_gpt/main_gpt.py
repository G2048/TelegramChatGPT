import os
import sys
import logging.config
import argparse
import openai

from settings import LogConfig, OPENAI_TOKEN
from dataclasses import dataclass


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


class Create_Responce:
    VAULT = []

    def __init__(self, role):
        openai.api_key = OPENAI_TOKEN
        self.__create_role(role)
        self.VAULT.append(self.message_role)

    def __create_role(self, role):
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
        self.VAULT.append({'role': 'user', 'content': self.question})
        logger.debug(self.VAULT)
        self.user_message = self.VAULT

    def safe_dialog(self, answer):
        if len(self.VAULT) >= 250:
            del self.VAULT[0]

        self.VAULT.append({'role': 'system', 'content': answer})

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

    def __init__(self, responce):
        self.responce = responce
        self.answer = ''

    def _finish_reason(self):
        return self.responce['choices'][0]['finish_reason']

    def _index(self):
        return self.responce['choices'][0]['index']

    def message(self):
        tokens = self.responce['choices'][0]['message']['content']
        for token in tokens:
            self.answer += token
        return self.answer

    def role(self):
        return self.responce['choices'][0]['message']['role']

    def created(self):
        return self.responce['created']

    def id(self):
        return self.responce['id']

    def _model(self):
        return self.responce['model']

    def _object(self):
        return self.responce['object']

    def _usage(self):
        return self.responce['usage']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--dry-run', action='store_true', help='???')
    parser.add_argument('-v', '--verbose', action='count', default=2, help='Log level verbosity')
    args = parser.parse_args()

    log_level = 50 - args.verbose * 10
    logging.config.dictConfig(LogConfig)
    logger = logging.getLogger('')
    logger.setLevel = log_level

    # role = Roles().ChatGPT
    role = Roles().ASSISTANT
    to_ai = Create_Responce(role)

    while True:
        try:
            user_message = input('>>> ')
            if user_message in ['print dialog', 'history']:
                to_ai.print_dialog()
            else:
                to_ai.message = user_message
                to_ai.create_message()
                request = to_ai.ask()

                parser = ChatParser(request)
                answer = parser.message()
                to_ai.safe_dialog(answer)

                print()
                print(answer)
                print()
        except KeyboardInterrupt:
            sys.exit()


if __name__ == '__main__':
    main()
