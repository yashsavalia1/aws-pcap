import Layout from "../components/Layout";
import Chart from "../components/Chart";
import { Packet } from "../../types/Packet";
import { useEffect, useState } from "react";
import useWebSocket from "react-use-websocket";

export default function LatencyAnalytics() {

  const [packets, setPackets] = useState<Packet[]>([]);

  const { lastJsonMessage } = useWebSocket<Packet>(`ws://${window.location.host}/api/ws/packets`)

  useEffect(() => {
    if (lastJsonMessage) {
      setPackets((prevPackets) => [lastJsonMessage, ...prevPackets]);
    }
  }, [lastJsonMessage]);

  return (
    <div>
      <title>AWS Packet Capturing | Latency Analytics</title>
      <Layout>
        <div className="h-screen p-6 flex flex-col gap-4">
          <div className="font-bold text-2xl">Latency Analytics</div>
          <div className="flex flex-wrap">
            <div className="w-1/2 p-3">
              <div className="card w-full max-w-full h-full p-6">
                <Chart title="chart 1" data={packets.map(p => Date.parse(p.timestamp) - Date.parse(p.stock_data.timestamp))} />
              </div>
            </div>
            <div className="w-1/2 p-3">
              <div className="card w-full max-w-full h-full p-6">
                <Chart title="chart 2" data={[]} />
              </div>
            </div>

            <div className="w-1/2 p-3">
              <div className="card w-full max-w-full h-full p-6">
                <Chart title="chart 3" data={[]} />
              </div>
            </div>
            <div className="w-1/2 p-3">
              <div className="card w-full max-w-full h-full p-6">
                <Chart title="chart 4" data={[]} />
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </div>
  );
}
