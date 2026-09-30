# ☁️ LAN CLOUD v1.0.1

> **Your private cloud, running on your own network. Simple. Secure. Yours.**

Private, self-hosted LAN file storage built for personal and trusted local
networks.

LAN CLOUD menjalankan **FastAPI + SQLite** pada Ubuntu server, sementara byte
file tetap berada di filesystem lokal server.

Tidak membutuhkan external cloud storage, telemetry, atau application-created
storage quota.

---

## ✨ Highlights

- 🔒 Private LAN-first architecture
- 🖥️ Ubuntu sebagai backend/server utama
- ⚡ FastAPI + Uvicorn
- 🗄️ SQLite metadata database
- 📁 Local filesystem storage
- 🔐 Device authentication
- 🔑 Password-encrypted client vault
- 🛡️ Device isolation
- 📦 File upload/download/delete
- 🔄 Sync mode
- 👀 Watch mode
- ♻️ Retry dengan exponential backoff
- 🧮 SHA-256 file integrity
- 🚫 Download overwrite protection
- 🗂️ Relative path preservation
- 💾 SQLite backup & restore workflow
- 🧪 Regression testing
- 🌐 LAN-only by design
- 🚫 No mandatory public cloud
- 🚫 No telemetry
- 🚫 No router port forwarding requirement

---

# 🏗️ Architecture

```text
                    Trusted LAN / Wi-Fi
                           │
          ┌────────────────┼────────────────┐
          │                │                │
      Client A          Client B          Client C
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                    Ubuntu Server
                           │
                    FastAPI + Uvicorn
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        SQLite Database            Local Storage
        metadata only              actual file bytes
```

Storage menggunakan namespace berdasarkan device:

```text
storage/
├── <device-id-A>/
│   ├── Documents/
│   └── Photos/
│
└── <device-id-B>/
    ├── Documents/
    └── Backup/
```

Setiap device memiliki identity dan storage namespace sendiri.

---

# ⚠️ Security Notice

LAN CLOUD dirancang untuk **trusted LAN/Wi-Fi**.

Default deployment menggunakan HTTP.

Artinya:

> **Traffic antara client dan server tidak terenkripsi.**

Karena itu:

- gunakan trusted LAN/Wi-Fi
- gunakan network isolation jika diperlukan
- gunakan firewall
- jangan forward port `8000` dari router ke internet
- jangan expose server secara langsung ke public internet

Uvicorn dapat menggunakan:

```bash
--host 0.0.0.0
```

tetapi host firewall tetap harus membatasi siapa yang boleh mengakses port
`8000`.

`0.0.0.0` adalah listening interface, bukan berarti LAN CLOUD otomatis
menjadi public cloud.

---

# 📦 Requirements

## Server

Direkomendasikan:

- Ubuntu/Linux
- Python 3
- Python virtual environment
- SQLite
- FastAPI
- Uvicorn
- LAN/Wi-Fi yang dipercaya

## Client

Didukung secara konsep pada:

- Linux
- Windows
- Android melalui Termux

Root Android **tidak diperlukan** untuk menjalankan client LAN CLOUD.

---

# 🚀 Installation — Ubuntu Server

## 1. Update Ubuntu

```bash
apt update
apt upgrade -y
```

Install dependency dasar:

```bash
apt install -y python3 python3-pip python3-venv curl unzip tar
```

---

## 2. Clone Repository

Repository resmi:

```text
https://github.com/ryvexdev/lan-cloud-v1.0
```

Clone:

```bash
git clone https://github.com/ryvexdev/lan-cloud-v1.0.git
```

Masuk ke project:

```bash
cd lan-cloud-v1.0
```

Atau menggunakan SSH:

```bash
git clone git@github.com:ryvexdev/lan-cloud-v1.0.git
cd lan-cloud-v1.0
```

---

# 📁 Optional Production Location

Untuk deployment server, project dapat ditempatkan di:

```text
/opt/lan-cloud/lan-cloud-v1.0
```

Contoh:

```bash
mkdir -p /opt/lan-cloud
```

Kemudian extract/copy project ke:

```text
/opt/lan-cloud/lan-cloud-v1.0
```

Masuk:

```bash
cd /opt/lan-cloud/lan-cloud-v1.0
```

