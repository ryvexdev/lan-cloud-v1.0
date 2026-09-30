import os
import uuid
import hmac
from datetime import datetime, timezone

from fastapi import APIRouter, Form, HTTPException, Depends
from .database import connect
from .auth import new_token, token_hash, authenticate

router = APIRouter()


@router.post("")
def register(
    device_name: str = Form(...),
    registration_key: str = Form(...),
):
    expected_key = os.environ.get("LAN_CLOUD_REGISTRATION_KEY")

    # Fail closed if the registration key is not configured.
    if not expected_key:
        raise HTTPException(
            status_code=503,
            detail="Device registration is disabled"
        )

    if not hmac.compare_digest(registration_key, expected_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid registration key"
        )

    name = device_name.strip()[:120]
    if not name:
        raise HTTPException(
            status_code=400,
            detail="Device name is required"
        )

    did = str(uuid.uuid4())
    token = new_token()
    now = datetime.now(timezone.utc).isoformat()

    with connect() as c:
        c.execute(
            "INSERT INTO devices VALUES(?,?,?,?,?)",
            (did, name, token_hash(token), now, now)
        )

    return {
        "device_id": did,
        "device_name": name,
        "token": token,
        "created_at": now,
    }


@router.get("")
def list_devices(
    dev=Depends(authenticate)
):
    return {
        "devices": [{
            "device_id": dev["device_id"],
            "device_name": dev["device_name"],
        }]
    }
