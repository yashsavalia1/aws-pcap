from abstract_client import Client

import asyncio
import websockets
import requests
import json
from datetime import datetime
import random

class VanillaClient(Client):
    def __init__(self, df_hostname, df_port, or_hostname, or_port):
        self.d_hostname = df_hostname
        self.df_port = df_port
        self.or_hostname = or_hostname
        self.or_port = or_port

    @property
    def data_feed_url(self):
        return f"ws://{self.df_hostname}:{self.df_port}"

    @property
    def order_req_url(self):
        # return f"https://{self.or_hostname}:{self.or_port}/order"
        return f"http://{self.or_hostname}:{self.or_port}/order"

    def generate_response(self, msg):
        data = {
            "type": "buy",
            "amount": "100",
            "id": json.loads(msg)["id"],
            "timestamp": datetime.now(datetime.UTC).isoformat()
        }
        headers = {'Content-Type': 'application/json'}
        return (headers, data)

    def send_response(self, msg):
        headers, data = self.generate_response(msg)
        # requests.post(self.order_req_url, data=json.dumps(data), headers=headers, verify=False)
        requests.post(self.order_req_url, data=json.dumps(data), headers=headers)

    async def recv_message(self, ws) -> str:
        msg = await ws.recv()
        print(msg)
        return msg

    async def worker(self):
        async with websockets.connect(self.data_feed_url) as websocket:
            while True:
                msg = await self.recv_message(websocket)
                if random.randint(1, 5) == 1:
                    self.send_response(msg)

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.worker())
