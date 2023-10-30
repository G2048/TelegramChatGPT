from abc import abstractmethod


class Repository:
    def __init__(self, database):
        self.database = database

    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def last_by_id(self):
        pass

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def list_id(self):
        pass

    @abstractmethod
    def get_id(self):
        pass

    def __call__(self, *args, **kwargs):
        return (row['id'] for row in self.list_id())

    __contains__ = __call__


class UserRepository(Repository):

    def add(self, user, description):
        self.database.execute('INSERT INTO users(name, description) VALUES(?, ?);', user, description)
        return self.get_id(user)

    def last_by_id(self, *args):
        user = self.database.select('SELECT * FROM users ORDER BY id DESC LIMIT 1;')
        return user[0] if user else None

    def get_id(self, user):
        user = self.database.select('SELECT id FROM users WHERE name = ?;', user)[0]
        return user['id'] if user else None

    def list(self):
        return self.database.select('SELECT * FROM users;')

    def list_id(self):
        return self.database.select('SELECT id FROM users;')


class ChatRepository(Repository):

    def add(self, user_id, chat_name):
        self.database.execute('INSERT INTO chats(user_id, name) VALUES (?, ?);', user_id, chat_name)
        return self.last_by_id(user_id)['id']

    def last_by_id(self, user_id):
        chats = self.database.select('SELECT * FROM chats WHERE user_id = ? ORDER BY id DESC LIMIT 1;', user_id)
        return chats[0] if chats else None

    def get_id(self, user_id):
        chat_id = self.database.select('SELECT id FROM chats WHERE user_id = ? ;', user_id)[0]
        return chat_id['id'] if chat_id else None

    def list(self, user_id):
        return self.database.select('SELECT * FROM chats WHERE user_id = ? ORDER BY id;', user_id)

    def list_id(self):
        return self.database.select('SELECT id FROM chats ORDER BY id;')


class DialogRepository(Repository):

    def add(self, chat_id, message):
        self.database.execute('INSERT INTO messages(chat_id, content) VALUES (?, ?);', chat_id, message)
        return self.get_id(chat_id)

    def last_by_id(self, chat_id):
        message = self.database.select('SELECT * FROM messages WHERE chat_id = ? ORDER BY id DESC LIMIT 1;', chat_id)
        return message[0] if message else None

    def get_id(self, dialog_id):
        dialog_id = self.database.select('SELECT id FROM messages WHERE chat_id = ? ;', dialog_id)[0]
        return dialog_id['id'] if dialog_id else None

    def list(self, chat_id):
        return self.database.select('SELECT * FROM messages WHERE chat_id = ? ORDER BY id;', chat_id)

    def list_id(self):
        return self.database.select('SELECT id FROM messages ORDER BY id;')