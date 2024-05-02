import Image from "next/image";
import { Inter } from "next/font/google";
import Layout from "@/components/Layout";

const inter = Inter({ subsets: ["latin"] });

export default function Home() {
  return (
    <div className={inter.className}>
      <title>AWS Packet Capturing | Home</title>
      <Layout>
        <div className="h-screen p-6">
          <div className="card h-full max-w-full">
            hi
          </div>
        </div>
      </Layout>
    </div>
  );
}
