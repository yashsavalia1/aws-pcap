import time
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
    layers: List[BaseLayer] = packet.layers
    for i, layer in enumerate(layers):
        if layer.layer_name == "vxlan":
            layers = layers[i + 1 :]
            break

    ip_layers = packet.get_multiple_layers("ip")
    if len(ip_layers) == 0:
        ip_layers = packet.get_multiple_layers("ipv6")

    ip_layer = ip_layers[-1]

    src = ip_layer.src
    dst = ip_layer.dst

    tcp_flags = int_to_tcp_flags(int(packet.tcp.flags, 16))

    app_protocol = ""
    if 'http' in packet:
        app_protocol = "http"

    # Check if the packet contains WebSocket layer
    payload_json = {}
    if "websocket" in packet:
        app_protocol = "websocket"
        # The payload in WebSocket can be found in different fields depending on the frame type
        if hasattr(packet.websocket, "payload"):
            websocket_payload = packet.websocket.payload
            if hasattr(websocket_payload, "text"):
                payload_json = json.loads(websocket_payload.text)

    tcp_packet = {
        "timestamp": packet.sniff_timestamp,
        "source": src,
        "destination": dst,
        "length": packet.length,
        "data": packet.get_raw_packet().hex(),
        "network_protocol": "ip",
        "transport_protocol": "tcp",
        "tcp_flags": tcp_flags,
        "application_protocol": app_protocol,
        "stock_data": payload_json,
    }
    print(json.dumps(tcp_packet, indent=4), flush=True)

