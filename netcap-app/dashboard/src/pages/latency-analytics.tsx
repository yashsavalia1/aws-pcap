import Layout from "../components/Layout";
import Chart from "../components/Chart";
import { Packet } from "../../types/Packet";
import { useEffect, useMemo, useState } from "react";
import useWebSocket from "react-use-websocket";
import { Duration, ZonedDateTime } from "@js-joda/core";

export default function LatencyAnalytics() {
  const [packets, setPackets] = useState<Packet[]>([]);
  const latency = useMemo(
    () =>
      packets
        .filter((p) => p.stock_data.id)
        .map(
          (p) =>
            Duration.between(
              ZonedDateTime.parse(p.stock_data.timestamp),
              ZonedDateTime.parse(p.timestamp)
            ).toNanos() / 1e6
        ),
    [packets]
  );

  const { lastJsonMessage } = useWebSocket<Packet>(
    `ws://${window.location.host}/api/ws/packets`
  );

  useEffect(() => {
    if (lastJsonMessage && lastJsonMessage.stock_data?.timestamp) {
      setPackets((prevPackets) =>
        [...prevPackets, lastJsonMessage].slice(-100)
      );
    }
  }, [lastJsonMessage]);

  return (
    <div>
      <title>AWS Packet Capturing | Latency Analytics</title>
      <Layout>
        <div className="h-screen p-6 flex flex-col gap-4">
          <div className="font-bold text-2xl">Latency Analytics</div>
          <div className="flex flex-wrap">
            <div className="card w-full max-w-full h-full p-6">
              <Chart title="Latency (ms)" data={latency} />
          <div>
            Average Latency: {latency.length && latency.reduce((p, c) => p + c) / latency.length} ms
          </div>
            </div>
          </div>
        </div>
      </Layout>
    </div>
  );
}
