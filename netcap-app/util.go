package main

import (
	"encoding/binary"
)

func HasTLSRecords(payload []byte) bool {
	if len(payload) < 5 {
		// Minimum TLS record header length is 5 bytes
		return false
	}

	// Check if the first byte is a valid TLS record type
	switch payload[0] {
	case 0x14, 0x15, 0x16, 0x17:
		break
	default:
		return false
	}

	// Check if the version is valid
	if binary.BigEndian.Uint16(payload[1:3]) < 0x0301 || binary.BigEndian.Uint16(payload[1:3]) > 0x0304 {
		return false
	}

	// Check if the length is valid
	if len(payload) < int(binary.BigEndian.Uint16(payload[3:5]))+5 {
		return false
	}

	return true
}
