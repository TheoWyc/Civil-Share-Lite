import express from "express";
import { createServer } from "http";
import { Server } from "socket.io";

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
    cors: { 
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// Middleware CORS pour l'API REST
app.use((req, res, next) => {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    res.header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
    next();
});

app.use(express.json());

app.get("/health", (req, res) => {
    console.log("✅ Health check appelé");
    res.json({ status: "ok", timestamp: new Date().toISOString() });
});

app.post("/announcements", (req, res) => {
    const announcement = req.body;
    console.log("📢 Nouvelle annonce:", announcement);
    io.emit("new_announcement", announcement);
    res.json({ message: "Annonce créée", data: announcement });
});

io.on("connection", (socket) => {
    console.log("🔌 Un utilisateur est connecté !");
});

const PORT = 8000;
httpServer.listen(PORT, "0.0.0.0", () => {
    console.log(`✅ Backend lancé sur http://0.0.0.0:${PORT}`);
});