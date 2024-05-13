import Layout from "../components/Layout";

export default function Home() {
  return (
    <div>
      <Layout>
        <div className="h-screen p-6">
          <div className="card h-full max-w-full">
            <div className="w-full h-full flex flex-col justify-center items-center gap-4">
              <div className="card bg-slate-700 w-min p-5">Trader</div>
              <div className="card bg-slate-700 w-min p-5">Trader</div>
              <div className="card bg-slate-700 w-min p-5">Trader</div>
            </div>
          </div>
        </div>
      </Layout>
    </div>
  );
}
