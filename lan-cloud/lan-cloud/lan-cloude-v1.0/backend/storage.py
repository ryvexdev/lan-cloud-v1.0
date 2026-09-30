import hashlib, os
from pathlib import Path
from fastapi import HTTPException
ROOT = Path(__file__).resolve().parent.parent
STORAGE_ROOT = Path(os.environ.get("LAN_CLOUD_STORAGE", ROOT / "storage")).resolve()
STORAGE_ROOT.mkdir(parents=True, exist_ok=True)

def safe_rel(value: str) -> Path:
    if not value or "\\" in value or "\x00" in value or value.startswith(("/", "~")) or ":" in value:
        raise HTTPException(400, "Invalid relative path")
    p = Path(value)
    if p.is_absolute() or any(part in ("..", ".") for part in p.parts) or not p.parts:
        raise HTTPException(400, "Invalid relative path")
    return p

def device_root(device_id: str) -> Path:
    return (STORAGE_ROOT / device_id).resolve()

def target_for(device_id: str, rel: Path) -> Path:
    root = device_root(device_id)
    target = (root / rel).resolve()
    if target != root and root not in target.parents:
        raise HTTPException(400, "Invalid relative path")
    return target

def sha256_file(path: Path) -> tuple[int, str]:
    h=hashlib.sha256(); size=0
    with path.open("rb") as f:
        while chunk:=f.read(1024*1024):
            size += len(chunk); h.update(chunk)
    return size,h.hexdigest()
