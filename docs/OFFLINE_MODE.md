# MINEGUARD Offline-First Operation & Data Resilience
## SIH26025 — Zero-Loss Edge Safety Architecture

---

### 1. The Offline-First Imperative
Underground mining panels and remote open-cast sites suffer frequent telecommunication interruptions. MINEGUARD guarantees 100% core safety operation when completely severed from external WAN and cloud networks.

---

### 2. Dual-Layer Storage Architecture

#### Layer 1: Node-Level MicroSD Storage (ESP32)
- Each MINEGUARD node logs raw 1Hz sensor frames to onboard MicroSD flash memory.
- If LoRa RF is jammed or obstructed, frames remain safely archived for manual forensic extraction.

#### Layer 2: Gateway-Level SQLite Database (`edge_buffer.db`)
- The MINEGATE Raspberry Pi Zero 2 W writes every received LoRa packet into a local SQLite database with `sync_status = 'PENDING'`.
- All local safety actions (GPIO siren actuation, risk scoring, operator alerts) run against local SQLite storage.

---

### 3. Reconnection Synchronization Protocol
1. The `GatewaySyncService` daemon polls internet reachability every 15 seconds.
2. Upon active internet detection, it selects up to 50 `PENDING` records per batch.
3. Records are POSTed to the FastAPI / Cloud PostgreSQL sync endpoint.
4. Upon HTTP 200 confirmation, local SQLite marks records as `SYNCED`.
5. Queued remote notifications (Email / SMS) are processed in chronological order.
