import Image from "next/image";
import { Inter } from "next/font/google";
import Layout from "@/components/Layout";

const inter = Inter({ subsets: ["latin"] });

export default function PacketExplorer() {
  return (
    <div className={inter.className}>
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
                    <tr>
                      <th>1</th>
                      <td>Cy Ganderton</td>
                      <td>Quality Control Specialist</td>
                      <td>Blue</td>
                      <td>Blue</td>
                      <td>Blue</td>
                      <td>Blue</td>
                      <td>Blue</td>
                      <td>Blue</td>
                    </tr>
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
