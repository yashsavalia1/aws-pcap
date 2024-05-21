package main

import (
	"fmt"

	wsparse "github.com/usnistgov/ndntdump/websocket"
)

// for packet parsing

// for recieving packets
// for writing pcap files

func main() {

	/* 	ch := make(chan int)
	   	ch <- 1
	   	ch <- 2
	   	ch <- 3
	   	ch <- 4

	   	for i := range ch {
	   		fmt.Println(i)
	   	} */

	// data := `{"hello": "World"}`
	// fmt.Println(string([]byte(data)))
	// var jsonData map[string]interface{}
	// json.Unmarshal([]byte(data), &jsonData)
	// fmt.Println(jsonData)

	rawbytes := []byte{129, 126, 0, 128, 123, 34, 105, 100, 34, 58, 32, 34, 52, 55, 102, 55, 100, 49, 55, 54, 45, 51, 101, 55, 50, 45, 52, 53, 97, 97, 45, 56, 53, 56, 57, 45, 97, 53, 49, 54, 53, 49, 101, 97, 49, 102, 101, 57, 34, 44, 32, 34, 115, 121, 109, 98, 111, 108, 34, 58, 32, 34, 70, 66, 34, 44, 32, 34, 112, 114, 105, 99, 101, 34, 58, 32, 52, 51, 57, 46, 56, 50, 44, 32, 34, 116, 105, 109, 101, 115, 116, 97, 109, 112, 34, 58, 32, 34, 50, 48, 50, 52, 45, 48, 53, 45, 50, 49, 84, 48, 53, 58, 53, 54, 58, 49, 54, 46, 52, 48, 56, 49, 50, 55, 43, 48, 48, 58, 48, 48, 34, 125}
	frames, err := ExtractTextFrames(rawbytes)
	if err != nil {
		fmt.Println(err)
	}
	for _, frame := range frames {
		fmt.Println(string(frame.Payload))
	}

	// for elem := range queue {
	// 	fmt.Println(elem)
	// }
	// go func() {
	// 	for i := range ch {
	// 		fmt.Println(i)
	// 	}
	// }()

	/* 	handle, err := pcap.OpenOffline("C:/Users/YashS/Desktop/session.pcap")
	   	if err != nil {
	   		panic(err)
	   	}
	   	defer handle.Close()

	   	//read in packets
	   	packetSource := gopacket.NewPacketSource(handle, handle.LinkType())
	   	for packet := range packetSource.Packets() {
	   		// get VXLAN layer

	   		var vxlanLayer gopacket.Layer
	   		for _, layer := range packet.Layers() {
	   			if layer.LayerType() == layers.LayerTypeVXLAN {
	   				vxlanLayer = layer
	   				break
	   			}
	   		}
	   		if vxlanLayer == nil {
	   			continue
	   		}

	   		innerPacket := gopacket.NewPacket(vxlanLayer.LayerPayload(), layers.LayerTypeEthernet, gopacket.Default)

	   		// src and dest ip addresses
	   		fmt.Println("Flow: ", innerPacket.NetworkLayer().NetworkFlow().String())
	   		// get inner packet length
	   		fmt.Println("Length: ", innerPacket.NetworkLayer().(*layers.IPv4).Length)
	   		// get tcp flags
	   		fmt.Println("Flags: ", innerPacket.TransportLayer().(*layers.TCP).SYN, innerPacket.TransportLayer().(*layers.TCP).ACK, innerPacket.TransportLayer().(*layers.TCP).FIN, innerPacket.TransportLayer().(*layers.TCP).RST)

	   		// fmt.Println("Data: ", innerPacket.Data())

	   		fmt.Println("---------------------------------")
	   	} */
}

func ExtractTextFrames(input []byte) (frames []wsparse.Frame, e error) {
	for len(input) > 0 {
		var f wsparse.Frame
		input, e = f.Decode(input)
		if e != nil {
			return
		}

		if f.FlagOp != wsparse.FlagFin|0x81 {
			continue
		}

		f.Unmask()
		frames = append(frames, f)
	}
	return
}
