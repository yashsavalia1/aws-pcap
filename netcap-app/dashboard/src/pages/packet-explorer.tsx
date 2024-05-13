import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import useWebSocket from "react-use-websocket";
import { Packet } from "../../types/Packet";

export default function PacketExplorer() {

  const [packets, setPackets] = useState<Packet[]>([]);
  const [selectedPacket, setSelectedPacket] = useState<Packet | null>(null);

  const { lastJsonMessage } = useWebSocket<Packet>(`ws://${window.location.host}/api/ws/packets`)

  useEffect(() => {
    if (lastJsonMessage) {
      setPackets((prevPackets) => [lastJsonMessage, ...prevPackets]);
    }
  }, [lastJsonMessage]);

  return (
    <div>
      <title>AWS Packet Capturing | Packet Explorer</title>
      <Layout>
        <div className="h-screen p-6 flex flex-col gap-5 max-w-[100%-18rem]">
          <div className="card h-2/3 max-w-full p-6">
            <div className="w-full h-full flex flex-col items-center gap-4">
              <div className="w-full self-start">
                <div className="font-bold">Network Traffic</div>
                <span>
                  A list of all the packets being sent on the simulated trading
                  network.
                </span>
              </div>
              <div className="flex w-full overflow-x-auto">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Packet ID</th>
                      <th>Recorded Timestamp</th>
                      <th>Packet Length</th>
                      <th>Source IP</th>
                      <th>Destination IP</th>
                      <th>Network Protocol</th>
                      <th>IP Protocol</th>
                      <th>TCP Flags</th>
                      <th>Application Protocol</th>
                    </tr>
                  </thead>
                  <tbody>
                    {packets.map((packet, i) => (
                      <tr key={i} onClick={() => setSelectedPacket(packet)} className="hover:bg-gray-700 cursor-pointer">
                        <td>{i}</td>
                        <td>{packet.timestamp}</td>
                        <td>{packet.length}</td>
                        <td>{packet.source}</td>
                        <td>{packet.destination}</td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div className="h-1/3 flex max-w-full gap-5">
            <div className="card max-w-full h-full w-1/2 p-6">
              {selectedPacket && (
                <>
                  <div className="font-bold">Packet Details</div>
                  <div>
                    <div className="font-bold">Data:</div>
                    <div className="break-all overflow-clip h-48">{selectedPacket.data}</div>
                  </div>
                </>
              )
              }


            </div>
            <div className="card max-w-full h-full w-1/2 p-6">hi</div>
          </div>
        </div>
      </Layout>
    </div>
  );
}
