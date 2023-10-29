from abc import abstractmethod


class Repository:
    def __init__(self, database):
        self.database = database

    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def last(self):
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
        return (row.id for row in self.list_id())

    __contains__ = __call__


class UserRepository(Repository):

    def add(self, user, description):
        self.database.execute('INSERT INTO users(name, description) VALUES(?, ?);', user, description)
        return self.get_id(user)

    def last(self):
        user = self.database.select('SELECT * FROM users ORDER BY id DESC LIMIT 1;')
        return user[0] if user else None

    def get_id(self, user):
        user = self.database.select('SELECT id FROM users WHERE name = ?;', user)[0]
        return user.id if user else None

    def list(self):
        return self.database.select('SELECT * FROM users;')

    def list_id(self):
        return self.database.select('SELECT id FROM users;')


class ChatRepository(Repository):

    def add(self, user_id, chat_name):
        self.database.execute(f'INSERT INTO chats(user_id, name) VALUES (?, ?);', user_id, chat_name)
        return self.get_id(user_id)

    def last(self):
        return self.database.select(f'SELECT * FROM chats ORDER BY id DESC LIMIT 1;')[0]

    def get_id(self, user_id):
        chat_id = self.database.select(f'SELECT id FROM chats WHERE user_id = ? ;', user_id)[0]
        return chat_id.id if chat_id else None

    def list(self):
        return self.database.select(f'SELECT * FROM chats ORDER BY id;')

    def list_id(self):
        return self.database.select(f'SELECT id FROM chats ORDER BY id;')


class DialogRepository(Repository):

    def add(self, chat_id, message):
        self.database.execute('INSERT INTO messages(chat_id, content) VALUES (?, ?);', chat_id, message)
        return self.get_id(chat_id)

    def last(self):
        return self.database.select(f'SELECT * FROM messages ORDER BY id DESC LIMIT 1;')[0]

    def get_id(self, dialog_id):
        dialog_id = self.database.select(f'SELECT id FROM messages WHERE chat_id = ? ;', dialog_id)[0]
        return dialog_id.id if dialog_id else None

    def list(self):
        return self.database.select(f'SELECT * FROM messages ORDER BY id;')

    def list_id(self):
        return self.database.select(f'SELECT id FROM messages ORDER BY id;')
