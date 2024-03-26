from vanilla_client import VanillaClient

import ssl
import websockets
import requests
import json
import urllib3
from urllib3.exceptions import InsecureRequestWarning

class EncryptedClient(VanillaClient):
    def __init__(self, df_hostname, df_port, or_hostname, or_port):
        super().__init__(df_hostname, df_port, or_hostname, or_port)
        urllib3.disable_warnings(InsecureRequestWarning)
    
    @property
    def data_feed_url(self):
        return f"wss://{self.df_hostname}:{self.df_port}"

    async def worker(self):
        # disable SSL Verfication
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with websockets.connect(self.data_feed_url, ssl=ssl_context) as websocket:
            while True:
                msg = await self.recv_message(websocket)
                self.send_response(msg)

    @property
    def order_req_url(self):
        return f"https://{self.or_hostname}:{self.or_port}/order"

    def send_response(self, msg):
        headers, data = self.generate_response(msg)
        requests.post(self.order_req_url, data=json.dumps(data), headers=headers, verify=False)