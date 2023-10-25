import json
import logging
import logging.config
import redis

from typing import Union
from abc import ABCMeta, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass, make_dataclass
from settings import LogConfig
from redis.commands.json.path import Path
# import redis.commands.search.aggregation as aggregations
# import redis.commands.search.reducers as reducers
# from redis.commands.search.field import TextField, NumericField, TagField
# from redis.commands.search.indexDefinition import IndexDefinition, IndexType
# from redis.commands.search.query import NumericFilter, Query


logging.config.dictConfig(LogConfig)
logger = logging.getLogger('consolemode')


json = Dict[str, str]


"""
### Layout of data storage:
    1. List of Contacts -> user_id (uniq, primary key)
    ╭───┬─────────┬─────────────────╮
    │ # │ user_id │    user_name    │
    ├───┼─────────┼─────────────────┤
    │ 0 │       1 │ Niki@telegram   │
    │ 1 │       2 │ FixBot@telegram │
    ╰───┴─────────┴─────────────────╯
    INSERT, DELETE

    2. List of Chats: user_id(forein key) -> chat_id (uniq, primary key) (Preview is the first message)
    ╭───┬─────────┬─────────┬──────────────────────────────╮
    │ # │ user_id │ chat_id │          chat_name           │
    ├───┼─────────┼─────────┼──────────────────────────────┤
    │ 0 │       1 │     983 │ Tell me about...             │
    │ 1 │       2 │    1532 │ How create the machine of... │
    ╰───┴─────────┴─────────┴──────────────────────────────╯
    Only INSERT and DELETE

    3. Chat_id(forein key) -> message_id(forein key) and number order of message_id for every chat_id
    ╭───┬─────────┬────────────┬───────╮
    │ # │ chat_id │ message_id │ order │
    ├───┼─────────┼────────────┼───────┤
    │ 0 │     983 │         23 │     0 │
    │ 1 │    1532 │         24 │     0 │
    │ 2 │    1532 │         25 │     1 │
    │ 3 │     983 │         26 │     1 │
    ╰───┴─────────┴────────────┴───────╯
    Order equal Time ?

    4. Message_id(uniq, primary key) -> Json with conversation
    ╭───┬────────────┬───────────────────────╮
    │ # │ message_id │        message        │
    ├───┼────────────┼───────────────────────┤
    │ 0 │         23 │ {'start': 'message1'} │
    │ 1 │         24 │ {'start': 'message1'} │
    ╰───┴────────────┴───────────────────────╯
    INSERT, DELETE, UPDATE

### Must will release:
    1. Create a new user if don't exists
    2. Create Chat
    3. Choose chat
    4. Update the current chat
    5. Save chat
    6. Delete chat (Only by owner)
"""

