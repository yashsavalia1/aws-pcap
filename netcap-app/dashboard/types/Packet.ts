export type Packet = {
  id: number;
  timestamp: string;
  length: number;
  source: string;
  destination: string;
  data: string;
  network_protocol: string;
  transport_protocol: string;
  tcp_flags: string;
  application_protocol: string;
  stock_data: StockData;
};

export type StockData = {
  id: string;
  symbol: string;
  price: number;
  timestamp: string;
};