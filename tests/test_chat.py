import unittest
from chat_gpt.main_gpt import Roles, CreateResponce


class TestChat(unittest.TestCase):
    def setUp(self) -> None:
        role = Roles.ChatGPT
        self.to_ai = CreateResponce(role)

    def test_send_message(self):
        self.to_ai.message = 'Hello!'
        self.assertDictEqual({'role': 'user', 'content': 'Hello!'}, self.to_ai.message)
        self.to_ai.ask()
        answer = self.to_ai.answer
        self.assertIsNotNone(answer)
        print(answer)