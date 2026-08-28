import sqlite3
import json
import time
from pathlib import Path
from gateway.config import GATEWAY_CONFIG

class EdgeLocalDB:
    def __init__(self, db_path=None):
        self.db_path = db_path or GATEWAY_CONFIG['db_path']
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS buffered_telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    payload TEXT NOT NULL,
                    sync_status TEXT DEFAULT 'PENDING',
                    created_at REAL NOT NULL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS buffered_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT,
                    risk_score REAL,
                    sync_status TEXT DEFAULT 'PENDING',
                    created_at REAL NOT NULL
                )
            ''')
            conn.commit()

    def insert_telemetry(self, node_id: str, payload: dict):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO buffered_telemetry (node_id, timestamp, payload, sync_status, created_at) VALUES (?, ?, ?, 'PENDING', ?)",
                (node_id, payload.get('timestamp', time.time()), json.dumps(payload), time.time())
            )
            conn.commit()

    def insert_alert(self, node_id: str, alert_data: dict):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO buffered_alerts (node_id, alert_type, severity, title, message, risk_score, sync_status, created_at) VALUES (?, ?, ?, ?, ?, ?, 'PENDING', ?)",
                (node_id, alert_data.get('alert_type'), alert_data.get('severity'), alert_data.get('title'), alert_data.get('message'), alert_data.get('risk_score', 0.0), time.time())
            )
            conn.commit()

    def get_pending_records(self, limit: int = 100):
        with self._get_conn() as conn:
            telemetry = conn.execute("SELECT * FROM buffered_telemetry WHERE sync_status = 'PENDING' LIMIT ?", (limit,)).fetchall()
            alerts = conn.execute("SELECT * FROM buffered_alerts WHERE sync_status = 'PENDING' LIMIT ?", (limit,)).fetchall()
            return {'telemetry': [dict(r) for r in telemetry], 'alerts': [dict(r) for r in alerts]}

    def mark_telemetry_synced(self, ids: list):
        if not ids:
            return
        with self._get_conn() as conn:
            placeholders = ','.join('?' * len(ids))
            conn.execute(f"UPDATE buffered_telemetry SET sync_status = 'SYNCED' WHERE id IN ({placeholders})", ids)
            conn.commit()
