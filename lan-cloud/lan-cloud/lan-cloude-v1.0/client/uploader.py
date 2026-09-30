import hashlib, time
from pathlib import Path
import requests

def digest(path: Path):
    h=hashlib.sha256(); size=0
    with path.open("rb") as f:
        while chunk:=f.read(1024*1024): h.update(chunk); size+=len(chunk)
    return size,h.hexdigest()

def headers(identity): return {"X-Device-ID":identity["device_id"],"X-Device-Token":identity["token"]}

def server_files(server,identity):
    r=requests.get(server+"/files",headers=headers(identity),timeout=30); r.raise_for_status()
    return {x["rel_path"]:x for x in r.json().get("files",[])}

def upload_one(server,identity,path:Path,root:Path,retries=5,silent=False):
    rel=path.resolve().relative_to(root.resolve()).as_posix(); size,sha=digest(path)
    for attempt in range(retries):
        try:
            with path.open("rb") as f:
                r=requests.post(server+"/upload",headers=headers(identity),data={"relative_path":rel,"size":size,"sha256":sha,"mtime":path.stat().st_mtime},files={"file":(path.name,f)},timeout=(20,3600))
            r.raise_for_status(); return True
        except Exception:
            if attempt+1==retries: return False
            time.sleep(min(2**(attempt+1),32))
