package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	wsparse "github.com/usnistgov/ndntdump/websocket"
)

const (
	OpText = 0x81
)

func getTCPPacket(packet gopacket.Packet) *TCPPacket {
	innerPacket := getInnerPacket(packet)
	if innerPacket == nil {
		return nil
	}

	var (
		networkProtocol, transportProtocol, applicationProtocol, tcpFlags string
		length                                                            uint16
		stockData                                                         StockData
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
		appProtocol, data := getApplicationLayerData[StockData](appLayer)
		applicationProtocol = appProtocol
		if data != nil {
			stockData = *data
		}
	}

	return &TCPPacket{
		Timestamp:           packet.Metadata().Timestamp,
		Source:              innerPacket.NetworkLayer().NetworkFlow().Src().String(),
		Destination:         innerPacket.NetworkLayer().NetworkFlow().Dst().String(),
		Length:              length,
		Data:                innerPacket.Data(),
		NetworkProtocol:     networkProtocol,
		TransportProtocol:   transportProtocol,
		TCPFlags:            tcpFlags,
		ApplicationProtocol: applicationProtocol,
		StockData:           stockData,
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

func getApplicationLayerData[DataFormat any](appLayer gopacket.ApplicationLayer) (string, *DataFormat) {
	if appLayer == nil {
		return "", nil
	}
	payload := appLayer.Payload()

	// parse http request
	_, err := http.ReadRequest(bufio.NewReader(bytes.NewReader(payload)))
	if err == nil {
		return "HTTP", nil
	}

	// parse http response
	_, err = http.ReadResponse(bufio.NewReader(bytes.NewReader(payload)), nil)
	if err == nil {
		return "HTTP", nil
	}

	//parse websocket request
	frames, err := ExtractTextFrames(payload)
	if err == nil {
		for _, frame := range frames {
			frameData := frame.Payload
			if len(frameData) == 0 {
				continue
			}
			var jsonData DataFormat
			if err = json.Unmarshal(frameData, &jsonData); err == nil {
				return "WebSocket", &jsonData
			}
			continue
		}
		return "WebSocket", nil
	}

	return "", nil
}

func ExtractTextFrames(input []byte) (frames []wsparse.Frame, e error) {
	for len(input) > 0 {
		var f wsparse.Frame
		input, e = f.Decode(input)
		if e != nil {
			return
		}

		if f.FlagOp != wsparse.FlagFin|OpText {
			continue
		}

		f.Unmask()
		frames = append(frames, f)
	}
	return
}
