import socket
import time
import json
import random
import time
from datetime import datetime
import socket
import threading
from enum import Enum
from dotenv import load_dotenv
import requests
import os

def generate_trace_packet(gw_ip):
    order_id = random.randint(10000000, 99999999)
    packet = {'order_id': order_id,
              'source_ip': None,
              'gateway_ip': gw_ip,
              'trader_in': None,
              'trader_out': str(int(time.time() * (10 ** 9))),
              'gateway_in': None,
              'gateway_out': None,
              'ome_in': None,
              'ome_out': None,
              'ticker_out': None,
              'latency': None
              }
    return json.dumps(packet).encode()  # serialize the packet to string

def recv(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break

        response_packet = json.loads(data.decode())  # Deserialize the packet
        response_packet['trader_in'] = str(int(time.time() * (10 ** 9)))

        response_packet['latency'] = int(response_packet['trader_in']) - int(response_packet['trader_out'])

        print('Received', response_packet)

        api_url = "http://" + os.getenv('BACKEND_IP') + ":3000/PingPong"

        response = requests.post(api_url, json=response_packet)
        print(f"Data sent to API, response: {response.status_code}")

def connect_and_handle_gw(ip, port):
    s = socket.socket()
    s.connect((ip, port))
    t = threading.Thread(target=recv, args=(s,))
    t.daemon = True
    t.start()

    while True:
        packet = generate_trace_packet(ip)
        s.sendall(packet)
        time_wait = random.uniform(5, 6)
        time.sleep(time_wait)

if __name__ == '__main__':
    load_dotenv()

    PORT = int(os.getenv('EXCHANGE_PORT'))
    BASE_IP = os.getenv('EXCHANGE_BASE_IP')
    OCLET = os.getenv('EXCHANGE_START_OCTET')

    NUM_EXCHANGES = int(os.getenv('NUM_EXCHANGES'))
    for i in range(NUM_EXCHANGES):
        thread = threading.Thread(target=connect_and_handle_gw, args=(BASE_IP + str(int(OCLET) + i), PORT,))
        thread.start()
