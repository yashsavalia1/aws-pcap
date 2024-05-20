package main

import (
	"bufio"
	"bytes"
	"fmt"
	"net/http"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	wsparse "github.com/usnistgov/ndntdump/websocket"
)

func getTCPPacket(packet gopacket.Packet) *TCPPacket {
	innerPacket := getInnerPacket(packet)
	if innerPacket == nil {
		return nil
	}

	var (
		networkProtocol, transportProtocol, applicationProtocol, tcpFlags string
		length                                                            uint16
	)

	if innerPacket.NetworkLayer() != nil {
		networkProtocol = innerPacket.NetworkLayer().LayerType().String()
		if innerPacket.NetworkLayer().LayerType() == layers.LayerTypeIPv4 {
			length = innerPacket.NetworkLayer().(*layers.IPv4).Length
		} else if innerPacket.NetworkLayer().LayerType() == layers.LayerTypeIPv6 {
			length = innerPacket.NetworkLayer().(*layers.IPv6).Length
		}
	}
	if innerPacket.TransportLayer() != nil {
		transportProtocol = innerPacket.TransportLayer().LayerType().String()

		if innerPacket.TransportLayer().LayerType() == layers.LayerTypeTCP {
			tcpLayer := innerPacket.TransportLayer().(*layers.TCP)
			tcpFlags = getTCPFlags(tcpLayer)
		}
	}

	if innerPacket.ApplicationLayer() != nil {
		appLayer := innerPacket.ApplicationLayer()
		applicationProtocol = getApplicationProtocol(appLayer)
	}

	return &TCPPacket{
		Timestamp:           packet.Metadata().Timestamp.String(),
		Source:              innerPacket.NetworkLayer().NetworkFlow().Src().String(),
		Destination:         innerPacket.NetworkLayer().NetworkFlow().Dst().String(),
		Length:              length,
		Data:                innerPacket.Data(),
		NetworkProtocol:     networkProtocol,
		TransportProtocol:   transportProtocol,
		TCPFlags:            tcpFlags,
		ApplicationProtocol: applicationProtocol,
	}
}

func getInnerPacket(packet gopacket.Packet) gopacket.Packet {
	var vxlanLayer gopacket.Layer
	for _, layer := range packet.Layers() {
		if layer.LayerType() == layers.LayerTypeVXLAN {
			vxlanLayer = layer
			break
		}
	}
	if vxlanLayer == nil {
		return nil
	}
	return gopacket.NewPacket(vxlanLayer.LayerPayload(), layers.LayerTypeEthernet, gopacket.Default)
}

func getTCPFlags(tcpLayer *layers.TCP) string {
	var flags []string
	if tcpLayer.FIN {
		flags = append(flags, "FIN")
	}
	if tcpLayer.SYN {
		flags = append(flags, "SYN")
	}
	if tcpLayer.RST {
		flags = append(flags, "RST")
	}
	if tcpLayer.PSH {
		flags = append(flags, "PSH")
	}
	if tcpLayer.ACK {
		flags = append(flags, "ACK")
	}
	if tcpLayer.URG {
		flags = append(flags, "URG")
	}
	if tcpLayer.ECE {
		flags = append(flags, "ECE")
	}
	if tcpLayer.CWR {
		flags = append(flags, "CWR")
	}
	return fmt.Sprint(flags)
}

func getApplicationProtocol(appLayer gopacket.ApplicationLayer) string {
	if appLayer == nil {
		return ""
	}
	payload := appLayer.Payload()

	// parse http request
	_, err := http.ReadRequest(bufio.NewReader(bytes.NewReader(payload)))
	if err == nil {
		return "HTTP"
	}

	// parse http response
	_, err = http.ReadResponse(bufio.NewReader(bytes.NewReader(payload)), nil)
	if err == nil {
		return "HTTP"
	}

	//parse websocket request
	_, err = wsparse.ExtractBinaryFrames(payload)
	if err == nil {
		return "WebSocket"
	}

	return ""
}
