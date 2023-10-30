import unittest
from backend.sqlite import SqliteDatabase
from backend.repository import UserRepository, ChatRepository, DialogRepository


class TestDataBase(unittest.TestCase):
    def setUp(self):
        self.database = SqliteDatabase(':memory:')
        self.sql_fill_table_users = 'INSERT INTO users VALUES(?)'
        self.sql_fill_table_users_chats = 'INSERT INTO chats VALUES(?, ?)'
        self.sql_fill_table_chats_messages = 'INSERT INTO messages VALUES(?, ?, ?)'

    def test_create_database_and_users(self):
        self.database.create()
        self.database.add_user('admin')
        self.database.add_user('user_1')
        users = self.database.cursor.execute('SELECT * FROM users;').fetchall()
        self.assertIsInstance(users, list)
        for user in users:
            print(user)
            print(user.id, user.name)
        print(self.database.cursor.description)


class TestUserRepository(unittest.TestCase):
    def setUp(self):
        # dbase ='test.db'
        dbase = ':memory:'
        self.database = SqliteDatabase(dbase)
        self.database.create()
        self.repository = UserRepository(self.database)
        # self.repository = ChatRepository(self.database)
        # self.repository = DialogRepository(self.database)

    def test_add(self):
        admin_id = self.repository.add('admin', 'description of admin')
        user_id = self.repository.add('user_1', 'description of user_1')
        self.assertEqual(admin_id, 1)
        self.assertEqual(user_id, 2)
        print(admin_id, user_id)

    def test_last(self):
        self.test_add()
        user = self.repository.last_by_id()
        self.assertIsNotNone(user)
        print(f'{user=}')

    def test_list_users(self):
        self.test_add()
        users = self.repository.list()
        self.assertIsNotNone(users)
        self.assertIsInstance(users, list)
        for user in users:
            print(f'{user.id=} {user.name=} {user.description=}')

    def test_list_id(self):
        self.test_add()
        users_id = self.repository.list_id()
        self.assertIsNotNone(users_id)
        self.assertIsInstance(users_id, list)
        for user_id in users_id:
            print(f"{user_id['id']=}")

    def test_contain_id(self):
        self.test_add()
        admin_id = 1
        result = admin_id in self.repository()
        self.assertTrue(result)


class TestChatRepository(unittest.TestCase):
    def setUp(self):
        # dbase ='test.db'
        dbase = ':memory:'
        self.database = SqliteDatabase(dbase)
        self.database.create()
        # TestUserRepository()
        self.repository = ChatRepository(self.database)

    def test_add(self):
        chat_admin_id = self.repository.add(1, 'User 1 Chat number 1')
        chat_user_id = self.repository.add(2, 'Chat number 2')
        chat_admin_id_2 = self.repository.add(1, 'User 1 Chat number 2')
        self.assertEqual(chat_admin_id, 1)
        self.assertEqual(chat_user_id, 2)
        self.assertEqual(chat_admin_id_2, 3)
        print(chat_admin_id, chat_user_id)

    def test_last(self):
        self.test_add()
        user = self.repository.last_by_id(user_id=1)
        self.assertIsNotNone(user)
        print(f'{user=}')

    def test_list(self):
        self.test_add()
        user_id = 1
        chats = self.repository.list(user_id)
        self.assertIsNotNone(chats)
        self.assertIsInstance(chats, list)
        for chat in chats:
            # print(chat)
            print(f"{chat['id']=} {chat['name']=} {chat['user_id']=}")

    def test_list_id(self):
        self.test_add()
        users_id = self.repository.list_id()
        self.assertIsNotNone(users_id)
        self.assertIsInstance(users_id, list)
        for user_id in users_id:
            print(f'{user_id.id=}')

    def test_contain_id(self):
        self.test_add()
        admin_id = 1
        result = admin_id in self.repository()
        self.assertTrue(result)


class TestDialogRepository(unittest.TestCase):
    def setUp(self):
        # dbase ='test.db'
        dbase = ':memory:'
        self.database = SqliteDatabase(dbase)
        self.database.create()
        self.repository = DialogRepository(self.database)

    def test_add(self):
        chat_admin_id = self.repository.add(1, 'I never wanted this...')
        chat_user_id = self.repository.add(2, 'Let burn the Galaxy!')
        self.assertEqual(chat_admin_id, 1)
        self.assertEqual(chat_user_id, 2)
        print(chat_admin_id, chat_user_id)

    def test_last(self):
        self.test_add()
        chat = self.repository.last_by_id(chat_id=1)
        self.assertIsNotNone(chat)
        print(f'{chat=}')
        print(chat['content'])

    def test_list(self):
        self.test_add()
        messages = self.repository.list(1)
        self.assertIsNotNone(messages)
        self.assertIsInstance(messages, list)
        for message in messages:

            print(f"{message['id']=} {message['chat_id']=} {message['content']=} {message['created_at']=}")

    def test_list_id(self):
        self.test_add()
        chats_id = self.repository.list_id()
        self.assertIsNotNone(chats_id)
        self.assertIsInstance(chats_id, list)
        for user_id in chats_id:
            print(f"{user_id['id']=}")

    def test_contain_id(self):
        self.test_add()
        admin_id = 1
        result = admin_id in self.repository()
        self.assertTrue(result)
