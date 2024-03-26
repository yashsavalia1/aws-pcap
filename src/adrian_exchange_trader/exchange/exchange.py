import socket
import simplefix
from enum import Enum
import random
import select
import threading
from dotenv import load_dotenv
import os
from threading import Thread
import time

parser = simplefix.FixParser()

class MsgType(Enum):
    newOrder = 1
    marketDataRequest = 2

def getMessageType(msg):
    if msg.get(35).decode('UTF-8') == 'D':
        return MsgType.newOrder
    elif msg.get(35).decode('UTF-8') == 'V':
        return MsgType.marketDataRequest
    print("Error - Unknown message type")

def generateOrderAck(incomingMsg):
    msg = simplefix.FixMessage()
    msg.append_string('8=FIX.4.2')  # Set the FIX version to 4.2
    msg_seq_num = random.randint(1, 1000)
    msg.append_pair(34, msg_seq_num, header=True)  # random MsgSeqNum(34)
    msg.append_pair(35, '8')  # 35: Set  message type to Execution Report
    msg.append_tz_timestamp(52, precision=6, header=True)  # 52: time
    msg.append_pair(11, incomingMsg.get(11).decode('UTF-8')) # Set ClOrdID to the same value as the incoming message
    msg.append_pair(39, 0) # Set OrdStatus to 0 (New)
    encoded_msg = msg.encode()
    return encoded_msg

def sendOrderFillRandomDelay(incomingMsg, client):
    time.sleep(random.uniform(0, 2))
    try:
        client.send(generateOrderFill(incomingMsg))
    except:
        print('Error sending order fill')
        return
    print('Sent order fill')

def generateOrderFill(incomingMsg):
    msg = simplefix.FixMessage()
    msg.append_string('8=FIX.4.2')  # Set the FIX version to 4.2
    msg_seq_num = random.randint(1, 1000)
    msg.append_pair(34, msg_seq_num, header=True)  # random MsgSeqNum(34)
    msg.append_pair(35, '8')  # 35: Set  message type to Execution Report
    msg.append_tz_timestamp(52, precision=6, header=True)  # 52: time
    msg.append_pair(11, incomingMsg.get(11).decode('UTF-8')) # Set ClOrdID to the same value as the incoming message
    msg.append_pair(39, 2) # Set OrdStatus to 2 (Filled)
    encoded_msg = msg.encode()
    return encoded_msg

def generateMarketDataResponse(incomingMsg):
    msg = simplefix.FixMessage()
    msg.append_string('8=FIX.4.2')  # Set the FIX version to 4.2
    msg_seq_num = random.randint(1, 1000)  # Set the message sequence number
    msg.append_pair(34, msg_seq_num, header=True)  # MsgSeqNum(34)
    msg.append_pair(35, 'W')  # 35: Set  message type
    msg.append_tz_timestamp(52, precision=6, header=True)  # 52: time
    msg.append_pair(262, incomingMsg.get(262).decode('UTF-8')) # MDReqID
    encoded_msg = msg.encode()
    return encoded_msg

def handleMessage(raw_msg, client):
    parser.append_buffer(raw_msg)
    msg = parser.get_message()
    type = getMessageType(msg)
    if type == MsgType.newOrder:
        print('Received a new order')
        response = generateOrderAck(msg)
        client.send(response)
        thread = Thread(target = sendOrderFillRandomDelay, args = (msg, client,))
        thread.start()

    elif type == MsgType.marketDataRequest:
        print('Received a market data request')
        response = generateMarketDataResponse(msg)
        client.send(response)

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            readable, _, _ = select.select([self.sock], [], [], 1.0)
            if self.sock in readable:
                client, address = self.sock.accept()
                print("Connected to client IP: {}".format(address))
                client.settimeout(60)
                threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    print("Received data: {} from IP: {}".format(data, address))
                    handleMessage(data, client)
                    
                else:
                    print("Closing connection to client IP: {}".format(address))
                    client.close()
                    return False
            except:
                print("Closing connection to client IP: {}".format(address))
                client.close()
                return False

if __name__ == "__main__":
    load_dotenv()
    PORT = int(os.getenv('EXCHANGE_PORT'))
    ThreadedServer('',PORT).listen()


