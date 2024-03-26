from abstract_data_feed import DataFeedServer

import asyncio
import websockets
import json
import random
from datetime import datetime
from uuid import uuid4
import scipy.stats as stats
import numpy as np

class VanillaDataFeedServer(DataFeedServer):
    def __init__(self, hostname, port, delay_in_seconds) -> None:
        self.hostname = hostname
        self.port = port
        self.delay_in_seconds = stats.lognorm(s=1, loc=0, scale=np.exp(delay_in_seconds))

    def create_server(self):
        return websockets.serve(self.worker, self.hostname, self.port)

    def run(self):
        start_server = self.create_server()
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def worker(self, ws, path):
        while True:
            await self.send_data(ws)
            await asyncio.sleep(self.delay_in_seconds.rvs())

    def generate_data(self):
        stock_symbols = ['AAPL', 'GOOG', 'MSFT', 'AMZN', 'FB']
        data = {
            'id': str(uuid4()),
            'symbol': random.choice(stock_symbols),
            'price': round(random.uniform(100, 500), 2),
            'timestamp': datetime.now(datetime.UTC).isoformat()
        }
        return data

    async def send_data(self, ws):
        await ws.send(json.dumps(self.generate_data()))
