import argparse
import logging.config
from settings import LogConfig
from chat_gpt.chat import Roles, ChatGPT, Models

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=2, help='Log level verbosity')
    args = parser.parse_args()

    log_level = 50 - args.verbose * 10
    logger.setLevel = log_level

    roles = {'1': Roles.ChatGPT, '2': Roles.ASSISTANT}
    models = {'1': Models.GPT_turbo}

    print('The current chat models: ')
    print(f'[1] {Models.GPT_turbo=}')
    print()
    while True:
        model = input('Choose chat model: ')
        if model not in models:
            print('No! Only gpt-3.5!')
            model = '1'
            break
        else:
            break

    print('The current roles: ')
    print(f'[1] {Roles.ChatGPT=}')
    print(f'[2] {Roles.ASSISTANT=}')

    while True:
        role = input('Choose your role: ')
        if role not in roles:
            print('Choose 1 or 2')
        else:
            break

    to_ai = ChatGPT()
    to_ai.new_dialog(roles[role], models[model])
    while True:
        try:
            user_message = input('>>> ')
            if user_message in ['print dialog', 'history']:
                to_ai.print_dialog()
            else:
                to_ai.message = user_message
                answer = to_ai.ask()
                print()
                print(answer)
                print()
        except KeyboardInterrupt:
            exit()


if __name__ == '__main__':
    main()
