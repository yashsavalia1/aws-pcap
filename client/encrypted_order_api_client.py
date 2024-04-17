from vanilla_client import VanillaClient

import requests
import json
import urllib3
from urllib3.exceptions import InsecureRequestWarning

class EncryptedOrderAPIClient(VanillaClient):
    def __init__(self, df_hostname, df_port, or_hostname, or_port):
        super().__init__(df_hostname, df_port, or_hostname, or_port)
        urllib3.disable_warnings(InsecureRequestWarning)
    
    @property
    def order_req_url(self):
        return f"https://{self.or_hostname}:{self.or_port}/order"

    def send_response(self, msg):
        headers, data = self.generate_response(msg)
        requests.post(self.order_req_url, data=json.dumps(data), headers=headers, verify=False)