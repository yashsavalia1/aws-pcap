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

    let latestPrice = 0;
    setInterval(() => {
        const db = new sqlite3.Database("./prisma/database.db");
        db.all<{ price: number }>("SELECT * FROM trades ORDER BY time DESC LIMIT 1", (err, rows) => {
            if (err) {
                console.error(err);
                return;
            }
            rows.forEach((row) => {
                if (latestPrice === row["price"]) return;
                ws.send(JSON.stringify(row["price"]));
                latestPrice = row["price"];
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
