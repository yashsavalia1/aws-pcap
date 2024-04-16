import simplefix
import time
import random
from enum import Enum

def generate_random_new_order(trader_id, client_order_id=None):
    msg = simplefix.FixMessage()
    start_time = time.time()

    msg.append_string('8=FIX.4.2')  # Set the FIX version to 4.2

    sender_id = 'TRADER' + str(trader_id)
    msg.append_pair(49, sender_id, header=True)

    msg.append_pair(56, 'EXCHANGE', header=True)  # TargetCompID(56)

    msg_seq_num = random.randint(1, 1000)  # Set the message sequence number
    msg.append_pair(34, msg_seq_num, header=True)  # MsgSeqNum(34)

    msg.append_pair(35, 'D')  # 35: Set  message type

    # set sending time
    msg.append_tz_timestamp(52, precision=6, header=True)  # 52: time
    if client_order_id == None:
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
        price = round(random.uniform(1, 1000), 2)  # Set a random price for limit orders
        msg.append_pair(44, price)

    encoded_msg = msg.encode()
    end_time = time.time()
    print(f"Time taken to generate FIX message: {end_time - start_time:.6f} seconds")
    return encoded_msg

def generate_random_market_data_request():
    msg = simplefix.FixMessage()
    start_time = time.time()

    msg.append_string('8=FIX.4.2')  # Set the FIX version to 4.2
    sender_id = 'TRADER' + str(random.randint(1000, 9999))
    msg.append_pair(49, sender_id, header=True)

    msg.append_pair(56, 'EXCHANGE', header=True)  # TargetCompID(56)

    msg_seq_num = random.randint(1, 1000)  # Set the message sequence number
    msg.append_pair(34, msg_seq_num, header=True)  # MsgSeqNum(34)
    msg.append_pair(35, 'V')  # 35: Set  message type
    # set sending time
    msg.append_tz_timestamp(52, precision=6, header=True)  # 52: time
    MDReqID = str(random.randint(10000000, 99999999))
    msg.append_pair(262, MDReqID)
    encoded_msg = msg.encode()
    end_time = time.time()
    print(f"Time taken to generate FIX message: {end_time - start_time:.6f} seconds")
    return encoded_msg

class MsgType(Enum):
    newOrder = 1
    marketDataRequest = 2
    marketData = 3
    executionReportAck = 4
    executionReportFilled = 5

def getMessageType(msg):
    if msg.get(35).decode('UTF-8') == '8':
        if msg.get(39).decode('UTF-8') == '0':
            return MsgType.executionReportAck
        elif msg.get(39).decode('UTF-8') == '2':
            return MsgType.executionReportFilled
    elif msg.get(35).decode('UTF-8') == 'W':
        return MsgType.marketData
    elif msg.get(35).decode('UTF-8') == 'D':
        return MsgType.newOrder
    elif msg.get(35).decode('UTF-8') == 'V':
        return MsgType.marketDataRequest
    print("Error - Unknown message type")

def generateOrderAck(incomingMsg, msgSeqOffset):
    msg = simplefix.FixMessage()
    msg.append_string('8=FIX.4.2')  # Set the FIX version to 4.2
    msg.append_pair(49, incomingMsg.get(56).decode('UTF-8'), header=True)
    msg.append_pair(56, incomingMsg.get(49).decode('UTF-8'), header=True)  # TargetCompID(56)
    msg.append_pair(34, int(incomingMsg.get(34).decode('UTF-8')) + msgSeqOffset, header=True)  # random MsgSeqNum(34)
    msg.append_pair(35, '8')  # 35: Set  message type to Execution Report
    msg.append_tz_timestamp(52, precision=6, header=True)  # 52: time
    msg.append_pair(11, incomingMsg.get(11).decode('UTF-8')) # Set ClOrdID to the same value as the incoming message
    msg.append_pair(39, 0) # Set OrdStatus to 0 (New)
    encoded_msg = msg.encode()
    return encoded_msg

def generateOrderFill(incomingMsg, msgSeqOffset):
    msg = simplefix.FixMessage()
    msg.append_string('8=FIX.4.2')  # Set the FIX version to 4.2
    msg.append_pair(49, incomingMsg.get(56).decode('UTF-8'), header=True)
    msg.append_pair(56, incomingMsg.get(49).decode('UTF-8'), header=True)  # TargetCompID(56)
    msg.append_pair(34, int(incomingMsg.get(34).decode('UTF-8')) + msgSeqOffset, header=True)  # random MsgSeqNum(34)
    msg.append_pair(35, '8')  # 35: Set  message type to Execution Report
    msg.append_tz_timestamp(52, precision=6, header=True)  # 52: time
    msg.append_pair(11, incomingMsg.get(11).decode('UTF-8')) # Set ClOrdID to the same value as the incoming message
    msg.append_pair(39, 2) # Set OrdStatus to 2 (Filled)
    encoded_msg = msg.encode()
    return encoded_msg

def generateMarketDataResponse(incomingMsg, msgSeqOffset):
    msg = simplefix.FixMessage()
    msg.append_string('8=FIX.4.2')  # Set the FIX version to 4.2
    msg.append_pair(49, incomingMsg.get(56).decode('UTF-8'), header=True)
    msg.append_pair(56, incomingMsg.get(49).decode('UTF-8'), header=True)  # TargetCompID(56)
    msg.append_pair(34, int(incomingMsg.get(34).decode('UTF-8')) + msgSeqOffset, header=True)  # random MsgSeqNum(34)
    msg.append_pair(11, incomingMsg.get(11).decode('UTF-8')) # Set ClOrdID to the same value as the incoming message
    msg.append_pair(35, 'W')  # 35: Set  message type
    msg.append_tz_timestamp(52, precision=6, header=True)  # 52: time
    msg.append_pair(262, incomingMsg.get(262).decode('UTF-8')) # MDReqID
    encoded_msg = msg.encode()
    return encoded_msg

class TrendingRandomDelay:
    def __init__(self, initial_delay=1000, fluctuation_percent=10):
        self.current_delay = initial_delay
        self.fluctuation_percent = fluctuation_percent

    def generate_delay(self):
        fluctuation = random.uniform(-self.fluctuation_percent, self.fluctuation_percent) / 100.0
        self.current_delay = self.current_delay + (self.current_delay * fluctuation)
        return int(self.current_delay)

def parseMsg(raw_msg):
    parser = simplefix.FixParser()
    parser.append_buffer(raw_msg)
    msg = parser.get_message()
    if not msg:
        return None
    clientId = msg.get(11)
    if not clientId:
        return None
    return getMessageType(msg), clientId.decode('UTF-8')

def getFIX(raw_msg):
    parser = simplefix.FixParser()
    parser.append_buffer(raw_msg)
    return parser.get_message()
