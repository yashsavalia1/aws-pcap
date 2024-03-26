# Random FIX exchange

This script simulates a FIX exchange that responds to FIX traders messages. It can handle new orders and market data requests. To market data request, it responds with market data snapshot. To new order, it firsts responds with order ack. Then after a random delay it responds with order filled.

## Features

- Respond to new order
- Respond to market data requests
- Send simulated order fills
- Handle multiple clients

## Requirements

- Python 3.7+
- `simplefix` library
- `python-dotenv` library

## Installation

To install required libraries, run:

```sh
pip install simplefix python-dotenv
```

## Usage
Run the script:
```sh
python3 exchange.py
```
The script will wait for a client to connect, then repsond to its messages.

## Important Functions
- `generateOrderAck(incomingMsg) `
Generates a order ack message to an incoming new order message
- `sendOrderFillRandomDelay(incomingMsg, client) `
Sends an order fill to the client for an incoming new order message after a random amount of delay
- `generateMarketDataResponse(incomingMsg)`
Responds with market data to a market data request message
- `handleMessage(raw_msg, client)`
Called when a message is received, handles what should be done with the message
- `listenToClient(self, client, address)`
Called when a new client connects. Is run in a seperate thread per each client, handles listening to the client and callign handleMessage whenever it receives a message from that client.
