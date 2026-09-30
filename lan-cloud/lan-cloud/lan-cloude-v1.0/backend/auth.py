import hashlib, hmac, secrets
from fastapi import Header, HTTPException, Depends
from .database import connect

def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def new_token() -> str:
    return secrets.token_urlsafe(32)

def authenticate(device_id: str = Header(..., alias="X-Device-ID"), token: str = Header(..., alias="X-Device-Token")):
    with connect() as c:
        row = c.execute("SELECT device_id,device_name,token_hash FROM devices WHERE device_id=?", (device_id,)).fetchone()
        if not row or not hmac.compare_digest(row["token_hash"], token_hash(token)):
            raise HTTPException(status_code=401, detail="Invalid device credentials")
        from datetime import datetime, timezone
        c.execute("UPDATE devices SET last_seen=? WHERE device_id=?", (datetime.now(timezone.utc).isoformat(), device_id))
    return dict(row)
