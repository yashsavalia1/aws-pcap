import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import useWebSocket from "react-use-websocket";
import { Packet } from "../../types/Packet";
import HexViewer from "../components/HexViewer";

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
        <input className="modal-state" id="modal-1" type="checkbox" />
        <div className="modal">
          <label className="modal-overlay" htmlFor="modal-1"></label>
          <div className="modal-content max-w-full flex flex-col gap-5">
            <label htmlFor="modal-1" className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</label>
            <div className="p-5">
              <HexViewer data={selectedPacket?.data || ""} />
            </div>
          </div>
        </div>
        
        <div className="h-screen p-6 flex flex-col gap-5">
          <div className="card h-full max-w-full p-6">
            <div className="w-full h-full flex flex-col items-center gap-4">
              <div className="w-full self-start">
                <div className="font-bold">Network Traffic</div>
                <span>
                  A list of all the packets being sent on the simulated trading
                  network.
                </span>
              </div>
              <div className="flex w-full overflow-x-auto">
                <table className="table table-compact over">
                  <thead>
                    <tr>
                      <th>Packet ID</th>
                      <th>Recorded Timestamp</th>
                      <th>Packet Length</th>
                      <th>Source IP</th>
                      <th>Destination IP</th>
                      <th>Network Protocol</th>
                      <th>Transport Protocol</th>
                      <th>TCP Flags</th>
                      <th>Application Protocol</th>
                    </tr>
                  </thead>
                  <tbody>
                    {packets.map((packet, i) => (
                      <tr
                        key={i}
                        onClick={() => {
                          setSelectedPacket(packet)
                          document.getElementById("modal-1")?.click()
                        }}
                        className="hover:bg-gray-700 cursor-pointer"
                      >
                        <td>{i}</td>
                        <td>{packet.timestamp}</td>
                        <td>{packet.length}</td>
                        <td>{packet.source}</td>
                        <td>{packet.destination}</td>
                        <td>{packet.network_protocol}</td>
                        <td>{packet.transport_protocol}</td>
                        <td>{packet.tcp_flags}</td>
                        <td>{packet.application_protocol}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </Layout >
    </div >
  );
}