Untuk deployment production, gunakan dedicated Linux service account yang
tidak memiliki privilege berlebihan jika memungkinkan.

---

# 🐍 3. Create Python Virtual Environment

Dari project root:

```bash
python3 -m venv .venv
```

Aktifkan:

```bash
source .venv/bin/activate
```

Pastikan environment aktif:

```bash
which python
python --version
```

---

# 📚 4. Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

Jika `pip` perlu di-update:

```bash
python -m pip install --upgrade pip
```

Kemudian:

```bash
pip install -r backend/requirements.txt
```

---

# 🔑 5. Registration Key

LAN CLOUD menggunakan registration key untuk mengontrol pendaftaran device.

Set environment variable:

```bash
export LAN_CLOUD_REGISTRATION_KEY='GANTI-DENGAN-KEY-RAHASIA'
```

Verifikasi tanpa mencetak nilai secret:

```bash
test -n "$LAN_CLOUD_REGISTRATION_KEY" && echo "Registration key is set"
```

Jangan pernah memasukkan registration key asli ke:

- Git commit
- GitHub
- README
- screenshot
- source code
- issue publik
- log publik

Untuk deployment permanen, gunakan environment/service configuration yang
sesuai.

---

# 🖥️ 6. Start Backend Server

Dari project root:

```bash
source .venv/bin/activate
```

Jalankan:

```bash
python3 -m uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000
```

Server akan listen pada:

```text
0.0.0.0:8000
```

Cari IP LAN server:

```bash
hostname -I
```

atau:

```bash
ip addr
```

Contoh:

```text
192.168.1.10
```

Maka client LAN dapat menggunakan:

```text
http://192.168.1.10:8000
```

---

# 🔌 API Endpoints

Endpoint utama:

```text
GET    /
GET    /health
POST   /register
POST   /upload
GET    /files
GET    /download?relative_path=...
DELETE /files?relative_path=...
```

## Authentication

Endpoint device menggunakan:

```text
X-Device-ID
X-Device-Token
```

## Registration

```text
POST /register
```

Registration dilakukan sebelum device memiliki credential.

Karena registration endpoint belum menggunakan device token, akses
registration harus dibatasi melalui:

- registration key
- trusted LAN
- host firewall
- network isolation

---

# 🔥 7. LAN Firewall

Contoh environment:

```text
LAN subnet : 192.168.1.0/24
Server IP  : 192.168.1.10
Port       : 8000
```

Dengan UFW:

```bash
ufw allow from 192.168.1.0/24 to any port 8000 proto tcp
ufw deny 8000/tcp
ufw status
```

Untuk baseline firewall:

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow from 192.168.1.0/24 to any port 8000 proto tcp
ufw enable
ufw status verbose
```

> **PENTING:** Jika Ubuntu diakses melalui SSH secara remote, izinkan SSH
> terlebih dahulu sebelum menjalankan `ufw enable`.

Contoh:

```bash
ufw allow ssh
```

Sesuaikan subnet dengan jaringan sebenarnya.

Periksa juga:

- IPv4 firewall
- IPv6 firewall
- router configuration
- Wi-Fi isolation
- VLAN/network isolation jika digunakan

Jangan membuat:

```text
Router Port Forwarding
```

untuk port `8000`.

---

# 🧪 8. Test Server

Dari device yang berada pada LAN yang sama:

```bash
curl http://192.168.1.10:8000/
```

Health check:

```bash
curl http://192.168.1.10:8000/health
```

Jika mendapatkan:

```text
Connection refused
```

periksa:

1. Uvicorn sedang berjalan
2. IP server benar
3. client dan server berada pada LAN yang sama
4. firewall
5. port `8000`
6. interface network server

---

# 📱 Client Installation

## Linux

Masuk ke client:

```bash
cd client
```

Buat virtual environment:

```bash
python3 -m venv .venv
```

Aktifkan:

```bash
. .venv/bin/activate
```

Install dependency:

```bash
pip install -r requirements.txt
```

---

# 📱 Android / Termux

Install Python:

```bash
pkg update
pkg install python
```

Kemudian masuk ke directory client dan gunakan Python seperti biasa.

Root Android **tidak diperlukan** untuk penggunaan LAN CLOUD client.

Contoh:

```bash
python client.py \
  --server http://192.168.1.10:8000 \
  --list
