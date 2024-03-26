import random
import simplefix
import time
import socket
import threading
import signal
from enum import Enum
from dotenv import load_dotenv, set_key
import os

from simplefix.message import sys

parser = simplefix.FixParser()


class MsgType(Enum):
    executionReportAck = 1
    marketData = 2
    executionReportFilled = 3


def getMessageType(msg):
    if msg.get(35).decode('UTF-8') == '8':
        if msg.get(39).decode('UTF-8') == '0':
            return MsgType.executionReportAck
        elif msg.get(39).decode('UTF-8') == '2':
            return MsgType.executionReportFilled
    elif msg.get(35).decode('UTF-8') == 'W':
        return MsgType.marketData
    print("Error - Unknown message type")


def generate_random_new_order(
        trader_id,
        exchange_id,
        client_order_id,
        msgSeqNum):
    msg = simplefix.FixMessage()
    start_time = time.time()

    msg.append_string('8=FIX.4.2')  # Set the FIX version to 4.2

    sender_id = 'TRADER' + str(trader_id)
    msg.append_pair(49, sender_id, header=True)

    msg.append_pair(
        56,
        'EXCHANGE' +
        exchange_id,
        header=True)  # TargetCompID(56)

    msg.append_pair(34, msgSeqNum, header=True)  # MsgSeqNum(34)

    msg.append_pair(35, 'D')  # 35: Set  message type

    # set sending time
    msg.append_tz_timestamp(52, precision=6, header=True)  # 52: time
    if client_order_id is None:
        client_order_id = str(random.randint(10000000, 99999999))
    msg.append_pair(11, client_order_id)

    # Symbol(55) - Set a random stock symbol
    symbols = ['AAPL', 'GOOG', 'AMZN', 'FB', 'TSLA']
    symbol = random.choice(symbols)
    msg.append_pair(55, symbol)

    side = random.choice([1, 2])  # set side (1 for Buy, 2 for sell)
    msg.append_pair(54, side)

    order_type = random.choice([1, 2])  # 1 for Market, 2 for Limit
    msg.append_pair(40, order_type)

    order_qty = random.randint(1, 1000)
    msg.append_pair(38, order_qty)

    time_in_force = random.choice([0, 1])  # (0 for Day, 1 for GTC)
    msg.append_pair(59, time_in_force)

    if order_type == 2:
        # Set a random price for limit orders
        price = round(random.uniform(1, 1000), 2)
        msg.append_pair(44, price)

    encoded_msg = msg.encode()
    end_time = time.time()
    print(
        f"Time taken to generate FIX message: {end_time - start_time:.6f} seconds")
    return encoded_msg


def generate_random_market_data_request(
        trader_id,
        exchange_id,
        client_order_id,
        msgSeqNum):
    msg = simplefix.FixMessage()
    start_time = time.time()

    msg.append_string('8=FIX.4.2')  # Set the FIX version to 4.2
    sender_id = 'TRADER' + str(trader_id)
    msg.append_pair(49, sender_id, header=True)

    msg.append_pair(
        56,
        'EXCHANGE' +
        exchange_id,
        header=True)  # TargetCompID(56)
    msg.append_pair(11, client_order_id)

    msg.append_pair(34, msgSeqNum, header=True)  # MsgSeqNum(34)
    msg.append_pair(35, 'V')  # 35: Set  message type
    # set sending time
    msg.append_tz_timestamp(52, precision=6, header=True)  # 52: time
    MDReqID = str(random.randint(10000000, 99999999))
    msg.append_pair(262, MDReqID)
    encoded_msg = msg.encode()
    end_time = time.time()
    print(
        f"Time taken to generate FIX message: {end_time - start_time:.6f} seconds")
    return encoded_msg


def handleMessage(raw_msg):
    parser.append_buffer(raw_msg)
    msg = parser.get_message()
    type = getMessageType(msg)
    if type == MsgType.executionReportAck:
        print('Received execution report ACK')
    elif type == MsgType.marketData:
        print('Received market data')
    elif type == MsgType.executionReportFilled:
        print('Received execution report FILLED')


def recv(s):
    while True:
        data = s.recv(1024).decode()
        if data:
            handleMessage(data)

currentMessageId = 0
currentMessageSeq = 0

lock = threading.Lock()

def sigintHandler(sig, frame):
    global currentMessageId
    set_key(dotenv_path="../.env", key_to_set="TRADER_MSG_ID", value_to_set=str(currentMessageId + 1))
    print(f"\nSIGINT Caught - ClOrdID: {currentMessageId}, MSGSEQ: {currentMessageSeq}")
    sys.exit(0)

if __name__ == '__main__':
    load_dotenv()

    currentMessageId = 0 if os.environ.get("TRADER_MSG_ID") == None else int(os.environ["TRADER_MSG_ID"])
    currentMessageSeq = currentMessageId * 10

    UDP_PORT = os.environ.get("UDP_BROADCAST_PORT")
    PORT = os.getenv('EXCHANGE_PORT')
    BASE_IP = os.getenv('EXCHANGE_BASE_IP')
    OCLET = os.getenv('EXCHANGE_START_OCTET')
    NUM_EXCHANGES = os.getenv('NUM_EXCHANGES')

    if (UDP_PORT is None or PORT is None or BASE_IP is None or OCLET is None or NUM_EXCHANGES is None):
        exit(-1)

    UDP_PORT = int(UDP_PORT)
    PORT = int(PORT)
    NUM_EXCHANGES = int(NUM_EXCHANGES)
    
    signal.signal(signal.SIGINT, sigintHandler)

    def connectAndHandleExchange(
            ip,
            port,
            ):

        global currentMessageId
        global currentMessageSeq
        global lock

        s = socket.socket()
        s.connect((ip, port))

        t = threading.Thread(target=recv, args=(s,))
        t.daemon = True
        t.start()

        traderId = os.getenv('CUR_IP')
        if traderId:
            traderId = traderId[-2:]
        else:
            traderId = random.randint(50, 100)

        while True:
            with lock:
                choice = random.choice([1, 2, 2, 2, 2])
                print(f"Generating for #{currentMessageId}")
                if choice == 1:
                    z = generate_random_market_data_request(
                        traderId, ip[-2:], f"M-{traderId}-{currentMessageId}", currentMessageSeq)
                else:
                    z = generate_random_new_order(
                        traderId, ip[-2:], f"O-{traderId}-{currentMessageId}", currentMessageSeq)
                s.sendall(z)
                currentMessageId += 1
                currentMessageSeq += 10
            time_wait = random.uniform(2, 5)
            time.sleep(time_wait)

    def listenUDPBroadcast():
        udpSock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP)
        udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udpSock.bind(("0.0.0.0", UDP_PORT))

        while True:
            data = udpSock.recv(4096)
            if data:
                print("[UDP BROADCAST] -", end=" ")
                handleMessage(data)

    threading.Thread(target=listenUDPBroadcast).start()


    for i in range(NUM_EXCHANGES):
        thread = threading.Thread(target=connectAndHandleExchange, args=(
            BASE_IP + str(int(OCLET) + i), PORT,))
        thread.start()
