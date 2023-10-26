import argparse
import logging.config
from settings import LogConfig
from chat_gpt.main_gpt import Roles, CreateResponce, ChatParser

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=2, help='Log level verbosity')
    args = parser.parse_args()

    log_level = 50 - args.verbose * 10
    logger.setLevel = log_level

    roles = {'1': Roles.ChatGPT, '2': Roles.ASSISTANT}
    print('The current roles: ')
    print(f'[1] {Roles.ChatGPT=}')
    print(f'[2] {Roles.ASSISTANT=}')

    while True:
        role = input('Choose your role: ')
        if role not in roles:
            print('Choose 1 or 2')
        else:
            break

    to_ai = CreateResponce(roles[role])
    while True:
        try:
            user_message = input('>>> ')
            if user_message in ['print dialog', 'history']:
                to_ai.print_dialog()
            else:
                to_ai.message = user_message
                to_ai.create_message()
                request = to_ai.ask()

                #TODO: need to incapsulate this logic into the Chat
                parser = ChatParser(request)
                answer = parser.message()
                to_ai.safe_dialog(answer)

                print()
                print(answer)
                print()
        except KeyboardInterrupt:
            exit()


if __name__ == '__main__':
    main()
