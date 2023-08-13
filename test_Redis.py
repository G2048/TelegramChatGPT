import redis
import logging.config
from settings import LogConfig 
from backend import RedisBackend
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


test()
