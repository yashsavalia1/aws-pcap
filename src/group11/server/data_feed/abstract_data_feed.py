from abc import ABC, abstractmethod

class DataFeedServer(ABC):
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    async def worker(self, ws, path):
        pass

    @abstractmethod
    def generate_data(self):
        pass

    @abstractmethod
    async def send_data(self, ws):
        pass