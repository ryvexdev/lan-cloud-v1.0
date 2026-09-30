# LAN Cloud v1.0 — hardening update 1.0.1

Private, self-hosted LAN file storage. Ubuntu runs FastAPI + SQLite; file bytes stay on its local filesystem. Client credentials are stored in a password-encrypted Fernet vault. No external cloud, telemetry, or application-created storage quota.

> Security note: bind Uvicorn to `0.0.0.0` only on a trusted LAN and restrict port 8000 with the host firewall. HTTP on a LAN does not encrypt traffic. Use a trusted isolated Wi-Fi/LAN; do not forward this port to the internet.

## Ubuntu installation (root deployment)

```bash
apt update
apt upgrade -y
apt install -y python3 python3-pip python3-venv curl unzip tar
mkdir -p /opt/lan-cloud
# Extract this project into /opt/lan-cloud/lan-cloud-v1.0, or copy its contents there.
cd /opt/lan-cloud/lan-cloud-v1.0
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

## Server startup

From the project root:

```bash
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Endpoints: `GET /`, `GET /health`, `POST /register`, `POST /upload`, `GET /files`, `GET /download?relative_path=...`, `DELETE /files?relative_path=...`. Registration is unauthenticated by design and should only be exposed to a trusted LAN. Device endpoints use `X-Device-ID` and `X-Device-Token` headers.

## LAN firewall

Example LAN `192.168.1.0/24`, server `192.168.1.10`, port `8000`. With UFW, allow only the LAN subnet and deny other inbound access to this port:

```bash
ufw allow from 192.168.1.0/24 to any port 8000 proto tcp
ufw deny 8000/tcp
ufw status
```

Adapt the subnet to the actual private LAN. Do not configure router port forwarding. `0.0.0.0` is a listening interface, not a public-cloud deployment; firewall policy is essential.

## Client install

```bash
cd client
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

On Android use Termux, install Python, then the same pip command. Root is not required. On Windows use Python 3.11+ and a virtual environment; invoke `python client.py` instead of `python3 client.py`.

## Registration, token, and encrypted vault

```bash
python3 client.py --server http://192.168.1.10:8000 --register
```

Copy the one-time token from the terminal, enter it to verify, then choose a vault password. The encrypted `~/.lan-cloud/device.vault` uses PBKDF2-HMAC-SHA256 and Fernet. `LAN_CLOUD_PASSWORD` can supply the password for unattended runs; set it through the service environment, not source code. Server URL is never stored in the vault or a config file. Protect the one-time token and vault password.

## Sync and silent watch

```bash
python3 client.py --server http://192.168.1.10:8000 --sync ~/Documents
python3 client.py --server http://192.168.1.10:8000 --watch ~/Documents
```

Sync scans files, compares remote path/size/SHA-256, and uploads only changes. Watch mode polls every three seconds and intentionally suppresses upload errors/progress. Retries use exponential backoff up to 32 seconds. Keep the process running for continuous watch.

## List, download, delete

```bash
python3 client.py --server http://192.168.1.10:8000 --list
python3 client.py --server http://192.168.1.10:8000 --download Documents/report.pdf --output ~/Downloads
python3 client.py --server http://192.168.1.10:8000 --delete Documents/report.pdf
```

Each device sees only its own file records and files. Device registration creates a separate identity/storage namespace.

## Backup

```bash
python3 tools/backup.py
```

This makes a consistent SQLite metadata backup. Back up `storage/` separately with filesystem backup tools and preserve the database and file tree together.

## Testing

```bash
pip install pytest cryptography fastapi python-multipart
python3 -m pytest -q
```

The included tests cover vault encryption/decryption and basic path traversal rejection. For production acceptance, also test large-file transfers, concurrent uploads, device isolation, disk-full behavior, retry behavior, and restore procedures on the target Ubuntu host.

## Troubleshooting

- Connection refused: confirm server process, LAN IP, subnet, and firewall.
- 401: verify the correct vault/device and token; reset by registering a new device after removing the old record through an administrator procedure.
- Vault password error: password cannot be recovered; keep a secure backup of the vault and password.
- Disk full: free filesystem space; there is no application quota.
- Permission error: run the service account with write access to `storage/` and `database/`.
- Never expose port 8000 to the public internet. Current transport is plain HTTP; use only a trusted LAN.


## Security hardening & acceptance workflow (Stages 1–6)

1. **Source audit:** review routes, authentication dependencies, path validation, file writes, and error responses. Registration is `POST /register`; authenticated device listing returns only the authenticated device identity.
2. **Ubuntu hardening:** run as a dedicated unprivileged service account where practical; keep project/database/storage permissions restrictive; do not expose port 8000 with router port-forwarding.
3. **Authorization tests:** verify invalid tokens fail, and device A cannot list/download/delete device B's files. Run tests before deployment.
4. **Transfer integrity:** validate file size and SHA-256 server-side; use temporary upload then atomic replace. Exercise large uploads and interrupted transfers on the target filesystem.
5. **Client automation:** use `--sync` for one-shot synchronization and `--watch` for silent polling; monitor process health externally rather than enabling noisy terminal output.
6. **Recovery:** take SQLite online backups and separately back up the storage tree; perform a restore drill and compare file hashes.

### Example UFW rules (adapt subnet; ensure SSH access first)

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow from 192.168.1.0/24 to any port 8000 proto tcp
ufw enable
ufw status verbose
```

Replace `192.168.1.0/24` with the trusted LAN subnet. Check IPv4 and IPv6 firewall policy and router settings. HTTP traffic is not encrypted; use only a trusted isolated LAN or configure a private VPN/TLS layer for untrusted networks.

### Stages 1–6 validation checklist

- [ ] Audit all routes and secret/error handling.
- [ ] Confirm port 8000 is reachable only from the intended LAN.
- [ ] Test wrong token and cross-device access denial.
- [ ] Test large-file upload, wrong hash/size rejection, and interrupted upload cleanup.
- [ ] Test sync deduplication, changed-file upload, silent watch, and retry behavior.
- [ ] Restore a database + storage backup and verify hashes.

**Deployment caveat:** firewall and network isolation cannot be enforced by the Python application alone. Apply and verify the host/router firewall on the actual Ubuntu server. This project has not been independently penetration-tested.