```

---

# 🪟 Windows

Gunakan Python 3.11+.

Buat virtual environment:

```powershell
python -m venv .venv
```

Aktifkan:

```powershell
.venv\Scripts\activate
```

Install dependency:

```powershell
pip install -r requirements.txt
```

Windows menggunakan:

```text
python client.py
```

bukan:

```text
python3 client.py
```

---

# 🔐 Device Registration

Jalankan:

```bash
python3 client.py \
  --server http://192.168.1.10:8000 \
  --register
```

Client akan melakukan proses registration.

Setelah server memberikan one-time token:

1. copy token
2. masukkan token untuk verification
3. pilih vault password

Setelah berhasil, credential device disimpan dalam:

```text
~/.lan-cloud/device.vault
```

---

# 🔒 Encrypted Client Vault

Client credential disimpan menggunakan password-encrypted vault.

Vault menggunakan:

```text
PBKDF2-HMAC-SHA256
Fernet
```

Vault:

```text
~/.lan-cloud/device.vault
```

Password vault harus dilindungi.

Untuk unattended operation, password dapat disediakan melalui:

```text
LAN_CLOUD_PASSWORD
```

Gunakan environment/service configuration.

Jangan hard-code password:

```python
LAN_CLOUD_PASSWORD = "password123"
```

di source code.

Server URL tidak disimpan di vault atau config file.

---

# 🔄 Sync

Untuk one-shot synchronization:

```bash
python3 client.py \
  --server http://192.168.1.10:8000 \
  --sync ~/Documents
```

Sync membandingkan:

```text
relative path
file size
SHA-256
```

File hanya di-upload jika diperlukan.

---

# 👀 Watch Mode

Jalankan:

```bash
python3 client.py \
  --server http://192.168.1.10:8000 \
  --watch ~/Documents
```

Watch mode:

- polling setiap 3 detik
- mendeteksi perubahan
- melakukan synchronization
- menggunakan retry
- exponential backoff hingga 32 detik

Gunakan:

```text
--sync
```

untuk one-shot synchronization.

Gunakan:

```text
--watch
```

untuk continuous synchronization.

Hentikan:

```text
Ctrl+C
```

Watch mode sengaja tidak dibuat noisy untuk progress/error output.

Untuk deployment service, monitor health process dari luar.

---

# 📋 List Files

```bash
python3 client.py \
  --server http://192.168.1.10:8000 \
  --list
```

---

# ⬇️ Download

Contoh:

```bash
python3 client.py \
  --server http://192.168.1.10:8000 \
  --download Documents/report.pdf \
  --output ~/Downloads
```

Relative path dipertahankan.

Contoh remote:

```text
Documents/report.pdf
```

menjadi:

```text
~/Downloads/Documents/report.pdf
```

---

# 🛡️ Download Collision Protection

LAN CLOUD tidak menimpa file target secara diam-diam.

Jika file sudah ada:

```text
FileExistsError
```

akan diberikan dan proses download ditolak.

Ini mencegah accidental overwrite.

---

# 🗑️ Delete

```bash
python3 client.py \
  --server http://192.168.1.10:8000 \
  --delete Documents/report.pdf
```

---

# 🔐 Device Isolation

Setiap device memiliki:

```text
Device ID
Device Token
Storage Namespace
```

Contoh:

```text
storage/
├── device-A/
│   └── Documents/
│
└── device-B/
    └── Documents/
```

Device A tidak boleh:

- list file device B
- download file device B
- delete file device B

Authorization harus selalu berdasarkan identity device yang terautentikasi.

---

# 🧮 File Integrity

LAN CLOUD menggunakan:

```text
File Size
SHA-256
```

Untuk memvalidasi file secara manual:

```bash
sha256sum file-asli
```

dan:

```bash
sha256sum file-hasil-download
```

Hash harus sama.

Contoh:

```text
978d2563add9dae967a0b10a736b6243c70bcfdc9fca56a7aa7c1fc7b551894a
```

---

# 📦 Upload Integrity

Transfer file menggunakan mekanisme:

```text
Temporary Upload
       ↓
Validation
       ↓
SHA-256 / Size Verification
       ↓
