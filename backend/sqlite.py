import sqlite3
from collections import namedtuple

"""
### Layout of data storage:
    1. List of Contacts -> user_id (uniq, primary key)
    ╭───┬─────────┬─────────────────╮
    │ # │ user_id │    user_name    │
    ├───┼─────────┼─────────────────┤
    │ 0 │      11 │ Niki@telegram   │
    │ 1 │      42 │ FixBot@telegram │
    ╰───┴─────────┴─────────────────╯
    INSERT, DELETE

    2. List of Chats: user_id(forein key) -> chat_id (uniq, primary key) (Preview is the first message)
    ╭───┬─────────┬─────────┬──────────────────────────────╮
    │ # │      id │ user_id │          chat_name           │
    ├───┼─────────┼─────────┼──────────────────────────────┤
    │ 0 │       1 │      11 │ Tell me about...             │
    │ 1 │       2 │      42 │ How create the machine of... │
    ╰───┴─────────┴─────────┴──────────────────────────────╯
    Only INSERT and DELETE

    3. Chat_id(forein key) -> message_id(forein key) and number order of message_id for every chat_id
    ╭───┬─────────┬────────────┬───────────────────────╮
    │ # │ chat_id │         id │        message        │
    ├───┼─────────┼────────────│───────────────────────┤
    │ 0 │     983 │         23 │ {'start': 'message1'} │
    │ 1 │    1532 │         24 │ {'start': 'message1'} │
    │ 2 │    1532 │         25 │ {'start': 'message1'} │
    │ 3 │     983 │         26 │                       │
    ╰───┴─────────┴────────────┴───────────────────────╯
    Order equal Time ?
    4. Message_id(uniq, primary key) -> Json with conversation
    INSERT, DELETE, UPDATE
"""


def namedtuple_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    cls = namedtuple("Row", fields)
    return cls._make(row)


class SqliteDatabase:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.connection.row_factory = namedtuple_factory
        self.cursor = self.connection.cursor()
        self.close = self.connection.close
        self.commit = self.connection.commit

    def __init_sql_create_database(self):
        self.sql_create_users_table = """CREATE TABLE IF NOT EXISTS users
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                     name TEXT,
                                     description TEXT,
                                     FOREIGN KEY (id) REFERENCES chats(user_id)
                                     );
                                  """
        self.sql_create_users_chats_table = """CREATE TABLE IF NOT EXISTS chats
                                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                         user_id INTEGER,
                                         name TEXT,
                                         FOREIGN KEY (id) REFERENCES messages(chat_id)
                                         );
                                       """
        self.sql_create_chats_messages_table = """CREATE TABLE IF NOT EXISTS messages
                                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                         chat_id INTEGER,
                                         content TEXT,
                                         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                         );
                                    """
        self.sql_create_index_chat_id = """CREATE INDEX IF NOT EXISTS idx_chat_id ON messages(chat_id);"""

    def create(self):
        self.__init_sql_create_database()
        self.execute(self.sql_create_users_table)
        self.execute(self.sql_create_users_chats_table)
        self.execute(self.sql_create_chats_messages_table)
        self.execute(self.sql_create_index_chat_id)

    def execute(self, sql, *args):
        self.cursor.execute(sql, args)
        self.connection.commit()

    def select(self, sql, *args):
        self.cursor.execute(sql, args)
        return self.cursor.fetchall()

    def add_user(self, user):
        self.execute('INSERT INTO users(name) VALUES (?)', (user,))

    def __del__(self):
        self.connection.close()
