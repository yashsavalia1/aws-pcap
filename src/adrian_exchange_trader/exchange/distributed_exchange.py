from threading import Thread
import socket
import os
from time import sleep
import importlib
from dotenv import load_dotenv
from Nsleep import py_nanosleep
FIXHelper = importlib.import_module('FIXHelper')

class FIXClient(Thread):
    def __init__(self, host, port, onSend=None, onResponse=None):
        super(FIXClient, self).__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.onSend = onSend
        self.onResponse = onResponse

    def run(self):
        while True:
            try:
                sleep(1)
                self.sock.connect((self.host, self.port))
                break
            except BaseException:
                print("Waiting for server to open...")
                print("Retrying connection in 1s...")
        self.connected = True
        if self.onSend:
            Thread(target=self.onSend, args=(self.sock,)).start()
        while True:
            data = None;
            try:
                data = self.sock.recv(4096)
            except:
                print('Error receiving data from server')
            if data and self.onResponse:
                self.onResponse(data, self.sock)


#     def sendRandom(self):
#         while True:
#             with self.lock:
#                 self.onMessage()
#                 self.sock.sendall(f"{self.msgCount[0]}".encode())
#                 self.msgCount[0] += 1
#             sleep(random.randint(1,5))


class FIXServer(Thread):
    def __init__(self, host, port, onRecv):
        super(FIXServer, self).__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        self.onRecv = onRecv
        self.replyConn = None

    def run(self):
        while True:
            clientConnection, _ = self.sock.accept()
            Thread(
                target=self.handleClient, args=(
                    (clientConnection,))).start()

    def handleClient(self, conn):
        self.replyConn = conn
        while True:
            data = conn.recv(4096)
            if data:
                try:
                    self.onRecv(data, conn)
                except:
                    print('Error receiving data from target')


class FIXExchange():
    def __init__(self) -> None:
        portStr = os.environ.get('EXCHANGE_PORT')
        if portStr:
            port = int(portStr)
        else:
            port = 3125

        self.gatewayOMEClient = FIXClient(os.environ.get('OME_IP'), port)
        self.gatewayDropCopyClient = FIXClient(os.environ.get('DROPCOPY_IP'), port)
        self.omeClient = FIXClient(os.environ.get('TICKER_IP'), port)

        self.gatewayDelay = FIXHelper.TrendingRandomDelay(10000, 10)
        self.omeDelay = FIXHelper.TrendingRandomDelay(100000, 20)
        self.tickerDelay = FIXHelper.TrendingRandomDelay(10000, 10)
        self.dropCopyDelay = FIXHelper.TrendingRandomDelay(10000, 10)

        self.udpTickerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udpTickerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.udpTickerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udpTickerSocket.settimeout(0.2)

        def onRecvGateway(data, conn):
            print("Received on Gateway -", end=" ")
            ackData = FIXHelper.generateOrderAck(FIXHelper.getFIX(data), 1)
            try:
                conn.sendall(ackData)
            except:
                print('Error sending fix acknowledgement to client')
            msgType, msgId = FIXHelper.parseMsg(data)
            py_nanosleep(0, self.gatewayDelay.generate_delay())
            
            if msgType == FIXHelper.MsgType.newOrder:
                forwardData = FIXHelper.generateOrderFill(FIXHelper.getFIX(data), 2)
                print(f"[FIX NEW ORDER] #{msgId}")
                try:
                    self.gatewayOMEClient.sock.sendall(forwardData)
                except:
                    print('Error connecting to the OME')
            elif msgType ==  FIXHelper.MsgType.marketDataRequest:
                forwardMktData = FIXHelper.generateMarketDataResponse(FIXHelper.getFIX(data), 2)
                print(f"[FIX MARKET REQUEST] #{msgId}")
                try:
                    self.gatewayDropCopyClient.sock.sendall(forwardMktData)
                except:
                    print('Error connecting to the Drop Copy')

        def onRecvOME(data, _):
            print("Received on OME")
            orderFillData = FIXHelper.generateOrderFill(FIXHelper.getFIX(data), 1)
            py_nanosleep(0, self.omeDelay.generate_delay())
            try:
                self.omeClient.sock.sendall(orderFillData)
            except:
                print("Error connecting to the Ticker")

        def onRecvTicker(data, _):
            print("Received on Ticker")
            tickerSendData = FIXHelper.generateOrderFill(FIXHelper.getFIX(data), 1)
            udpPortStr = os.environ.get('UDP_BROADCAST_PORT')
            if udpPortStr:
                udpPort = int(udpPortStr)
            else:
                udpPort = 3200
            try:
                self.udpTickerSocket.sendto(tickerSendData, (f"{os.environ.get('TRADER_BASE_IP')}255", udpPort))
            except:
                print("Error sending UDP broadcast")
            py_nanosleep(0, self.tickerDelay.generate_delay())
            if self.gatewayServer.replyConn:
                try:
                    self.gatewayServer.replyConn.sendall(tickerSendData)
                except:
                    print('Error sending order fill to client')

        def onRecvDropCopy(data, _):
            print("Received on Drop Copy")
            marketDataRes = FIXHelper.generateMarketDataResponse(FIXHelper.getFIX(data), 3)
            py_nanosleep(0, self.dropCopyDelay.generate_delay())
            if self.gatewayServer.replyConn:
                try:
                    self.gatewayServer.replyConn.sendall(marketDataRes)
                except:
                    print('Error sending market data to client')

        self.omeServer = FIXServer(os.environ.get('OME_IP'), port, onRecvOME)
        self.tickerServer = FIXServer(os.environ.get('TICKER_IP'), port, onRecvTicker)
        self.dropCopyServer = FIXServer(os.environ.get('DROPCOPY_IP'), port, onRecvDropCopy)
        self.gatewayServer = FIXServer(os.environ.get('CUR_IP'), port, onRecvGateway)

    def start(self):
        self.gatewayServer.start()
        self.omeServer.start()
        self.tickerServer.start()
        self.gatewayOMEClient.start()
        self.gatewayDropCopyClient.start()
        self.omeClient.start()
        self.dropCopyServer.start()

if __name__ == "__main__":
    load_dotenv()

#     def generateRandomFIX(conn):
#         msgNum = 0
#         while True:
#             packet = FIXHelper.generate_random_new_order(0, msgNum)
#             conn.sendall(packet)
#             msgNum += 1
#             print('Sending Trade...')
#             sleep(random.randint(1, 5))
# 
#     def onResponse(data, _):
#         msgType, msgId = FIXHelper.parseMsg(data)
#         print(f"Received Packet: {msgType.name} of id {msgId}")
# 
#     trader = FIXClient(
#         "127.0.0.1",
#         port,
#         generateRandomFIX,
#         onResponse=onResponse)
#     trader.start()

    FIXExchange().start()
