from abc import ABC, abstractmethod

class Client(ABC):
    @abstractmethod
    def generate_response(self, msg):
        pass

    @abstractmethod
    async def send_response(self, ws):
        pass

    @abstractmethod
    async def recv_message(self, ws) -> str:
        pass

    @abstractmethod
    async def worker(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @property
    @abstractmethod
    def data_feed_url(self):
        pass

    @property
    @abstractmethod
    def order_req_url(self):
        pass
