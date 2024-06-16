from scapy.all import *
from scapy.layers.ssl_tls import ssl_tls_process_session_from_keylog

# Load the SSL key log file
ssl_keylog = ssl_tls_process_session_from_keylog("sslkeylog.log", True)

def handle_packet(packet):
    if packet.haslayer(SSL):
        # Decrypt the SSL/TLS packet
        decrypted = ssl_keylog.decrypt_payload(packet[SSL])
        if decrypted:
            print(f"Decrypted payload: {decrypted.payload}")

# Start capturing packets
sniff(iface="eth0", prn=handle_packet)