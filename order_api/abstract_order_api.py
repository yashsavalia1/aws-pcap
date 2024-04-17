from abc import ABC, abstractmethod

class OrderAPIServer(ABC):
    @abstractmethod
    async def run(self):
        pass

    @abstractmethod
    def register_routes(self):
        pass