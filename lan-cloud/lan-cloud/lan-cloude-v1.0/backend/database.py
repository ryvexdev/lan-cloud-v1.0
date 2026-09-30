import os, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("LAN_CLOUD_DB", ROOT / "database" / "cloud.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def connect():
    c = sqlite3.connect(DB_PATH, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    c.execute("PRAGMA journal_mode=WAL")
    return c

def init_db():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS devices(
          device_id TEXT PRIMARY KEY, device_name TEXT NOT NULL, token_hash TEXT NOT NULL,
          created_at TEXT NOT NULL, last_seen TEXT);
        CREATE TABLE IF NOT EXISTS files(
          id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT NOT NULL,
          rel_path TEXT NOT NULL, size INTEGER NOT NULL, sha256 TEXT NOT NULL,
          storage_path TEXT NOT NULL, mtime REAL NOT NULL, uploaded_at TEXT NOT NULL,
          UNIQUE(device_id, rel_path), FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE CASCADE);
        CREATE INDEX IF NOT EXISTS idx_files_device ON files(device_id);
        CREATE INDEX IF NOT EXISTS idx_files_hash ON files(sha256);
        ''')
