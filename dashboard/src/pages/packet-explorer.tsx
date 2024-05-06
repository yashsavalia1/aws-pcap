import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import useWebSocket from "react-use-websocket";
import { Packet } from "../../types/Packet";

export default function PacketExplorer() {

  const [packets, setPackets] = useState<Packet[]>([]);

  const { lastJsonMessage } = useWebSocket<Packet[]>("ws://localhost/api/ws")

  useEffect(() => {
    if (lastJsonMessage) {
      setPackets((prevPackets) => [...lastJsonMessage, ...prevPackets]);
    }
  }, [lastJsonMessage]);

  return (
    <div>
      <title>AWS Packet Capturing | Packet Explorer</title>
      <Layout>
        <div className="h-screen p-6 flex flex-col gap-5">
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
                <table className="table table-hover">
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
                    {packets.map((packet) => (
                      <tr key={packet.id}>
                        <td>{packet.id}</td>
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
          <div className="h-1/3 flex justify-stretch gap-5">
            <div className="card h-full w-full max-w-full p-6">hi</div>
            <div className="card h-full w-full max-w-full p-6">hi</div>
          </div>
        </div>
      </Layout>
    </div>
  );
}