class IBackend(metaclass=ABCMeta):

    @abstractmethod
    def get_data(self,):
        pass

    @abstractmethod
    def set_data(self,):
        pass

    @abstractmethod
    def get_json(self,):
        pass

    @abstractmethod
    def set_json(self,):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def execute(self, sql): 
        pass

    @abstractmethod
    def fetch(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def close_connection(self):
        pass

    @abstractmethod
    def flush_db(self):
        pass


class RedisBackend:

    def __init__(self,):
        self.client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.json = self.client.json()

    def __name__(self):
        return 'Redis'

    def increment(self, key_incr: str) -> Union[str, int]:
        _id = self.client.incrby(key_incr, 1)
        return _id

    def update(self, table: str, *values, **additions):
        key, value = values
        self.client.hset(table, key, value)

    def insert(self, table: str, new_dict: dict):
        old_dict = self.select_json(table.lower())
        self.json.set(table, Path.root_path(), old_dict.update(new_dict))

    def select(self, table: str, _id: Union[str, int]) -> Union[str, int]:
        data_type = self.client.type(table).decode('utf-8')

        if data_type == 'ReJSON-RL':
            return self.select_json(table)
        elif data_type == 'hash':
            return self.client.hget(table, _id)
        else:
            return NotImplemented

    def select_json(self, table: str) -> json:
        return self.json.get(table.lower())

    def update_json(self, table: str, json_data: Union[dict, json]):
        self.json.set(table.lower(), Path.root_path(), json_data)

    insert_json = update_json



    def set_data(self, key: str, value: str):
        self.client.set(key, value)

    def get_data(self, key: str) -> str:
        return self.client.get(key)

    def set_hashdata(self, key: str, set_map: dict):
        self.client.hset(key, mapping=set_map)

    def get_hashdata(self, client_id: str, key: str) -> str:
        return self.client.hget(client_id, key)

    def get_hashalldata(self, client_id: str) -> dict:
        return self.client.hgetall(client_id)

    def get_json(self, key: str) -> dict:
        return self.json.get(key.lower())

    def set_json(self, key: str, json_data: dict):
        if isinstance(json_data, type(dict)) and key is not None:
            key = key.lower()
            logger.debug(f'Key: "{key}" Path: {Path.root_path()} Data: {json_data}')

            self.json.set(key, Path.root_path(), json_data)
        else:
            raise ValueError('It is not json type!')

    def flush_db(self):
        self.client.flushall()


# Unused
class CreateUser:
    __backends = ['Redis', 'Postgresql']
    # getbackend = None

    def __new__(cls, ):
        cls.__backends = None
        instance = super().__new__(cls)
        return instance

    def __init__(self, user, user_id, user_name):
        db = RedisBackend()
        db.set_data(user, user_id)
        db.set_data(user, user_name)


# Must move to another file
class HandleData:
    """ 1. The fields of user - the hash type:
            1) id -> value id
            2) name -> value name
            3) chat_1 -> chat_id_1
            4) chat_2 -> chat_id_2

        2. chat_id_number -> json:
            1. Key is title of chat
            2. Value is a list of conversation (dicts within list)
    """

    def __init__(self, Backend):
        self.client = Backend()
        self.__user_id = None

    @property
    def user_id(self):
        """This is the greatest key for accesing to another fields"""

        if self.__user_id is None:
            raise ValueError('user_id don\'t be have the "None" value!')
        return self.__user_id

    @user_id.setter
    def user_id(self, value_id):
        self.__user_id = value_id

    def user_name(self):
        self.client.set_hashdata(self.__user_id)

    @property
    def chat_id(self,):
        return self.client.get_data(self.user_id)

    @chat_id.setter
    def chat_id(self, value_id):
        self.client.set_data(self.__user_id, value_id)

    @property
    def conversation(self):
        return self.client.get_hashdata(self.chat_id)

    @conversation.setter
    def conversation(self, dialogue):
        self.client.set_hashdata(self.chat_id, dialogue)

    @property
    def json_conversation(self):
        if self.chat_id is not None:
            logger.debug(f'Chat id: {self.chat_id}')
            return self.client.get_json(self.chat_id)

    @json_conversation.setter
    def json_conversation(self, payload: dict) -> None:
        logger.debug(f'Chat id: {self.chat_id} Payload: {payload}')
        self.client.set_json(self.chat_id, payload)



h = HandleData(Backend=RedisBackend)
h.user_id = 12
logger.info(f'Get user id: {h.user_id}')

# h.chat_id = 'Start_conversation'
# logger.info(f'Get Chat id: {h.chat_id}')

# h.conversation = {'client': 'Vasay' , 'client2' : 'Oleg'}
# logger.info(f'Get Conversation: {h.conversation}')
#

# h.json_conversation = user3
# h.json_conversation = {'chat_123' : [{'client': 'Vasay' , 'client2' : 'Oleg'},  {'client3': 'Robot' , 'client4' : 'Ui'}] }
# h.json_conversation['chat_123'].append({'new_client': 'new_conv'})
# logger.info("New conversation is: %s" % h.json_conversation['user'])

