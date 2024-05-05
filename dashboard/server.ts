import express from "express";
import type { Express } from "express";
import ViteExpress from "vite-express";
import { AddressInfo } from "net";
//import { PrismaClient } from "@prisma/client";
import expressWs from "express-ws"
import sqlite3 from "sqlite3";
import exec from "child_process";

const app = express();
expressWs(app);
const router = express.Router() as expressWs.Router;

// const prisma = new PrismaClient();

// router.get("/api/packet", async (req, res) => {
//    const packets = await prisma.tCPPacket.findMany();
//    res.json(packets);
//});

router.ws("/api/ws", async (ws, req) => {

    let latestTime = 0;
    setInterval(() => {
        const db = new sqlite3.Database("./prisma/database.db");
        db.all<{ timestamp: number }>("SELECT * FROM TCPPacket ORDER BY timestamp DESC LIMIT 50", (err, rows) => {
            if (err) {
                console.error(err);
                return;
            }
            rows.forEach((row) => {
                if (row.timestamp > latestTime) {
                    latestTime = row.timestamp;
                    ws.send(JSON.stringify(row));
                }
            });
        });
        db.close();
    }, 200);

    ws.on("message", async (msg) => {
        ws.send(msg);
    });
});

app.use(router);

const server = app.listen(80, "0.0.0.0", () => {
    const { address, port } = server.address() as AddressInfo;
    console.log(`Server running on http://localhost:${port}`);
});

ViteExpress.config({
    mode: process.argv.includes("--prod") ? "production" : "development",
    ignorePaths: (path) => path.includes("/api")
})
ViteExpress.bind(app, server);
