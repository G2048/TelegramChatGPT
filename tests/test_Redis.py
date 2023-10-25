import redis
import logging.config
from datetime import datetime
from settings import LogConfig 
from backend.backend import RedisBackend
from redis.commands.json.path import Path

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('consolemode')


user_information = {
            "name": "Paul Zamir",
            "email": "paul.zamir@example.com",
            "age": 35,
            "city": "Tel Aviv"
}

user3 = {
        "user": [user_information]
}


def test():
    r = RedisBackend()
    conv = {'client': 'Vasay' , 'client2' : 'Oleg'}

    user_id = 12
    chat_id = 'Start conversation'
    # upload
    r.set_data(user_id, chat_id)
    # download
    chat_id = r.get_data(user_id)
    logger.info(chat_id)

    # upload
    r.set_hashdata(chat_id, conv)
    # download
    logger.info(r.get_hashdata(chat_id))


def test2():
    user_information = {
            "name": "Paul Zamir",
            "email": "paul.zamir@example.com",
            "age": 35,
            "city": "Tel Aviv"
    }

    user3 = {
        "user": [user_information]
    }

    r = redis.Redis(host='localhost', port=6379)
    r.json().set('user:3', Path.root_path(), user3)
    logger.info(r.json().get('user:3'))


def test3():

    # First table
    table_1 = 'Users'
    user_id = '12'
    user_name = 'FixBot@telegram'

    # Second Table
    table_2 = 'Chats'
    chat_id = '532'
    chat_name = 'Tell me about..'

    # Third table
    table_3 = 'Events'
    order = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

    # Fourth Table
    table_4 = 'Messages'
    message_id = '0'
    message = {'role': 'system', 'content': 'You are a helpful assistant.'}

    r = redis.Redis(host='localhost', port=6379)

    # Fill data
    r.hset(table_1, user_id, user_name)
    r.hset(table_2, chat_id, chat_name)
    r.hset(table_3, chat_id, message_id)
    r.hset(table_3, message_id, order)
    # r.hset(table_4, message_id, message)
    j = r.json()
    j.set(message_id, Path.root_path(), message)

    logger.debug(j.get(message_id))


def test4():

    r = redis.Redis(host='localhost', port=6379)

    # First table
    table_1 = 'Users'
    user_key_incr = 'user_incr'
    user_id = r.incrby(user_key_incr, 1)
    user_name = 'FixBot@telegram'

    # Second Table
    table_2 = 'Chats'
    chat_key_incr = 'chat_incr'
    chat_id = r.incrby(chat_key_incr, 1)
    table_2_1 = 'Chats_Names'
    chat_name = 'Tell me about..'

    # Third table
    table_3 = 'Events'
    order = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    table_3_1 = 'Events_Order'

    # Fourth Table
    table_4 = 'Messages'
    message_key_incr = 'message_incr'
    message_id = r.incrby(message_key_incr, 1)
    message = {'role': 'system', 'content': 'You are a helpful assistant.'}


    j = r.json()
    # Fill data
    r.hset(table_1, user_id, user_name)
    j.set(table_2, Path.root_path(), {user_id: [chat_id]})
    r.hset(table_2_1, chat_id, chat_name)

    # Split chat_id and message_id to anothers tables
    # becouse Redis is simple key-value storage
    # r.hset(table_3, chat_id, message_id)
    # r.hset(table_4, message_id, order)


    j.set(table_3, Path.root_path(), {chat_id: [message_id]})
    r.hset(table_3_1, message_id, order)

    logger.debug(f'{message_id=} {message=}')
    j.set(table_4, Path.root_path(), {message_id: message})


    # Get message_id and relating messages
    logger.debug(j.get('Messages'))

    logger.debug(j.get(table_4)) # -> Get message
    logger.debug(r.hget(table_3_1, message_id)) # -> Get Order(TimeStamp) of message
    logger.debug(j.get(table_3)) # -> Get list of chat messages
    logger.debug(r.hget(table_2_1, chat_id)) # -> Get ChatName
    logger.debug(j.get(table_2)) # -> Get list of user chats
    logger.debug(r.hget(table_1, user_id)) # -> Get UserName
    logger.debug(r.type(table_1))
    logger.debug(r.type(table_2))
    logger.debug(r.type(table_3))
    # r.flushall()


if __name__ == '__main__':
    test4()
