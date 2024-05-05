import time
from websockets import connect
import asyncio
import sys
import sqlite3
import aiosqlite
import json

conn = sqlite3.connect("./prisma/database.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS trades")
cursor.execute(""" CREATE TABLE trades(
                        id int PRIMARY KEY,
                        time int,
                        quantity int,
                        price float)""")

cursor.execute("CREATE INDEX index_time ON trades(time)")

conn.commit()
conn.close()

url = "wss://fstream.binance.com/ws/btcusdt@aggTrade"

async def save_data(url):

    async with connect(url) as websocket:
        
        buffer = []
        
        while True:
            data = await websocket.recv()
            data = json.loads(data)
            buffer.append((data['a'],data['T'],data['q'],data['p']))

            #print(data)

            if len(buffer) > 3:

                #print('Writing to DB !!')

                async with aiosqlite.connect("./prisma/database.db") as db:
                    delay = time.time()
                    await db.executemany("""INSERT INTO trades
                                         (id, time, quantity, price) VALUES (?,?,?,?)""", buffer)
                    await db.commit()
                    print(f"Time taken to write to DB: {time.time()-delay}")
                
                buffer = []

            # print(data)


asyncio.run(save_data(url))