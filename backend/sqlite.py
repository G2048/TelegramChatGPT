import sqlite3

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


class Database:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.__init_sql_create_database()

    def __init_sql_create_database(self):
        self.sql_create_users_table = """CREATE TABLE IF NOT EXISTS users
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                     username TEXT,
                                     FOREIGN KEY (id) REFERENCES users_chats(user_id)
                                     )
                                  """
        self.sql_create_users_chats_table = """CREATE TABLE IF NOT EXISTS users_chats
                                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                         user_id INTEGER,
                                         chat_name TEXT,
                                         FOREIGN KEY (id) REFERENCES chats_messages(chat_id)
                                         )
                                       """
        self.sql_create_chats_messages_table = """CREATE TABLE IF NOT EXISTS chats_messages
                                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                         chat_id INTEGER,
                                         message TEXT
                                         )
                                    """
    def create(self):
        self.connection.execute(self.sql_create_users_table)
        self.connection.execute(self.sql_create_users_chats_table)
        self.connection.execute(self.sql_create_chats_messages_table)

    def __del__(self):
        self.connection.close()