Atomic Replace
```

Tujuannya untuk mencegah file setengah-upload dianggap sebagai file valid.

Acceptance testing harus mencakup:

- large files
- interrupted uploads
- wrong size
- wrong SHA-256
- concurrent uploads
- disk full

---

# 💾 Backup

Backup metadata SQLite:

```bash
python3 tools/backup.py
```

Backup tersebut menangani database metadata.

File bytes berada di:

```text
storage/
```

Storage harus dibackup secara terpisah menggunakan filesystem backup tool.

## Recovery Set

Database dan storage harus diperlakukan sebagai satu recovery set:

```text
database backup
+
storage/
```

Jangan hanya melakukan backup SQLite dan menganggap file sudah ikut
terbackup.

---

# ♻️ Restore Drill

Prosedur restore:

```text
1. Restore SQLite database
2. Restore storage/
3. Jalankan integrity check
4. Cocokkan database dengan storage
5. Verifikasi SHA-256
```

Contoh integrity check SQLite:

```bash
python3 -c "
import sqlite3
c=sqlite3.connect('database/cloud.db')
print(c.execute('PRAGMA integrity_check').fetchone()[0])
c.close()
"
```

Expected:

```text
ok
```

---

# 🧪 Testing

Install test dependencies jika diperlukan:

```bash
pip install pytest cryptography fastapi python-multipart
```

Jalankan seluruh test:

```bash
python3 -m pytest -q
```

Compile check:

```bash
python3 -m compileall -q .
```

---

# 🧪 Acceptance Testing

Untuk deployment production, lakukan:

```text
[ ] Server startup
[ ] Health endpoint
[ ] Registration
[ ] Encrypted vault
[ ] Authentication
[ ] Invalid token rejection
[ ] Device isolation
[ ] Upload
[ ] Large-file upload
[ ] Download
[ ] Download collision protection
[ ] Relative path preservation
[ ] SHA-256 verification
[ ] Wrong hash rejection
[ ] Wrong size rejection
[ ] Interrupted upload cleanup
[ ] Concurrent uploads
[ ] Sync deduplication
[ ] Changed-file synchronization
[ ] Watch mode
[ ] Retry behavior
[ ] Delete authorization
[ ] SQLite backup
[ ] Storage backup
[ ] Restore database
[ ] Restore storage
[ ] Post-restore hash verification
[ ] Firewall verification
```

---

# 🔐 Security Hardening & Acceptance Workflow

## Stage 1 — Source Audit

Review:

- API routes
- authentication dependencies
- registration flow
- path validation
- file writes
- error responses
- secret handling

Pastikan authenticated listing hanya mengembalikan identity device yang
sedang terautentikasi.

---

## Stage 2 — Ubuntu Hardening

Recommended:

```text
Dedicated service account
        ↓
Restricted filesystem permissions
        ↓
Host firewall
        ↓
Trusted LAN
        ↓
No router port forwarding
```

Project/database/storage sebaiknya memiliki permission yang restrictive.

---

## Stage 3 — Authorization Tests

Test:

```text
Invalid token
        ↓
Must fail

Device A → Device B files
        ↓
Must fail
```

Validasi:

```text
Device A cannot list Device B
Device A cannot download Device B
Device A cannot delete Device B
```

---

## Stage 4 — Transfer Integrity

Test:

```text
Large upload
Wrong size
Wrong SHA-256
Interrupted upload
Temporary file cleanup
Atomic replacement
Concurrent upload
```

---

## Stage 5 — Client Automation

Gunakan:

```text
--sync
```

untuk one-shot synchronization.

Gunakan:

```text
--watch
```

untuk continuous polling.

Retry menggunakan exponential backoff sampai:

```text
32 seconds
```

Untuk production, monitor process health menggunakan supervisor/service
monitoring daripada mengandalkan terminal.

---

## Stage 6 — Recovery

Recovery harus mencakup:

```text
SQLite backup
+
storage backup
+
restore
+
hash verification
```

Lakukan restore drill secara berkala.

---

# 🌐 LAN-Only Deployment

LAN CLOUD bukan public cloud.

Model deployment:

```text
                  TRUSTED LAN
                       │
          ┌────────────┼────────────┐
          │            │            │
       Client A     Client B     Client C
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
                Ubuntu Server
                       │
                 FastAPI/Uvicorn
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
        SQLite DB             storage/
        metadata              file bytes
