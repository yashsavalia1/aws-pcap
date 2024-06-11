package main

import (
	"encoding/binary"
)

func HasTLSRecords(payload []byte) bool {
	if len(payload) < 5 {
		// Minimum TLS record header length is 5 bytes
		return false
	}

	for {
		if len(payload) < 5 {
			// Not enough data for the next record header
			return false
		}

		// Check the record header format
		recordType := payload[0]
		recordVersion := binary.BigEndian.Uint16(payload[1:3])
		recordLength := int(binary.BigEndian.Uint16(payload[3:5]))

		if recordType != 0x16 && recordType != 0x17 { // Handshake or Application Data
			// Not a valid TLS record type
			return false
		}

		if recordVersion != 0x0301 && recordVersion != 0x0302 && recordVersion != 0x0303 {
			// Not a valid TLS version (TLS 1.0, 1.1, or 1.2)
			return false
		}

		if recordLength > len(payload)-5 {
			// Not enough data for the record body
			return false
		}

		// This looks like a valid TLS record header
		payload = payload[5+recordLength:]
		if len(payload) < 5 {
			// No more records
			return true
		}
	}
}
