import logging.config

from settings import LogConfig
from chat_gpt.chat import ChatGPT, Roles
from backend.repository import UserRepository, ChatRepository, DialogRepository

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('')

# TODO: Need to use the Chain of Responsibility pattern
# Create new User -> Create new chat -> Create new message
# if User exists -> Create new chat -> Create new message
# if User exists -> choose chat -> Create new message


""" The schema of conversation:

>>> user = User(user_id)
>>> user.list_chats() # print chats id
>>> chat_id = user.last_chat() # find chat
>>> 
>>> chat = Chat(chat_id) # choose chat
>>> chat.list_messages()
>>> message_id = chat.last_message() # find last message
>>>
>>> message = Message(last_message_id=message_id) # choose message
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


class BaseHandler:
    _next_handler = None

    def __init__(self, repository):
        self.repository = repository

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    def handle(self, *args, **kwargs):
        if self._next_handler:
            return self._next_handler.handle(*args, **kwargs)

    def new(self, entity_id, *args, **kwargs):
        entity_id = self.repository.add(entity_id, *args, **kwargs)
        logger.info(f'{type(self).__name__} with {entity_id} successfully created!')
        # return entity_id


# The Started handler
class User(BaseHandler):

    def handle(self, service_data: dict):
        # Check if user exists
        user_id = self.repository.get_id(service_data['telegram_id'])
        if not user_id:
            user_id = self.new(service_data['username'], service_data['telegram_id'])

        service_data['user_id'] = user_id
        super().handle(service_data)


# Second handler
class Chat(BaseHandler):
    chat_id = None

    # If it's the new user then user must write the first message
    def handle(self, service_data):
        if not self.repository.list_by_user_id(service_data['user_id']):
            message = input('Enter >>> ')
            chat_id = self.new(service_data['user_id'], message)
            service_data['chat_name'] = message
            service_data['chat_id'] = chat_id
        else:
            # Print all chats!
            list_chats = self.repository.list_by_user_id(service_data['user_id'])
            choose_chats = {}
            for chat in list_chats:
                name = chat['name']
                print(name)
                choose_chats[name] = chat['id']

            # Choose the Chat!
            while True:
                chat = input('Enter >>> ')
                if chat not in choose_chats:
                    print('No such chat!')
                else:
                    break

            service_data['chat_name'] = chat
            service_data['chat_id'] = choose_chats[chat]

        super().handle(service_data)

    def list(self, user_id):
        self.repository.list(user_id)


# Third handler
class Dialog(BaseHandler):

    # After this handler we are needs the condition to exit the loop
    def handle(self, service_data):
        last_message = self.repository.last_by_id(service_data['chat_id'])
        print(last_message)

        # The Conversing
        while True:
            message = input('Enter >>> ')
            if message in ('print dialog', 'history'):
                print(self.repository.list_by_chat_id(service_data['chat_id']))
            else:
                message_id = self.new(service_data['chat_id'], message)
        super().handle(service_data)


chatgpt = ChatGPT()
chatgpt.new_dialog(Roles.ChatGPT)
# start_message = chatgpt.last_answer

database = 'database.db'
user = UserRepository(database)
chat = ChatRepository(database)
dialog = DialogRepository(database)
# user.set_next(chat).set_next(dialog).set_next(chat)

# Start here
user_data = dict(username='@Nikitelegram', firstname='IX', telegram_id=5432, user_description='admin')

user_id = user.get_id(user_data['telegram_id'])
if user_id is None:
    user_id = user.add(**user_data)

all_chats = chat.list_by_user_id(user_id)

question = input('>>> ')
answer = chatgpt.ask_question(question)

# Start a new conversation for creating a new chat
if all_chats is None:
    chat_name = answer[:20]
    chat_id = chat.add(user_id, chat_name)
# Else choose the chat
else:
    # chat.handle(user_id, 'Hello!')
    for chat_num, chat in enumerate(all_chats):
        chat_num += 1
        user_data.update({chat[chat_num]: chat['id']})
        print(f'{chat_num}. Current chats: {chat["name"]=}')

    print('Choose the chat number!')
    chat_num = input('>>> ')
    chat_id = user_data[chat_num]
    last_message = dialog.last_by_id(chat_id)
    user_data.update({'current_chat': chat_id})
    print(last_message)

dialog.add(chat_id, answer)
# Old protocol
# chatgpt.message = message
# chatgpt.ask()
# chatgpt.answer

# user.handle('user', 'user_1')

while True:
    try:
        message = input('>>> ')
        message_data = dict(username='admin', user_description='Niki@telegram',
                            chat_name=message[:10], chat_id=chat_id,
                            message=message
                            )
        if message in ['print dialog', 'history']:
            chatgpt.list_dialogs()
        else:
            question = message
            answer = chatgpt.ask_question(question)
            dialog.add(user_data['chat_id'], answer)
            print()
            print(answer)
            print()
    except KeyboardInterrupt:
        exit()
