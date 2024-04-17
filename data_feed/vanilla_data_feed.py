import asyncio
import websockets
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
        async with websockets.serve(self.worker, self.hostname, self.port):
            await asyncio.Future()

    async def worker(self, ws, path):
        while True:
            await ws.send(json.dumps(self.generate_data()))
            await asyncio.sleep(np.random.uniform(self.delay_in_seconds[0], self.delay_in_seconds[1]))

    def generate_data(self):
        stock_symbols = ['AAPL', 'GOOG', 'MSFT', 'AMZN', 'FB']
        data = {
            'id': str(uuid4()),
            'symbol': random.choice(stock_symbols),
            'price': round(random.uniform(100, 500), 2),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        return data
        
