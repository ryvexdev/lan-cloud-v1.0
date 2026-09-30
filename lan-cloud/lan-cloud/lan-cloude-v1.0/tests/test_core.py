import hashlib, os, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from client.vault import save,load
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "client"))
from client.client import download_one
from backend.storage import safe_rel

def test_vault_roundtrip(tmp_path):
    p=tmp_path/"device.vault"; data={"device_id":"id","token":"secret"}
    save(data,"correct horse",p); assert load("correct horse",p)==data
    try: load("wrong",p)
    except ValueError: pass
    else: assert False

def test_vault_ciphertext(tmp_path):
    p=tmp_path/"device.vault"; save({"token":"secret"},"pw",p)
    assert b"secret" not in p.read_bytes()

def test_path_validation():
    for value in ("../secret","/etc/passwd","a/../../b"):
        try: safe_rel(value)
        except Exception: pass
        else: assert False
    assert safe_rel("Documents/a.txt").as_posix()=="Documents/a.txt"


class _Response:
    def __init__(self, chunks, status=200):
        self._chunks=chunks; self.status_code=status
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")
    def iter_content(self, chunk_size):
        yield from self._chunks


def test_download_preserves_relative_path_and_verifies_sha(monkeypatch, tmp_path):
    import client.client as cc
    data=b"nested content"
    import hashlib
    meta={"docs/a.txt":{"size":len(data),"sha256":hashlib.sha256(data).hexdigest()}}
    monkeypatch.setattr(cc, "server_files", lambda server, ident: meta)
    monkeypatch.setattr(cc.requests, "get", lambda *args, **kwargs: _Response([data[:6], data[6:]]))
    out=download_one("http://lan", {"device_id":"d","token":"t"}, "docs/a.txt", tmp_path)
    assert out == tmp_path / "docs" / "a.txt"
    assert out.read_bytes() == data


def test_download_rejects_collision(monkeypatch, tmp_path):
    import client.client as cc
    data=b"same"
    import hashlib
    meta={"docs/a.txt":{"size":len(data),"sha256":hashlib.sha256(data).hexdigest()}}
    monkeypatch.setattr(cc, "server_files", lambda server, ident: meta)
    target=tmp_path / "docs" / "a.txt"
    target.parent.mkdir()
    target.write_bytes(b"existing")
    try:
        download_one("http://lan", {"device_id":"d","token":"t"}, "docs/a.txt", tmp_path)
    except FileExistsError:
        pass
    else:
        assert False
    assert target.read_bytes() == b"existing"


def test_download_rejects_bad_hash(monkeypatch, tmp_path):
    import client.client as cc
    data=b"actual"
    meta={"docs/a.txt":{"size":len(data),"sha256":"0"*64}}
    monkeypatch.setattr(cc, "server_files", lambda server, ident: meta)
    monkeypatch.setattr(cc.requests, "get", lambda *args, **kwargs: _Response([data]))
    try:
        download_one("http://lan", {"device_id":"d","token":"t"}, "docs/a.txt", tmp_path)
    except ValueError as exc:
        assert "integrity" in str(exc).lower()
    else:
        assert False
    assert not (tmp_path / "docs" / "a.txt").exists()


def test_sync_reports_failed_upload(monkeypatch, tmp_path, capsys):
    import client.client as cc
    monkeypatch.setattr(cc, "identity", lambda: {"device_id":"d","token":"t"})
    monkeypatch.setattr(cc, "server_files", lambda server, ident: {})
    file=tmp_path / "failed.txt"
    file.write_text("data")
    monkeypatch.setattr(cc, "scan", lambda root: [file])
    monkeypatch.setattr(cc, "upload_one", lambda *args, **kwargs: False)
    cc.sync("http://lan", tmp_path)
    assert "Upload failed after retries: failed.txt" in capsys.readouterr().out
