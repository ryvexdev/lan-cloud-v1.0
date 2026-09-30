"""Password-encrypted local credential vault. Server URL is intentionally never stored."""
import base64, json, os
from pathlib import Path
from getpass import getpass
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

VAULT_PATH=Path.home()/".lan-cloud"/"device.vault"
ITERATIONS=600_000

def _key(password: str, salt: bytes) -> bytes:
    kdf=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=ITERATIONS)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def save(data: dict, password: str, path: Path=VAULT_PATH):
    path.parent.mkdir(parents=True,exist_ok=True); os.chmod(path.parent,0o700)
    salt=os.urandom(16); token=Fernet(_key(password,salt)).encrypt(json.dumps(data).encode())
    path.write_bytes(b"LCV1"+salt+token); os.chmod(path,0o600)

def load(password: str, path: Path=VAULT_PATH) -> dict:
    raw=path.read_bytes()
    if not raw.startswith(b"LCV1"): raise ValueError("Unsupported vault format")
    try: return json.loads(Fernet(_key(password,raw[4:20])).decrypt(raw[20:]))
    except (InvalidToken, ValueError): raise ValueError("Incorrect vault password or damaged vault")

def get_password(confirm=False):
    env=os.environ.get("LAN_CLOUD_PASSWORD")
    if env: return env
    p=getpass("Vault password: ")
    if confirm and p!=getpass("Confirm password: "): raise ValueError("Passwords do not match")
    if not p: raise ValueError("Password cannot be empty")
    return p