```

File bytes tetap berada di filesystem server.

Tidak ada:

```text
External cloud storage
Telemetry
Mandatory internet dependency
Application-created storage quota
```

---

# ⚠️ HTTP Transport

Default transport:

```text
HTTP
```

HTTP pada LAN **tidak mengenkripsi traffic**.

Jangan menganggap trusted LAN berarti traffic otomatis encrypted.

Untuk jaringan yang tidak dipercaya, gunakan private VPN atau TLS layer.

---

# 🌍 Remote Access

LAN CLOUD **tidak membutuhkan ngrok** untuk deployment normal.

Ngrok atau tunnel lain hanya boleh dianggap sebagai:

```text
Temporary testing / remote-access mechanism
```

Tunnel publik meningkatkan attack surface.

Jangan menjadikan tunnel publik sebagai production dependency untuk desain
private-LAN LAN CLOUD.

Jangan expose:

```text
:8000
```

langsung ke internet.

---

# 🩺 Troubleshooting

## Connection refused

Periksa:

```text
Uvicorn
IP server
LAN connection
Subnet
Firewall
Port 8000
```

Cek listening port:

```bash
ss -lntp | grep 8000
```

---

## 401 Unauthorized

Periksa:

- device vault
- device ID
- device token
- server URL
- credential yang digunakan

Jika device perlu diganti, gunakan prosedur registration/admin yang sesuai.

---

## Registration gagal

Periksa:

```text
LAN_CLOUD_REGISTRATION_KEY
LAN connection
Server IP
Port 8000
Firewall
```

---

## Vault password error

Vault password tidak dapat dipulihkan oleh aplikasi.

Jangan menghapus vault sebelum memastikan credential dan recovery procedure
tersedia.

Simpan password dengan aman.

---

## Disk Full

LAN CLOUD tidak membuat application storage quota.

Jika filesystem penuh:

```bash
df -h
```

Bebaskan storage sesuai kebutuhan.

---

## Permission Error

Pastikan service account memiliki permission yang sesuai terhadap:

```text
database/
storage/
```

Jangan memberikan permission root secara berlebihan hanya untuk mengatasi
permission error.

---

## Watch Tidak Berjalan

Periksa:

```text
watch process
filesystem permission
server connection
device credential
retry behavior
path yang dipantau
```

---

# 📊 Current Validation Status

Baseline validasi LAN CLOUD yang telah dilakukan:

```text
Registration + encrypted vault       PASS
Authentication/device isolation     PASS
Upload                              PASS
List                                PASS
Download                            PASS
SHA-256 integrity                   PASS
Collision protection                PASS
Relative path preservation          PASS
Sync/update                         PASS
Watch mode                          PASS
SQLite integrity                    PASS
Backup creation                     PASS
Backup integrity                    PASS
Backup ↔ active DB counts           PASS
Restore simulation                  PASS
DB ↔ storage consistency             PASS
Regression tests                    7/7 PASS
Python compile check                PASS
```

Status tersebut merupakan baseline development validation.

Production deployment tetap harus menjalankan acceptance checklist pada
Ubuntu server sebenarnya.

---

# 🐛 Bug Report & Support

Jika menemukan:

- bug
- installation issue
- authentication issue
- synchronization problem
- storage issue
- unexpected behavior
- security concern

laporkan melalui:

**WhatsApp:** `+62 878-9225-1045`

Format laporan:

```text
LAN CLOUD version:
OS:
Python version:

Command:
...

Error:
...

Steps to reproduce:
1.
2.
3.

Expected:
...

