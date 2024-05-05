import sqlite3
import time

def get_last_10_trades():
    conn = sqlite3.connect("./prisma/database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM trades ORDER BY time DESC LIMIT 10")
    data = cursor.fetchall()
    return data[0][3]

while True:
    print(get_last_10_trades(), flush=True, end='\r')
    time.sleep(0.1)