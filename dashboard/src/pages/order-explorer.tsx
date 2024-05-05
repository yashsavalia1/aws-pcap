import Layout from "../components/Layout";

export default function OrderExplorer() {
  return (
    <div>
      <title>AWS Packet Capturing | Order Explorer</title>
      <Layout>
        <div className="h-screen p-6 flex flex-col gap-4">
          <div className="font-bold text-2xl">Order Explorer</div>
          <div className="h-full flex justify-stretch gap-5">
            <div className="card h-full w-full max-w-full p-6">
              <div>
                <div className="font-bold">Order Requests</div>
                <span className="text-sm">
                  A list of all the orders placed to the exchange
                </span>
              </div>
              <div className="flex w-full overflow-x-auto">
                <table className="table table-hover">
                  <thead>
                    <tr>
                      <th>Order ID</th>
                      <th>Trader ID</th>
                      <th>Time Sent</th>
                      <th>Time Processed</th>
                      <th>Packet Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <th>1</th>
                      <td>Cy Ganderton</td>
                      <td>Quality Control Specialist</td>
                      <td>Blue</td>
                      <td>
                        <button className="btn btn-sm btn-primary">View</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="card h-full w-full max-w-full p-6">
              <div>
                <div className="font-bold">Market Data</div>
                <span className="text-sm">Packets related to market data</span>
              </div>
              <div className="flex w-full overflow-x-auto">
                <table className="table table-hover">
                  <thead>
                    <tr>
                      <th>Ticker</th>
                      <th>Trader ID</th>
                      <th>Time Sent</th>
                      <th>Time Processed</th>
                      <th>Packet Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <th>1</th>
                      <td>Cy Ganderton</td>
                      <td>Quality Control Specialist</td>
                      <td>Blue</td>
                      <td>
                        <button className="btn btn-sm btn-primary">View</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </div>
  );
}
