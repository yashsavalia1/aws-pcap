import { useEffect, useState } from "react";


const HexViewer = ({ data }: { data: string }) => {
  const hexBytes = data.match(/.{1,2}/g) || []; // Split hex data into pairs of characters
  const asciiBytes = hexBytes.map(byte => parseInt(byte, 16)); // Convert hex pairs to decimal
  const [selectedByte, setSelectedByte] = useState<number | null>(null);

  useEffect(() => {
    console.log(selectedByte);

  }, [selectedByte]);

  return (
    <div className="flex gap-8 w-full" style={{ fontFamily: "Fira Code" }}>
      <div className="flex gap-4">
        <div className="grid h-min" style={{ gridTemplateColumns: "repeat(16, minmax(0, 1fr))" }}>
          {hexBytes
            .map((pair, i) => (
              <div
                key={i}
                className="px-2"
                onMouseEnter={() => setSelectedByte(i)}
                onMouseLeave={() => setSelectedByte(null)}
              >
                <span className={`${selectedByte == i && "bg-blue-700"}`}>{pair}</span>
              </div>
            ))}
        </div>
      </div>
      <div className="flex gap-4">
        <div className="grid h-min w-full" style={{ gridTemplateColumns: "repeat(16, minmax(0, 1fr))" }}>
          {asciiBytes
            .map((byte, i) => (
              <div
                key={i}
                className={`${selectedByte == i && "bg-blue-700"}`}
                onMouseEnter={() => setSelectedByte(i)}
                onMouseLeave={() => setSelectedByte(null)}
              >
                {byte < 32 || byte > 126 ? "." : String.fromCharCode(byte)}
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default HexViewer;