Actual:
...
```

Jangan kirim:

```text
Registration key
Device token
Vault password
Encrypted vault
Private credential
Private database
Private files
```

Jika melaporkan security issue, hindari mempublikasikan credential atau
private data.

---

# 🌐 Repository

Official repository:

```text
https://github.com/ryvexdev/lan-cloud-v1.0
```

Clone:

```bash
git clone https://github.com/ryvexdev/lan-cloud-v1.0.git
```

---

# 🤝 Open Contribution

LAN CLOUD dikembangkan menggunakan workflow Git.

## Create Branch

```bash
git checkout -b fix/nama-perbaikan
```

Contoh:

```bash
git checkout -b fix/download-integrity
```

---

## Review

Sebelum commit:

```bash
git status
git diff
```

Pastikan hanya perubahan yang diperlukan yang masuk.

---

## Testing Before Commit

```bash
python3 -m pytest -q
python3 -m compileall -q .
```

---

## Commit

Gunakan commit message yang jelas:

```bash
git add .
git commit -m "fix: prevent download overwrite"
```

Recommended prefixes:

```text
feat:       feature baru
fix:        bug fix
docs:       documentation
test:       tests
security:   security hardening
refactor:   refactoring
chore:      maintenance
```

---

## Push

```bash
git push -u origin fix/nama-perbaikan
```

Kemudian buat Pull Request ke branch utama repository.

---

# 🧭 Contribution Principles

> **Jangan mengubah sistem yang sudah fixed tanpa alasan teknis yang jelas.**

Kontributor diharapkan:

- menjaga existing functionality
- menghindari refactor besar yang tidak diperlukan
- menambahkan regression test untuk bug
- tidak memasukkan secret
- tidak memasukkan database pribadi
- tidak memasukkan storage runtime
- tidak memasukkan device vault
- menjalankan test sebelum Pull Request
- menjelaskan perubahan secara transparan

---

# 🔒 Git Security Checklist

Sebelum:

```bash
git push
```

pastikan tidak ada:

```text
.env
database/*.db
database/*.sqlite
storage/
*.vault
*.token
*.key
password
API key
registration key
device credential
private data
```

Periksa:

```bash
git status
```

dan:

```bash
git ls-files
```

Cari kemungkinan secret:

```bash
grep -RniE \
"password|passwd|secret|token|api[_-]?key|registration[_-]?key" \
--exclude-dir=.git \
--exclude-dir=.venv \
.
```

Jangan commit hasil atau file yang mengandung credential asli.

---

# 📄 License

## MIT License

LAN CLOUD v1.0.1 menggunakan MIT License.

```text
MIT License

Copyright (c) 2026 RyvexDev / LAN CLOUD Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Dependency pihak ketiga tetap mengikuti lisensi masing-masing.

---

# 🧠 Project Philosophy

LAN CLOUD dibuat dengan prinsip:

```text
Private by design
LAN-first
Minimal attack surface
Device isolation
File integrity
Local storage
Transparent development
Minimal changes to fixed systems
No mandatory public cloud
```

LAN CLOUD ditujukan untuk penggunaan:

- personal
- private network
- home lab
- development
- internal network
- trusted LAN environment

---

# ⚠️ Deployment Caveat

Firewall dan network isolation tidak dapat dipaksakan sepenuhnya oleh aplikasi
Python.

Administrator tetap bertanggung jawab untuk:

```text
Host firewall
Router configuration
LAN isolation
IPv4/IPv6 policy
Filesystem permissions
Service account permissions
Backup policy
Recovery testing
```

HTTP traffic juga tidak terenkripsi.

Project ini **belum menjalani independent penetration test**.

---

# 🚀 Quick Start

Jika semua kebutuhan sudah terpasang:

### Server

```bash
cd /opt/lan-cloud/lan-cloud-v1.0
source .venv/bin/activate

export LAN_CLOUD_REGISTRATION_KEY='YOUR-SECRET-KEY'

python3 -m uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000
```

### Client

```bash
python3 client.py \
  --server http://192.168.1.10:8000 \
  --register
```

### Sync

```bash
python3 client.py \
  --server http://192.168.1.10:8000 \
  --sync ~/Documents
```

### Watch

```bash
python3 client.py \
  --server http://192.168.1.10:8000 \
  --watch ~/Documents
```

### List

```bash
python3 client.py \
  --server http://192.168.1.10:8000 \
  --list
```

### Download

```bash
python3 client.py \
  --server http://192.168.1.10:8000 \
  --download Documents/report.pdf \
  --output ~/Downloads
```

### Backup

```bash
python3 tools/backup.py
```

### Test

```bash
python3 -m pytest -q
```

### Compile

```bash
python3 -m compileall -q .
```

---

# ☁️ LAN CLOUD v1.0.1

**Private cloud.  
Your network.  
Your files.  
Your control.**
