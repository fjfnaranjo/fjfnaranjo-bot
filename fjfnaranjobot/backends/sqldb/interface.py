from abc import ABC, abstractmethod


class SQLDatabase(ABC):
    @abstractmethod
    def execute(self, sentence, *params):
        pass

    @abstractmethod
    def execute_and_fetch_index(self, sentence, *params):
        pass

    @abstractmethod
    def execute_and_fetch_one(self, sentence, *params):
        pass

    @abstractmethod
    def execute_and_fetch_all(self, sentence, *params):
        pass
