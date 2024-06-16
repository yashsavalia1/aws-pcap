package main

import (
	"bufio"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"runtime"
	"strconv"
	"strings"
	"time"

	"github.com/dustin/go-broadcast"
	"github.com/google/gopacket"        // for packet parsing
	"github.com/google/gopacket/pcap"   // for recieving packets
	"github.com/google/gopacket/pcapgo" // for writing pcap files
	"github.com/gorilla/websocket"
	tlsdecrypt "github.com/kiosk404/tls-decrypt/tls"
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

type PySharkPacket struct {
	Source            string                 `json:"source_ip"`
	Destination       string                 `json:"dest_ip"`
	TimeStamp         string                 `json:"timestamp"`
	RawPacket         string                 `json:"raw_packet"`
	NetworkProtocol   string                 `json:"network_protocol"`
	TransportProtocol string                 `json:"transport_protocol"`
	TCPFlags          []string               `json:"tcp_flags"`
	AppProtocol       string                 `json:"application_protocol"`
	WSPayload         map[string]interface{} `json:"ws_payload"`
	Length            uint16                 `json:"length"`
}

type TCPPacket struct {
	ID                  uint      `json:"id" gorm:"primarykey"`
	Timestamp           time.Time `json:"timestamp" gorm:"index"`
	Source              string    `json:"source"`
	Destination         string    `json:"destination"`
	Length              uint16    `json:"length"`
	Data                ByteSlice `json:"data"`
	NetworkProtocol     string    `json:"network_protocol"`
	TransportProtocol   string    `json:"transport_protocol"`
	TCPFlags            string    `json:"tcp_flags"`
	ApplicationProtocol string    `json:"application_protocol"`
	StockData           StockData `json:"stock_data" gorm:"-:all"`
}

type StockData struct {
	ID        string  `json:"id"`
	Symbol    string  `json:"symbol"`
	Price     float64 `json:"price"`
	Timestamp string  `json:"timestamp"`
}

type BinanceData struct {
	EventType        string `json:"e"`
	EventTime        uint64 `json:"E"`
	Symbol           string `json:"s"`
	AggregateTradeID uint64 `json:"a"`
	Price            string `json:"p"`
	Quantity         string `json:"q"`
	FirstTradeID     uint64 `json:"f"`
	LastTradeID      uint64 `json:"l"`
	TradeTime        uint64 `json:"T"`
	Maker            bool   `json:"m"`
}

type BitStamp struct {
	Data struct {
		ID             uint64  `json:"id"`
		TimeStamp      string  `json:"timestamp"`
		Amount         float64 `json:"amount"`
		AmountString   string  `json:"amount_str"`
		Price          float64 `json:"price"`
		PriceString    string  `json:"price_str"`
		Type           int     `json:"type"`
		MicroTimeStamp string  `json:"microtimestamp"`
		BuyID          uint64  `json:"buy_order_id"`
		SellID         uint64  `json:"sell_order_id"`
	} `json:"data"`
	Channel string `json:"channel"`
	Event   string `json:"event"`
}

type TLSSession struct {
	ClientHello *[]byte
	ServerHello *[]byte
	TlsStream   *tlsdecrypt.TLSStream
}

func (TCPPacket) TableName() string {
	return "TCPPacket"
}

var (
	db             *gorm.DB
	upgrader              = websocket.Upgrader{}
	b                     = broadcast.NewBroadcaster(1000)
	hostSessions          = map[string]TLSSession{}
	keyLogFilePath string = "keylog.txt"
)

func init() {
	// create database
	initDB, err := gorm.Open(sqlite.Open("./database.db"), &gorm.Config{AllowGlobalUpdate: true})
	if err != nil {
		panic(err)
	}
	if err = initDB.AutoMigrate(&TCPPacket{}); err != nil {
		panic(err)
	}
	if err = initDB.Delete(&TCPPacket{}).Error; err != nil {
		panic(err)
	}
	db = initDB
}

func main() {
	// go capturePackets()
	go pysharkCapture()
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

	api.POST("/ssl-keys", func(c echo.Context) error {
		file, err := c.FormFile("file")
		if err != nil {
			return c.JSON(http.StatusBadRequest, err)
		}
		src, err := file.Open()
		if err != nil {
			return c.JSON(http.StatusInternalServerError, err)
		}
		defer src.Close()

		// copy to new file
		dst, err := os.Create(keyLogFilePath)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, err)
		}
		defer dst.Close()

		if _, err = io.Copy(dst, src); err != nil {
			return c.JSON(http.StatusInternalServerError, err)
		}

		return c.String(http.StatusOK, "File uploaded")
	})

	e.Logger.Fatal(e.Start("0.0.0.0:80"))
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
	// dev := getDevice()
	// fmt.Println(dev)
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

func pysharkCapture() {
	cmd := exec.Command("python3", "pyshark_live.py")
	if runtime.GOOS == "windows" {
		cmd = exec.Command("python", "pyshark_live.py")
	}

	stdout, err := cmd.StdoutPipe()
	if err != nil {
		panic(err)
	}

	scanner := bufio.NewScanner(stdout)
	go func() {
		for scanner.Scan() {
			data := scanner.Text()
			var pySharkPacket PySharkPacket
			if err := json.Unmarshal([]byte(data), &pySharkPacket); err != nil {
				fmt.Println(err)
				continue
			}
			parts := strings.Split(pySharkPacket.TimeStamp, ".")
			if len(parts) != 2 {
				fmt.Println("Invalid timestamp")
				continue
			}
			decimal, err := strconv.ParseInt(parts[0], 10, 0)
			if err != nil {
				fmt.Println(err)
				continue
			}

			frac, err := strconv.ParseInt(parts[1], 10, 0)
			if err != nil {
				fmt.Println(err)
				continue
			}
			binanceData := BinanceData{}
			jsonData, err := json.Marshal(pySharkPacket.WSPayload)
			if err != nil {
				fmt.Println(err)
				continue
			}
			if err := json.Unmarshal(jsonData, &binanceData); err != nil {
				fmt.Println(err)
				continue
			}

			price, err := strconv.ParseFloat(binanceData.Price, 64)
			if err != nil {
				fmt.Println(err)
				continue
			}

			tcpPacket := &TCPPacket{
				Timestamp:           time.Unix(decimal, frac),
				Source:              pySharkPacket.Source,
				Destination:         pySharkPacket.Destination,
				Length:              uint16(len(pySharkPacket.RawPacket)),
				Data:                ByteSlice(pySharkPacket.RawPacket),
				NetworkProtocol:     pySharkPacket.NetworkProtocol,
				TransportProtocol:   pySharkPacket.TransportProtocol,
				ApplicationProtocol: pySharkPacket.AppProtocol,
				TCPFlags:            fmt.Sprint(pySharkPacket.TCPFlags),
				StockData: StockData{
					ID:        fmt.Sprint(binanceData.AggregateTradeID),
					Symbol:    binanceData.Symbol,
					Price:     price,
					Timestamp: strconv.FormatUint(binanceData.TradeTime, 10),
				},
			}

			b.Submit(tcpPacket)
		}
	}()

	if err := cmd.Start(); err != nil {
		panic(err)
	}
	if err := cmd.Wait(); err != nil {
		panic(err)
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
