#!/usr/bin/env python3
"""Consistent SQLite metadata backup. File payloads are backed up separately."""
import sqlite3, sys
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/"database"/"cloud.db"
out=Path(sys.argv[1]).expanduser() if len(sys.argv)>1 else ROOT/"database"/f"cloud-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db"
if not src.exists(): raise SystemExit("Database does not exist yet")
out.parent.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(src) as source, sqlite3.connect(out) as dest: source.backup(dest)
print(f"SQLite backup created: {out}")
