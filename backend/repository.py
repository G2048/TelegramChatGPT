from abc import ABC, abstractmethod


class IMessageRepository(ABC):

    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def __contains__(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self):
        pass

    @abstractmethod
    def __delitem__(self):
        pass


class ListMessageRepository(IMessageRepository):
    def __init__(self):
        self.messages = []

    def add(self, message):
        self.messages.append(message)

    def get(self):
        return self.messages

    def __contains__(self, item):
        return item in self.messages

    def __len__(self):
        return len(self.messages)

    def __getitem__(self, index):
        return self.messages[index]

    def __delitem__(self, index):
        del self.messages[index]

    def __repr__(self):
        return str(self.messages)