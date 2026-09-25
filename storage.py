"""
Einfache SQLite-Speicherung der erkannten Trades, damit
Duplikate erkannt und ein Verlauf gefuehrt werden kann.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "trades.db"


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_label TEXT,
            token TEXT,
            usd_value REAL,
            tx_hash TEXT UNIQUE,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def trade_exists(tx_hash: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT 1 FROM trades WHERE tx_hash = ?", (tx_hash,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


def save_trade(wallet_label: str, token: str, usd_value: float,
                tx_hash: str, timestamp: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR IGNORE INTO trades (wallet_label, token, usd_value, tx_hash, timestamp) "
        "VALUES (?, ?, ?, ?, ?)",
        (wallet_label, token, usd_value, tx_hash, timestamp),
    )
    conn.commit()
    conn.close()


def get_recent_trades(hours: int = 24) -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        "SELECT * FROM trades WHERE timestamp >= datetime('now', ?)",
        (f"-{hours} hours",),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
