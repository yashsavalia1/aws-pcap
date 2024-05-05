import Layout from "../components/Layout";
import Chart from "../components/Chart";

export default function LatencyAnalytics() {
  return (
    <div>
      <title>AWS Packet Capturing | Latency Analytics</title>
      <Layout>
        <div className="h-screen p-6 flex flex-col gap-4">
          <div className="font-bold text-2xl">Latency Analytics</div>
          <div className="flex flex-wrap">
            <div className="w-1/2 p-3">
              <div className="card w-full max-w-full h-full p-6">
                <Chart title="chart 1" data1={[]} />
              </div>
            </div>
            <div className="w-1/2 p-3">
              <div className="card w-full max-w-full h-full p-6">
                <Chart title="chart 2" data1={[]} />
              </div>
            </div>

            <div className="w-1/2 p-3">
              <div className="card w-full max-w-full h-full p-6">
                <Chart title="chart 3" data1={[]} />
              </div>
            </div>
            <div className="w-1/2 p-3">
              <div className="card w-full max-w-full h-full p-6">
                <Chart title="chart 4" data1={[]} />
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </div>
  );
}
