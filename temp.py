import pyshark
import pyshark.capture
from pyshark.packet.packet import Packet
from  pyshark.packet.layers.xml_layer import XmlLayer


cap = pyshark.LiveCapture(interface=r"\Device\NPF_{FE25A37F-E1DA-4501-A03C-4BAD92808BFC}", bpf_filter='tcp port 80')

for p in cap.sniff_continuously():
    packet: Packet = p
    for layer in packet.layers:
        l: XmlLayer = layer
        print(l._layer_name)


