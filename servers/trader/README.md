# Random FIX Client

This script simulates a random FIX client that sends and receives FIX messages for market data and new order executions. It generates random new order and market data request messages, sends them to a specified exchange server, and handles the responses. 

## Features

- Generates random new order messages
- Generates random market data request messages
- Handles execution report messages
- Handles market data messages

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
Create a .env file in the same directory as the script, and add the following variables:

```sh
EXCHANGE_IP=<Your_Exchange_IP>
EXCHANGE_PORT=<Your_Exchange_Port>
```
Run the script:
```sh
python random_fix_client.py
```
The script will start generating random FIX messages and send them to the specified exchange server.



## Important Functions
- `generate_random_new_order(client_order_id) `
Generates a random new order FIX message.
- `generate_random_market_data_request() `
Generates a random market data request FIX message.
- `handleMessage(raw_msg)`  Handles received FIX messages and returns the appropriate response.
- `recv()`  Receives messages from the server in a separate thread.