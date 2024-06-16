import asyncio
import websockets

async def echo(websocket, path):
    async for message in websocket:
        # When a message is received from the client, echo it back
        await websocket.send(message)

async def main():
    # Start the WebSocket server on localhost, port 8765
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # Keeps the server running indefinitely

if __name__ == "__main__":
    asyncio.run(main())
