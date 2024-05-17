package main

import (
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"strings"

	"github.com/google/gopacket" // for packet parsing
	"github.com/google/gopacket/layers"
	"github.com/google/gopacket/pcap"   // for recieving packets
	"github.com/google/gopacket/pcapgo" // for writing pcap files
	"github.com/gorilla/websocket"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"github.com/manifoldco/promptui"
	_ "github.com/mattn/go-sqlite3" // for sqlite3
	godpi "github.com/mushorg/go-dpi"
	godpi_types "github.com/mushorg/go-dpi/types"
	"gitlab.engr.illinois.edu/ie421_high_frequency_trading_spring_2024/ie421_hft_spring_2024_group_02/group_02_project/netcap-app/dashboard"
)

type ByteSlice []byte

func (b ByteSlice) MarshalJSON() ([]byte, error) {
	return json.Marshal(hex.EncodeToString(b))
}

type TCPPacket struct {
	Timestamp           string    `json:"timestamp"`
	Source              string    `json:"source"`
	Destination         string    `json:"destination"`
	Length              uint16    `json:"length"`
	Data                ByteSlice `json:"data"`
	NetworkProtocol     string    `json:"network_protocol"`
	TransportProtocol   string    `json:"transport_protocol"`
	TCPFlags            string    `json:"tcp_flags"`
	ApplicationProtocol string    `json:"application_protocol"`
}

var (
	upgrader  = websocket.Upgrader{}
	packetsCh chan gopacket.Packet
)

func init() {
	godpi.Initialize()

	// create database
	db, err := sql.Open("sqlite3", "./prisma/database.db")
	if err != nil {
		fmt.Println(err)
	}
	defer db.Close()

	if _, err := db.Exec(`DROP TABLE IF EXISTS TCPPacket`); err != nil {
		panic(err)
	}

	if _, err := db.Exec(`CREATE TABLE TCPPacket (
		"id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		"timestamp" DATETIME NOT NULL,
		"source" TEXT NOT NULL,
		"destination" TEXT NOT NULL,
		"length" INTEGER NOT NULL,
		"data" BLOB NOT NULL
		)`); err != nil {
		panic(err)
	}
	if _, err := db.Exec(`CREATE INDEX idx_TCPPacket_timestamp ON TCPPacket (timestamp)`); err != nil {
		panic(err)
	}
}

func main() {
	go capturePackets()
	setupEchoServer()
}

func setupEchoServer() {
	e := echo.New()
	e.Use(middleware.LoggerWithConfig(middleware.LoggerConfig{
		Format: "${time_rfc3339} ${method} ${uri} ${status}\n",
		Skipper: func(c echo.Context) bool {
			return !strings.Contains(c.Request().RequestURI, "/api")
		},
	}))

	dashboard.RegisterHandlers(e)

	api := e.Group("/api")

	api.GET("/hello", func(c echo.Context) error {
		return c.String(http.StatusOK, "Hello, World!")
	})

	api.GET("/ws/packets", handleWebSocketConnection)

	e.Logger.Fatal(e.Start("0.0.0.0:3000"))
}

func handleWebSocketConnection(c echo.Context) error {
	ws, err := upgrader.Upgrade(c.Response(), c.Request(), nil)
	if err != nil {
		c.Logger().Error(err)
		return err
	}
	defer ws.Close()

	//TODO: get packets from sqlite

	go func() {
		for packet := range packetsCh {
			innerPacket := getInnerPacket(packet)
			if innerPacket == nil {
				continue
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

			applicationProtocol = string(getApplicationProtocol(innerPacket))

			jsonPacket := TCPPacket{
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

			// Write
			if err := ws.WriteJSON(jsonPacket); err != nil {
				if websocket.IsUnexpectedCloseError(err, websocket.CloseNormalClosure, websocket.CloseGoingAway) {
					c.Logger().Error(err)
				}
				break
			}
		}
	}()

	for {
		_, _, err := ws.ReadMessage()
		if err != nil {
			// check if normal close
			if websocket.IsUnexpectedCloseError(err, websocket.CloseNormalClosure, websocket.CloseGoingAway) {
				c.Logger().Error(err)
				return err
			}
			break
		}
	}

	return nil
}

func capturePackets() {
	// get device for windows
	// ifs, _ := pcap.FindAllDevs()
	// var dev string
	// //var devices []string
	// for _, i := range ifs {
	// 	//devices = append(devices, i.Description)
	// 	if i.Description == "Intel(R) Wi-Fi 6 AX201 160MHz" {
	// 		dev = i.Name
	// 		break
	// 	}
	// }
	//dev = getDevice()
	// open device
	handle, err := pcap.OpenLive("ens5", 65535, false, pcap.BlockForever)
	if err != nil {
		panic(err)
	}
	if err := handle.SetBPFFilter("port 4789"); err != nil {
		panic(err)
	}
	packetSource := gopacket.NewPacketSource(handle, handle.LinkType())

	//handleSignalInterrupt(handle)

	// open pcap file
	f, _ := os.Create("test.pcap")
	defer f.Close()
	w := pcapgo.NewWriter(f)
	w.WriteFileHeader(65535, handle.LinkType())

	fmt.Println("Capturing packets...")
	packetsCh = packetSource.Packets()
	for packet := range packetsCh {
		//fmt.Println(packet.String())
		// insert packet to database
		insertPackets(packet)
		// write packet to pcap file
		w.WritePacket(packet.Metadata().CaptureInfo, packet.Data())
	}
}

func insertPackets(packet gopacket.Packet) {
	db, err := sql.Open("sqlite3", "./prisma/database.db")
	if err != nil {
		panic(err)
	}
	_, err = db.Exec("INSERT INTO TCPPacket (timestamp, source, destination, length, data) VALUES (?, ?, ?, ?, ?)",
		packet.Metadata().Timestamp,
		packet.NetworkLayer().NetworkFlow().Src().String(),
		packet.NetworkLayer().NetworkFlow().Dst().String(),
		len(packet.Data()),
		packet.Data())
	if err != nil {
		panic(err)
	}
	db.Close()
}

func handleSignalInterrupt(handle *pcap.Handle) {
	// handle ctrl+c
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	go func() {
		<-c
		stats, err := handle.Stats()
		if err != nil {
			panic(err)
		}
		fmt.Println(stats.PacketsReceived, "Packets received")
		fmt.Println(stats.PacketsDropped, "Dropped by kernel")
		fmt.Println(stats.PacketsIfDropped, "Dropped by interface")
		handle.Close()
		os.Exit(1)
	}()
}

//lint:ignore U1000 Ignore unused function
func getDevice() string {
	ifs, _ := pcap.FindAllDevs()
	var dev string
	var devices []string
	for _, i := range ifs {
		devices = append(devices, i.Description)
	}
	prompt := promptui.Select{
		Label: "Select a device",
		Items: devices,
	}
	_, result, err := prompt.Run()
	if err != nil {
		fmt.Println(err)
	}
	for _, i := range ifs {
		if i.Description == result {
			dev = i.Name
			break
		}
	}
	return dev
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

func getApplicationProtocol(packet gopacket.Packet) godpi_types.Protocol {
	// classify packet
	flow, _ := godpi.GetPacketFlow(packet)
	result := godpi.ClassifyFlow(flow)
	return result.Protocol
}
