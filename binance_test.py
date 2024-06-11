import asyncio
import os
import threading
import time
import websockets
import json
import requests

os.environ['SSLKEYLOGFILE'] = 'keylog.txt'
monitor_ip = "172.31.23.121"

file_contents = ""
with open("keylog.txt", "r") as f:
    file_contents = f.read()

stop_thread = False
class FileWatcherThread(threading.Thread):
    def run(self,*args,**kwargs):
        global file_contents
        global stop_thread
        global monitor_ip
        while True:
            if stop_thread:
                break
            time.sleep(0.1)            
            with open("keylog.txt", "r") as f:
                c = f.read()
                if c != file_contents:
                    requests.post(f"http://{monitor_ip}/api/ssl-keys", files={"file": open("keylog.txt", "rb")})
                    

t = FileWatcherThread()
t.start()

async def subscribe(symbol):
    uri = "wss://fstream.binance.com/ws/btcusdt@aggTrade"
    
    async with websockets.connect(uri) as websocket:
        # Handle incoming messages
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print(data)


# Run the client
symbol = "bnbbtc"
try:
    asyncio.get_event_loop().run_until_complete(subscribe(symbol))
except KeyboardInterrupt:
    stop_thread = True
