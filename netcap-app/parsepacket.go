package main

import (
	"bytes"
	"fmt"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
)

func getTCPPacket(packet gopacket.Packet) *TCPPacket {
	innerPacket := getInnerPacket(packet)
	if innerPacket == nil {
		return nil
	}

	var networkProtocol, transportProtocol, applicationProtocol, tcpFlags string
	if innerPacket.NetworkLayer() != nil {
		networkProtocol = innerPacket.NetworkLayer().LayerType().String()
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
		Timestamp:   packet.Metadata().Timestamp.String(),
		Source:      innerPacket.NetworkLayer().NetworkFlow().Src().String(),
		Destination: innerPacket.NetworkLayer().NetworkFlow().Dst().String(),
		// Need to watch: could be ipv6
		Length:              innerPacket.NetworkLayer().(*layers.IPv4).Length,
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
	payload := appLayer.Payload()

	// Check for HTTP request signature
	if bytes.HasPrefix(payload, []byte("GET ")) ||
		bytes.HasPrefix(payload, []byte("POST ")) ||
		bytes.HasPrefix(payload, []byte("PUT ")) ||
		bytes.HasPrefix(payload, []byte("DELETE ")) ||
		bytes.HasPrefix(payload, []byte("HEAD ")) ||
		bytes.HasPrefix(payload, []byte("OPTIONS ")) ||
		bytes.HasPrefix(payload, []byte("CONNECT ")) ||
		bytes.HasPrefix(payload, []byte("TRACE ")) {
		return "HTTP"
	}

	// Check for HTTP response signature
	if bytes.HasPrefix(payload, []byte("HTTP/")) {
		return "HTTP"
	}

	return ""
}
