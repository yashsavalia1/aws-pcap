import express from "express";
import type { Express } from "express";
import ViteExpress from "vite-express";
import { AddressInfo } from "net";
//import { PrismaClient } from "@prisma/client";
import expressWs from "express-ws"
import sqlite3 from "sqlite3";
import { exec } from "child_process";
import ws from "ws";
import { setIntervalAsync, clearIntervalAsync } from "set-interval-async";
import { Packet } from "./types/Packet";

const app = express();
expressWs(app);
const router = express.Router() as expressWs.Router;

exec("sudo python3 ./packet_capture/requestGen.py", (error, stdout, stderr) => {
    if (error) {
        console.error(`Error executing command: ${error.message}`);
    }
});

// const prisma = new PrismaClient();

// router.get("/api/packet", async (req, res) => {
//    const packets = await prisma.tCPPacket.findMany();
//    res.json(packets);
//});

router.ws("/api/ws", async (ws: ws.WebSocket, req) => {
    console.log("Websocket connection established");
    let latestID = 0;
    const interval = setIntervalAsync(async () => {
        const db = new sqlite3.Database("./prisma/database.db");
        await new Promise<void>((resolve, reject) => {
            db.all<Packet>("SELECT * FROM TCPPacket WHERE id > ? ORDER BY id DESC LIMIT 50", [latestID], (err, rows) => {
                if (err) {
                    console.error(err);
                    reject(err);
                    return;
                }
                if (rows.length > 0) {
                    ws.send(JSON.stringify(rows));
                    latestID = rows[0].id;
                }
                resolve();
            });

        }).catch(() => {
            clearIntervalAsync(interval);
            ws.close()
        });
    }, 500);

    ws.on("close", () => clearIntervalAsync(interval));
    ws.on("message", (msg) => {
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
