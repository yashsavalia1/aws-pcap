import asyncio
import os
import sqlite3
import sys
import requests
import json
import signal
from subprocess import Popen, PIPE, STDOUT
from dotenv import load_dotenv
import os
import pyshark
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

dir_path = os.path.dirname(os.path.realpath(__file__))

load_dotenv()

print("Starting packet capture...")

conn = sqlite3.connect(os.path.join(dir_path, "../prisma/database.db"))
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS TCPPacket")
cursor.execute(
    """CREATE TABLE TCPPacket (
"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
"timestamp" DATETIME NOT NULL,
"source" TEXT NOT NULL,
"destination" TEXT NOT NULL,
"length" INTEGER NOT NULL,
"data" TEXT NOT NULL
)"""
)

cursor.execute("CREATE INDEX index_timestamp ON TCPPacket(timestamp)")

conn.commit()
conn.close()


def convert_to_ip(hexStr):
    # Split the string into four segments of two characters each
    segments = [hexStr[i : i + 2] for i in range(0, len(hexStr), 2)]

    # Convert each segment from hexadecimal to decimal
    decimal_segments = [int(segment, 16) for segment in segments]

    # Convert the decimal segments to a string and join them with dots
    ip_address = ".".join(map(str, decimal_segments))

    return ip_address


async def start_capture():
    with Popen(
        os.path.join(dir_path, "./netcap"),
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=STDOUT,
        universal_newlines=True,
    ) as p:
        try:
            for line in p.stdout:
                data = json.loads(line)
                if type(data) != dict:
                    continue
                payload = data["raw_data"]["rawhex"]
                if int(data["raw_data"]["ip_protocol"]) == 56: # 0x38 = 56 (TLSP)
                    tls_payload = data["raw_data"]["rawhex"]
                    key = open('~/ssl_key.log', 'r').read()
                    backend = default_backend()
                    cipher = Cipher(algorithms.AES(key), modes.CBC(bytes.fromhex(tls_payload)), backend=backend)
                    decryptor = cipher.decryptor()
                    decrypted_payload = decryptor.update(bytes.fromhex(tls_payload)) + decryptor.finalize()
                    payload = decrypted_payload.hex()
                
                conn = sqlite3.connect(os.path.join(dir_path, "../prisma/database.db"))
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO TCPPacket (timestamp, source, destination, length, data) VALUES (?, ?, ?, ?, ?)",
                    (
                        data["tstamp_sec"],
                        convert_to_ip(data['raw_data']["ip_src_ip"]),
                        convert_to_ip(data['raw_data']["ip_dst_ip"]),
                        data["capture_length"],
                        payload,
                    ),
                )
                conn.commit()
                conn.close()

        except KeyboardInterrupt:
            p.send_signal(signal.SIGINT)
            p.wait()
            out, err = p.communicate()
            print(out)
            sys.exit(0)


asyncio.run(start_capture())
