import asyncio
import websockets
import json

async def subscribe(symbol):
    uri = "wss://testnet.binance.vision/ws-api/v3"
    
    async with websockets.connect(uri) as websocket:
        # Subscribing to the depth stream
        depth_params = {
            "id": 1,
            "method": "SUBSCRIBE",
            "params": [f"{symbol}@depth"]
        }
        await websocket.send(json.dumps(depth_params))

        # Subscribing to the trade stream
        trade_params = {
            "id": 2,
            "method": "SUBSCRIBE",
            "params": [f"{symbol}@trade"]
        }
        await websocket.send(json.dumps(trade_params))

        # Handle incoming messages
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print(data)

# Run the client
symbol = "bnbbtc"
asyncio.get_event_loop().run_until_complete(subscribe(symbol))
