/*
  Hardcoded Chat Relay with Safety Gates
  - Rooms
  - Two lanes: LIVE (SAFE only) and PENDING (UNRATED only)
  - Basic rate limit per connection
  - Ring buffers for late joiners
*/
const http = require("http");
const WebSocket = require("ws");
const crypto = require("crypto");

const PORT = process.env.PORT || 8787;

// --- Hardcoded policy knobs (adjust once, then treat as invariant) ---
const MAX_MSG_BYTES = 64 * 1024;
const RATE_LIMIT_WINDOW_MS = 1000;
const RATE_LIMIT_MAX_EVENTS = 120; // per client per second (points get batched!)
const RING_SAFE_MAX = 400;         // per room
const RING_PENDING_MAX = 250;      // per room
const ALLOW_UNRATED_TO_PUBLIC = false; // DO NOT FLIP unless private/test rooms

// roomId -> { live:Set(ws), pending:Set(ws), safeRing:[], pendingRing:[] }
const rooms = new Map();

function getRoom(roomId) {
  let r = rooms.get(roomId);
  if (!r) {
    r = {
      live: new Set(),
      pending: new Set(),
      safeRing: [],
      pendingRing: [],
    };
    rooms.set(roomId, r);
  }
  return r;
}

function pushRing(arr, max, item) {
  arr.push(item);
  if (arr.length > max) arr.splice(0, arr.length - max);
}

function nowMs() { return Date.now(); }
function uid() { return crypto.randomBytes(8).toString("hex"); }

function safeJsonParse(s) {
  try { return JSON.parse(s); } catch { return null; }
}

function send(ws, obj) {
  const data = JSON.stringify(obj);
  if (Buffer.byteLength(data, "utf8") > MAX_MSG_BYTES) return;
  if (ws.readyState === WebSocket.OPEN) ws.send(data);
}

function broadcast(set, obj) {
  for (const ws of set) send(ws, obj);
}

// Optional: plug in your real moderation/classifier here.
// For now: accept client-provided rating_state ONLY for SAFE promotion if you trust server-side checks.
// Recommended: server decides rating_state, clients can only *suggest*.
function classify(event) {
  // Hardcode minimal: if client says SAFE, accept; otherwise keep UNRATED.
  // Replace this with real moderation later.
  const rs = event.rating_state;
  if (rs === "SAFE") return "SAFE";
  if (rs === "NSFW") return "NSFW";
  if (rs === "BLOCKED") return "BLOCKED";
  return "UNRATED";
}

function laneFor(event, policy) {
  // policy: "public" or "private" (hardcode to public unless you explicitly create private rooms)
  const rating = event.rating_state;

  if (rating === "SAFE") return "live";
  if (rating === "UNRATED") {
    if (policy === "private") return "pending"; // still pending; UI can reveal in private if you want
    if (policy === "public") return ALLOW_UNRATED_TO_PUBLIC ? "live" : "pending";
  }
  return "drop";
}

const server = http.createServer((req, res) => {
  res.writeHead(200, {"content-type":"text/plain"});
  res.end("chat relay ok\n");
});

const wss = new WebSocket.Server({ server });

wss.on("connection", (ws) => {
  ws.id = uid();
  ws.roomId = null;
  ws.role = "live"; // or "pending"
  ws.policy = "public"; // hardcode; you can add per-room later

  ws._rl = { t0: nowMs(), n: 0 };

  function rateOk() {
    const t = nowMs();
    if (t - ws._rl.t0 > RATE_LIMIT_WINDOW_MS) {
      ws._rl.t0 = t;
      ws._rl.n = 0;
    }
    ws._rl.n++;
    return ws._rl.n <= RATE_LIMIT_MAX_EVENTS;
  }

  function join(roomId, role) {
    leave();
    ws.roomId = roomId;
    ws.role = role === "pending" ? "pending" : "live";

    const room = getRoom(roomId);
    if (ws.role === "pending") room.pending.add(ws);
    else room.live.add(ws);

    // Snapshot: SAFE always; pending only for pending role
    send(ws, { type:"snapshot", v:1, room:roomId, safe: room.safeRing, pending: ws.role==="pending" ? room.pendingRing : [] });
    send(ws, { type:"joined", v:1, room:roomId, role:ws.role, id:ws.id });
  }

  function leave() {
    if (!ws.roomId) return;
    const room = getRoom(ws.roomId);
    room.live.delete(ws);
    room.pending.delete(ws);
    ws.roomId = null;
  }

  ws.on("message", (buf) => {
    if (!rateOk()) return; // silently drop spam

    const str = buf.toString("utf8");
    if (Buffer.byteLength(str, "utf8") > MAX_MSG_BYTES) return;

    const msg = safeJsonParse(str);
    if (!msg || typeof msg !== "object") return;

    // Control messages
    if (msg.type === "join") {
      const room = String(msg.room || "").slice(0, 80);
      const role = msg.role === "pending" ? "pending" : "live";
      if (!room) return;
      join(room, role);
      return;
    }
    if (msg.type === "leave") {
      leave();
      return;
    }

    // Event messages must be in a room
    if (!ws.roomId) return;

    // Hardcoded envelope normalization
    const event = {
      v: 1,
      id: String(msg.id || uid()),
      room: ws.roomId,
      from: String(msg.from || ws.id),
      t: typeof msg.t === "number" ? msg.t : nowMs(),
      kind: msg.kind === "pict" ? "pict" : "text",
      data: msg.data && typeof msg.data === "object" ? msg.data : {},
      rating_state: "UNRATED",
    };

    // Server classification (replace later with real moderation)
    event.rating_state = classify(msg);

    // Decide lane
    const lane = laneFor(event, ws.policy);
    if (lane === "drop") return;

    const room = getRoom(ws.roomId);

    if (lane === "live") {
      pushRing(room.safeRing, RING_SAFE_MAX, event);
      broadcast(room.live, { type:"event", ...event });
      // Optional: live viewers never see pending
    } else if (lane === "pending") {
      pushRing(room.pendingRing, RING_PENDING_MAX, event);
      broadcast(room.pending, { type:"event", ...event });
      // Critical invariant: public live viewers DO NOT get this
    }
  });

  ws.on("close", () => {
    if (ws.roomId) {
      const room = getRoom(ws.roomId);
      room.live.delete(ws);
      room.pending.delete(ws);
    }
  });

  // minimal hello
  send(ws, { type:"hello", v:1, id: ws.id });
});

server.listen(PORT, () => {
  console.log(`chat relay listening on :${PORT}`);
});
