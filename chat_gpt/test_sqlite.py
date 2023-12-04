import unittest
from backend.sqlite import Database


class TestDataBase(unittest.TestCase):
    def setUp(self):
        self.database = Database('test.db')

    def test_something(self):
        self.database.create()


if __name__ == '__main__':
    unittest.main()
