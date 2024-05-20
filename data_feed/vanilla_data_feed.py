import asyncio
from websockets import server
import json
import random
from datetime import datetime, timezone
from uuid import uuid4
import scipy.stats as stats
import numpy as np

class VanillaDataFeedServer():
    def __init__(self, hostname, port, delay_in_seconds) -> None:
        self.hostname = hostname
        self.port = port
        self.delay_in_seconds = [delay_in_seconds - 2, delay_in_seconds + 2]


    async def run(self):
        async with server.serve(self.worker, self.hostname, self.port, compression=None):
            await asyncio.Future()

    async def worker(self, ws, path):
        while True:
            await ws.send(json.dumps(self.generate_data()))
            await asyncio.sleep(np.random.uniform(self.delay_in_seconds[0], self.delay_in_seconds[1]))

    def generate_data(self):
        stock_symbols = ['AAPL', 'GOOG', 'MSFT', 'AMZN', 'FB']
        stock_prices = [170, 165, 395, 179, 439]
        random_choice = random.randint(0, 4)
        price_range = stats.norm(stock_prices[random_choice], 0.01 * stock_prices[random_choice])
        price = price_range.rvs()
        data = {
            'id': str(uuid4()),
            'symbol': stock_symbols[random_choice],
            'price': round(price, 2),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        return data

    def generate_bitcoin_data(self):
        price_range = stats.norm(70000, 0.01 * 70000)
        price = price_range.rvs()
        quantity = np.random.randint(1, 201)
        mm = np.random.rand() <= 0.8
        data = {
            'e': 'trade',
            'E': datetime.now(timezone.utc).isoformat(),
            's': 'BTCUSDT',
            't': str(uuid4()),
            'p': round(price, 3),
            'q': quantity,
            'b': str(uuid4()),
            'a': str(uuid4()),
            'T': datetime.now(timezone.utc).isoformat(),
            'm': mm,
            'M': True 
        }
        return data
