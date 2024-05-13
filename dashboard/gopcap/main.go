package main

import (
	"database/sql"
	"fmt"
	"os"

	"net/http"

	"github.com/google/gopacket"        // for packet parsing
	"github.com/google/gopacket/pcap"   // for recieving packets
	"github.com/google/gopacket/pcapgo" // for writing pcap files
	"github.com/manifoldco/promptui"
	_ "github.com/mattn/go-sqlite3" // for sqlite3
)

func init() {
	db, err := sql.Open("sqlite3", "../prisma/database.db")
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

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "index.html")
	})
}

func main() {
	// get device for windows
	ifs, _ := pcap.FindAllDevs()
	var dev string
	//var devices []string
	for _, i := range ifs {
		//devices = append(devices, i.Description)
		if i.Description == "Intel(R) Wi-Fi 6 AX201 160MHz" {
			dev = i.Name
			break
		}
	}

	//dev = getDevice()

	// open device
	handle, err := pcap.OpenLive(dev, 65535, false, pcap.BlockForever)
	if err != nil {
		panic(err)
	}
	if err := handle.SetBPFFilter("not (arp or (ip proto \\icmp) or (port 123) or (port 22))"); err != nil {
		panic(err)
	}
	packetSource := gopacket.NewPacketSource(handle, handle.LinkType())

	// open pcap file
	f, _ := os.Create("test.pcap")
	defer f.Close()
	w := pcapgo.NewWriter(f)
	w.WriteFileHeader(65535, handle.LinkType())

	fmt.Println("Capturing packets...")
	for packet := range packetSource.Packets() {
		fmt.Println(packet.String())

		// insert packet to database
		insertPackets(packet)

		// write packet to pcap file
		w.WritePacket(packet.Metadata().CaptureInfo, packet.Data())
	}
}

func insertPackets(packet gopacket.Packet) {
	db, err := sql.Open("sqlite3", "../prisma/database.db")
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
