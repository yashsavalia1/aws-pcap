import socket
import json
import random
import threading
import time
import os
from dotenv import load_dotenv

class TrendingRandomDelay:
    def __init__(self, initial_delay=1000, fluctuation_percent=10):
        self.current_delay = initial_delay
        self.fluctuation_percent = fluctuation_percent

    def generate_delay(self):
        fluctuation = random.uniform(-self.fluctuation_percent, self.fluctuation_percent) / 100.0
        self.current_delay = self.current_delay + (self.current_delay * fluctuation)
        return int(self.current_delay)

class Exchange:
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))
        self.s.listen(5)
        self.gw_in_delay = TrendingRandomDelay(initial_delay=10000000)
        self.ome_in_delay = TrendingRandomDelay()
        self.ome_out_delay = TrendingRandomDelay()
        self.ticker_delay = TrendingRandomDelay()
        self.gw_out_delay = TrendingRandomDelay()
        
    def process_packet(self, data, socket):
        packet = json.loads(data.decode())
        print(f'Received packet: {packet}')

        hostname, port = socket.getpeername()
        packet['source_ip'] = str(hostname)
        packet['gateway_in'] = str(int(packet['trader_out']) + self.gw_in_delay.generate_delay())
        packet['ome_in'] = str(int(packet['gateway_in']) + self.ome_in_delay.generate_delay())
        packet['ome_out'] = str(int(packet['ome_in']) + self.ome_out_delay.generate_delay())
        packet['ticker_out'] = str(int(packet['ome_out']) + self.ticker_delay.generate_delay())
        packet['gateway_out'] =str(int(packet['ticker_out']) + self.gw_out_delay.generate_delay())

        return json.dumps(packet).encode()

    def start(self):
        while True:
            clientsocket, address = self.s.accept()
            threading.Thread(target=self.handle_client, args=(clientsocket,)).start()

    def handle_client(self, clientsocket):
        while True:
            data = clientsocket.recv(1024)
            if not data:
                break

            print(f'From IP: {clientsocket.getpeername()}')
            processed_packet = self.process_packet(data, clientsocket)
            clientsocket.sendall(processed_packet)

if __name__ == '__main__':
    load_dotenv()
    PORT = int(os.getenv('EXCHANGE_PORT'))
    exchange = Exchange('', PORT)
    exchange.start()