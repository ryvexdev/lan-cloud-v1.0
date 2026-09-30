import argparse, os, socket, time
from hashlib import sha256
from pathlib import Path
import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from vault import save,load,get_password,VAULT_PATH
from uploader import headers,upload_one,server_files,digest
from scanner import scan
console=Console()

def register(server):
    name=Prompt.ask("Device Name",default=socket.gethostname() or "DEVICE")
    with Progress(SpinnerColumn(),TextColumn("{task.description}"),transient=True,console=console) as p:
        t=p.add_task("Generating device identity...",total=None)
        p.update(t,description="Creating secure credentials...")
        registration_key=Prompt.ask("Registration Key",password=True)
        r=requests.post(server+"/register",data={"device_name":name,"registration_key":registration_key},timeout=30); r.raise_for_status(); data=r.json()
        p.update(t,description="Device registered")
    console.print(Panel.fit("[bold cyan]REGISTER DEVICE[/bold cyan]",border_style="cyan"))
    console.print(f"Device Name: {name}\nDevice ID: {data['device_id']}\n\n[bold yellow]Save this one-time token securely:[/bold yellow]\n{data['token']}")
    entered=Prompt.ask("Enter Token",password=True)
    if entered!=data["token"]: raise SystemExit("Token verification failed; revoke device and register again")
    password=get_password(confirm=True)
    save({"device_id":data["device_id"],"device_name":name,"token":entered},password)
    console.print("[green]✓ Device registered and encrypted vault saved.[/green]")

def identity(): return load(get_password())
def sync(server,folder,watch=False):
    root=Path(folder).expanduser().resolve(); ident=identity()
    while True:
        try:
            remote=server_files(server,ident)
            for path in scan(root):
                rel=path.relative_to(root).as_posix()
                try:
                    size,sha=digest(path); old=remote.get(rel)
                    if old and old["size"]==size and old["sha256"]==sha: continue
                    if not upload_one(server,ident,path,root):
                        console.print(f"[red]Upload failed after retries: {rel}[/red]")
                except Exception as exc:
                    console.print(f"[red]Upload failed: {rel} — {exc}[/red]")
        except Exception as exc:
            console.print(f"[red]Sync failed: {exc}[/red]")
        if not watch: break
        time.sleep(3)

def download_one(server,ident,relative_path,output):
    rel=Path(relative_path)
    if rel.is_absolute() or not rel.parts or any(part in ("", ".", "..") for part in rel.parts):
        raise ValueError("Invalid relative path")
    rel=Path(*rel.parts)
    remote=server_files(server,ident)
    meta=remote.get(rel.as_posix())
    if not meta:
        raise FileNotFoundError(f"Remote file not found: {rel.as_posix()}")
    expected_size=int(meta["size"])
    expected_sha=meta["sha256"].lower()
    root=Path(output).expanduser().resolve()
    out=(root / rel).resolve()
    if root != out and root not in out.parents:
        raise ValueError("Invalid output path")
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {out}")
    out.parent.mkdir(parents=True,exist_ok=True)
    tmp=out.with_name(out.name+".downloading")
    actual_size=0; h=sha256()
    try:
        r=requests.get(server+"/download",params={"relative_path":rel.as_posix()},headers=headers(ident),stream=True,timeout=300); r.raise_for_status()
        with tmp.open("wb") as f:
            for chunk in r.iter_content(1024*1024):
                if chunk:
                    f.write(chunk); h.update(chunk); actual_size += len(chunk)
        actual_sha=h.hexdigest()
        if actual_size != expected_size or actual_sha != expected_sha:
            raise ValueError(f"Download integrity validation failed: expected {expected_size} bytes/{expected_sha}, got {actual_size} bytes/{actual_sha}")
        try:
            os.link(tmp,out)
        except FileExistsError:
            raise FileExistsError(f"Refusing to overwrite existing file: {out}")
        finally:
            try: tmp.unlink()
            except FileNotFoundError: pass
    finally:
        try: tmp.unlink()
        except FileNotFoundError: pass
    return out

def listing(server):
    ident=identity(); r=requests.get(server+"/files",headers=headers(ident),timeout=30); r.raise_for_status()
    table=Table("File","Size","Uploaded")
    for f in r.json()["files"]: table.add_row(f["rel_path"],str(f["size"]),f["uploaded_at"])
    console.print(table)

def main():
    ap=argparse.ArgumentParser(description="Private LAN Cloud client")
    ap.add_argument("--server",required=True,help="Backend URL supplied at runtime")
    group=ap.add_mutually_exclusive_group()
    group.add_argument("--register",action="store_true"); group.add_argument("--sync",metavar="FOLDER"); group.add_argument("--watch",metavar="FOLDER")
    group.add_argument("--list",action="store_true"); group.add_argument("--download",metavar="RELATIVE_PATH"); group.add_argument("--delete",metavar="RELATIVE_PATH")
    ap.add_argument("--output",default=".")
    a=ap.parse_args(); server=a.server.rstrip("/")
    if a.register: register(server)
    elif a.sync: sync(server,a.sync)
    elif a.watch: sync(server,a.watch,True)
    elif a.list: listing(server)
    elif a.download:
        ident=identity(); out=download_one(server,ident,a.download,a.output)
        console.print(f"Downloaded: {out}")
    elif a.delete:
        ident=identity(); r=requests.delete(server+"/files",params={"relative_path":a.delete},headers=headers(ident),timeout=30); r.raise_for_status(); console.print("[green]File deleted[/green]")
if __name__=="__main__": main()
