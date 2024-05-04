import os
import sys
import requests
import socketio
import json
import signal
from subprocess import Popen, PIPE, STDOUT
from dotenv import load_dotenv


def convert_to_ip(hexStr):
    # Split the string into four segments of two characters each
    segments = [hexStr[i:i+2] for i in range(0, len(hexStr), 2)]

    # Convert each segment from hexadecimal to decimal
    decimal_segments = [int(segment, 16) for segment in segments]

    # Convert the decimal segments to a string and join them with dots
    ip_address = ".".join(map(str, decimal_segments))

    return ip_address

if __name__ == "__main__":
    load_dotenv()

    p = Popen(
        "./netcap_upload",
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=STDOUT,
        universal_newlines=True)
    print("the process is running")
    print(os.environ.get("BACKEND_IP"))

    sio = socketio.Client()
    sio.connect(f"http://{os.environ.get('BACKEND_IP')}:3000")
    print(f"socket connected id: {sio.sid}")
    try:
        for line in iter(p.stdout.readline, ''):
            try:
                packetJson = json.loads(line)
                hexSrcIP = packetJson['raw_data'].get('ip_src_ip')
                hexDstIP = packetJson['raw_data'].get('ip_dst_ip')
                srcIP = None
                dstIP = None
                if hexSrcIP and hexDstIP:
                    srcIP = convert_to_ip(hexSrcIP)
                    dstIP = convert_to_ip(hexDstIP)

                res = requests.post(
                    "http://192.168.56.101:3000/rawPCAPService",
                    json=packetJson)

                sio.emit('activity', {
                    "source": srcIP,
                    "target": dstIP
                    })

                print(f"{res.status_code} - Packet Recorded: {srcIP} -> {dstIP}")

            except BaseException as e:
                print("Error parsing or sending the JSON, did you remember to remove root to libpcap? Try running \"sudo setcap cap_net_raw,cap_net_admin=eip ./netcap_upload\" then try again")
                print(e)
                sys.exit(1)
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()
        out, err = p.communicate()
        print(out)
        sys.exit(0)
