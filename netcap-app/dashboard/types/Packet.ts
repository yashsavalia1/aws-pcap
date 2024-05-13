export type Packet = {
    id: number;
    timestamp: string;
    length: number;
    source: string;
    destination: string;
    data: string;
    // networkProtocol: string;
    // ipProtocol: string;
    // tcpFlags: string;
    // applicationProtocol: string;
  };