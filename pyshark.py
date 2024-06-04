import pyshark
import json
from pprint import pprint
from datetime import datetime
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import sys

load_dotenv()
print(os.getenv("SSLKEYLOGFILE"))

if len(sys.argv) != 2:
    print("Usage: python script.py [pcap file name]")
    sys.exit(1)  # Exit the script if no parameter or too many parameters are provided

pcap_path = sys.argv[1] 

sslkey_logfile_path = os.environ.get('SSLKEYLOGFILE') 
cap = pyshark.FileCapture(pcap_path, override_prefs={'tls.keylog_file': sslkey_logfile_path}, debug=True)
ts_map = {}

count = 0
print("Total # of packets: ", len(cap))
for packet in cap:
    # Check if the packet contains HTTP layer
    if 'http' in packet:
        # Check if the HTTP layer has the 'file_data' field which contains the payload
        if hasattr(packet.http, 'file_data'):
            try:
                # Attempt to decode the payload as ASCII
                http_payload = packet.http.file_data.binary_value.decode('ascii')
                # print(f"HTTP Payload (ASCII): {http_payload}")
                payload_json = json.loads(http_payload)
                if 'id' in payload_json:
                    id = payload_json["id"]
                    if id not in ts_map:
                        ts_map[id] = ["", "", -1.0]
                    ts_map[id][1] = payload_json["timestamp"]
            except UnicodeDecodeError:
                print("HTTP payload is not ASCII encoded")
    # Check if the packet contains WebSocket layer
    if 'websocket' in packet:
        # The payload in WebSocket can be found in different fields depending on the frame type
        if hasattr(packet.websocket, 'payload'):
            websocket_payload = packet.websocket
            # The payload might be encoded, for example, as Base64
            # print(f"WebSocket Opcode: {websocket_payload.field_names}")
            # print(f"WebSocket Opcode: {websocket_payload}")
            if hasattr(websocket_payload, 'payload_text'):
            # if hasattr(websocket_payload, 'payload_text') and packet.websocket.opcode == "1":
                # print(f"WebSocket Text: {websocket_payload.payload_text}")
                payload_json = json.loads(websocket_payload.payload_text)
                if 'id' in payload_json:
                    id = payload_json["id"]
                    if id not in ts_map:
                        ts_map[id] = ["", "", -1.0]
                    ts_map[id][0] = payload_json["timestamp"]

# pprint(ts_map)

for id, ts in ts_map.items():
    start = datetime.fromisoformat(ts[0])
    end = datetime.fromisoformat(ts[1])

    ts_map[id][2] = (end - start).total_seconds() * 1000


# pprint([ts[2] for id, ts in ts_map.items()])
# Extract delays (in milliseconds) from the ts_map
delays = [ts[2] for ts in ts_map.values()]

# Plot histogram
plt.hist(delays, bins=50, color='skyblue', edgecolor='black')  # Increased number of bins for granularity
plt.xlabel('Delay (ms)')
plt.ylabel('Frequency')
plt.title('Histogram of Message Delays')
plt.grid(axis='y', alpha=0.75)

plt.tight_layout()  # Adjust the layout to make room for the label
plt.show()
