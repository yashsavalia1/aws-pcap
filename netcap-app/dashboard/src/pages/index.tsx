import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import ReactFlow, { Background, Edge, Handle, Node, Position } from "reactflow";
import "reactflow/dist/style.css";
import { Trader } from "../../types/Trader";

function TraderNode({ data }: { data: Trader }) {
  return (
    <div>
      <div className="popover">
        <label
          className="popover-trigger card bg-slate-700 p-5 cursor-pointer"
          tabIndex={0}
        >
          {data.name}
        </label>
        <div className="popover-content" tabIndex={0}>
          <div className="popover-arrow"></div>
          <div className="p-4 text-sm">Instance ID: {data.id}</div>
        </div>
      </div>
      <Handle type="target" position={Position.Left} />
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

export default function Home() {
  const [traders, setTraders] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    (async () => {
      const res = await fetch("/api/traders");
      const data: { trader: Trader; monitor: Trader } = await res.json();
      setTraders([
        {
          id: "1",
          type: "custom",
          data: data.trader,
          position: { x: 300, y: 450 },
        },
        {
          id: "2",
          type: "custom",
          data: data.monitor,
          position: { x: 900, y: 450 },
        },
      ]);
      setEdges([
        {
          id: "e1-2",
          source: "1",
          target: "2",
          animated: true,
        },
      ]);
    })();
  }, []);

  return (
    <div>
      <Layout>
        <div className="h-screen p-6">
          <div className="card h-full max-w-full">
            <div className="w-full h-full flex flex-col justify-center items-center gap-4">
              <ReactFlow
                nodeTypes={{ custom: TraderNode }}
                nodes={traders}
                edges={edges}
                proOptions={{ hideAttribution: true }}
              >
                <Background color="#fff" gap={16} size={1} />
              </ReactFlow>
            </div>
          </div>
        </div>
      </Layout>
    </div>
  );
}
