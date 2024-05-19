package main

import (
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"strings"

	"github.com/dustin/go-broadcast"
	"github.com/google/gopacket"        // for packet parsing
	"github.com/google/gopacket/pcap"   // for recieving packets
	"github.com/google/gopacket/pcapgo" // for writing pcap files
	"github.com/gorilla/websocket"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"github.com/manifoldco/promptui"
	"gitlab.engr.illinois.edu/ie421_high_frequency_trading_spring_2024/ie421_hft_spring_2024_group_02/group_02_project/netcap-app/dashboard"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type ByteSlice []byte

func (b ByteSlice) MarshalJSON() ([]byte, error) {
	return json.Marshal(hex.EncodeToString(b))
}

type TCPPacket struct {
	gorm.Model
	Timestamp           string    `json:"timestamp" gorm:"index"`
	Source              string    `json:"source"`
	Destination         string    `json:"destination"`
	Length              uint16    `json:"length"`
	Data                ByteSlice `json:"data"`
	NetworkProtocol     string    `json:"network_protocol"`
	TransportProtocol   string    `json:"transport_protocol"`
	TCPFlags            string    `json:"tcp_flags"`
	ApplicationProtocol string    `json:"application_protocol"`
}

func (TCPPacket) TableName() string {
	return "TCPPacket"
}

var (
	upgrader = websocket.Upgrader{}
	db       *gorm.DB
	b        = broadcast.NewBroadcaster(1000)
)

func init() {
	// create database
	initDB, err := gorm.Open(sqlite.Open("./database.db"), &gorm.Config{})

	if err != nil {
		panic(err)
	}
	err = initDB.AutoMigrate(&TCPPacket{})
	if err != nil {
		panic(err)
	}
	db = initDB
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

	api.GET("/packets", func(c echo.Context) error {
		var packets []TCPPacket
		res := db.Find(&packets)
		if res.Error != nil {
			return c.JSON(http.StatusInternalServerError, res.Error)
		}
		return c.JSON(http.StatusOK, packets)
	})

	e.Logger.Fatal(e.Start("0.0.0.0:3000"))
}

func handleWebSocketConnection(c echo.Context) error {
	ws, err := upgrader.Upgrade(c.Response(), c.Request(), nil)
	if err != nil {
		c.Logger().Error(err)
		return err
	}
	defer ws.Close()

	packetCh := make(chan interface{})
	b.Register(packetCh)
	defer b.Unregister(packetCh)

	go func() {
		for packet := range packetCh {
			// Write
			if err := ws.WriteJSON(packet); err != nil {
				if websocket.IsUnexpectedCloseError(err, websocket.CloseNormalClosure, websocket.CloseGoingAway) {
					c.Logger().Error(err)
				}
				return
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
	for packet := range packetSource.Packets() {
		// write packet to pcap file
		w.WritePacket(packet.Metadata().CaptureInfo, packet.Data())

		// parse packet
		jsonPacket := getTCPPacket(packet)
		if jsonPacket == nil {
			continue
		}
		b.Submit(jsonPacket)

		// insert packet to database
		db.Create(jsonPacket)
	}
}

//lint:ignore U1000 Ignore unused function
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
