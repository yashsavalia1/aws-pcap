from typing import List
import pyshark
from pyshark.packet.packet import Packet
from pyshark.packet.layers.base import BaseLayer
import json


def int_to_tcp_flags(flags: int) -> List[str]:
    flag_str = []
    if flags & 0x01:
        flag_str.append("FIN")
    if flags & 0x02:
        flag_str.append("SYN")
    if flags & 0x04:
        flag_str.append("RST")
    if flags & 0x08:
        flag_str.append("PSH")
    if flags & 0x10:
        flag_str.append("ACK")
    if flags & 0x20:
        flag_str.append("URG")
    if flags & 0x40:
        flag_str.append("ECE")
    if flags & 0x80:
        flag_str.append("CWR")
    return flag_str


cap = pyshark.LiveCapture(
    # """\\Device\\NPF_{FE25A37F-E1DA-4501-A03C-4BAD92808BFC}""",
    # bpf_filter="tcp",
    "ens5",
    bpf_filter="port 4789",
    use_json=True,
    include_raw=True,
    override_prefs={"tls.keylog_file": "keylog.txt"},
    debug=True,
)
for packet in cap.sniff_continuously():
    packet: Packet

    if "ip" in packet:
        ip_src = packet.ip.src
        ip_dst = packet.ip.dst

    tcp_flags = []
    transport_protocol = ""
    if "tcp" in packet:
        transport_protocol = "TCP"
        tcp_flags = int_to_tcp_flags(int(packet.tcp.flags, 16))

    app_protocol = ""
    if "http" in packet:
        app_protocol = "HTTP"

    # Check if the packet contains WebSocket layer
    payload_json = {}
    if "websocket" in packet:
        app_protocol = "WebSocket"
        # The payload in WebSocket can be found in different fields depending on the frame type
        if hasattr(packet.websocket, "payload"):
            websocket_payload = packet.websocket.payload
            if hasattr(websocket_payload, "text"):
                payload_json = json.loads(websocket_payload.text)

    tcp_packet = {
        "source_ip": ip_src,
        "dest_ip": ip_dst,
        "timestamp": packet.sniff_timestamp,
        "raw_packet": packet.get_raw_packet().hex(),
        "length": packet.length,
        "tcp_flags": tcp_flags,
        "network_protocol": "IPv4",
        "transport_protocol": transport_protocol,
        "application_protocol": app_protocol,
        "ws_payload": payload_json,
    }
    print(json.dumps(tcp_packet), flush=True)
