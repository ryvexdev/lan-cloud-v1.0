# ☁️ LAN CLOUD v1.0

> **Private LAN Cloud Storage --- fast, simple, and designed for your
> own network.**

> **Version:** v1.0  
> **Architecture:** Private LAN / self-hosted  
> **Backend:** Python + FastAPI/Uvicorn  
> **Database:** SQLite  
> **License:** MIT License  
> **Bug reports:** WhatsApp `+62 878-9225-1045`


LAN CLOUD is a self-hosted cloud storage system built with **Python**
and designed for private use over a trusted **LAN/Wi-Fi network**.

The backend runs locally on an Ubuntu/Linux machine, while client
devices connect through the LAN to upload, download, synchronize, and
manage files.

------------------------------------------------------------------------

## ✨ Highlights

-   🔒 **Private LAN-first architecture**
-   🖥️ Ubuntu/Linux backend
-   📱 Multiple client devices
-   🔑 Device registration with registration key
-   🗄️ SQLite metadata database
-   📦 Per-device storage isolation
-   🔄 Manual sync and watch mode
-   📥 Download with relative-path preservation
-   🛡️ Download collision protection
-   🔐 SHA-256 file integrity verification
-   💾 SQLite backup and restore workflow
-   🧪 Automated regression tests
-   🚫 No public-cloud dependency
-   🌐 Optional tunnel support for temporary remote testing only

------------------------------------------------------------------------

## 🏗️ Architecture

``` text
                    ┌──────────────────────────┐
                    │      LAN / Wi-Fi         │
                    │     Trusted Network      │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
        ┌───────────┐      ┌───────────┐      ┌───────────┐
        │ Client #1 │      │ Client #2 │      │ Client #N │
        │  Python   │      │  Python   │      │  Python   │
        └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 ▼
                    ┌──────────────────────────┐
                    │       LAN CLOUD          │
                    │      FastAPI/Uvicorn     │
                    └────────────┬─────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
        ┌────────────────┐              ┌────────────────┐
        │ SQLite Database│              │    Storage     │
        │  cloud.db      │              │  device-scoped │
        └────────────────┘              └────────────────┘
```

### Storage isolation

Files are stored per device:

``` text
storage/
├── <device-id-1>/
│   ├── documents/
│   └── photos/
└── <device-id-2>/
    ├── documents/
    └── backups/
```

The database tracks the device, relative path, size, SHA-256, storage
path, modification time, and upload time.

------------------------------------------------------------------------

## 📁 Project Structure

A typical project layout:

``` text
lan-cloud-v1.0/
├── backend/
│   ├── main.py
│   ├── devices.py
│   └── ...
├── client/
│   ├── client.py
│   └── uploader.py
├── database/
│   └── cloud.db
├── storage/
│   └── <device-id>/
├── tests/
│   └── test_core.py
├── tools/
│   └── backup.py
├── .venv/
└── README.md
```

> Struktur dapat bertambah sesuai modul yang digunakan. Jangan menghapus
> file atau direktori yang sudah dipakai sistem.

------------------------------------------------------------------------

# 🚀 Installation — Step by Step

LAN CLOUD dirancang untuk dijalankan sebagai **private cloud di jaringan
LAN/Wi-Fi sendiri**. Tutorial ini mengasumsikan backend menggunakan Ubuntu/Linux
dan client menggunakan Python.

## 1. Persiapan Ubuntu/Linux

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
```

Cek:

```bash
git --version
python3 --version
```

## 2. Clone Repository

```bash
git clone https://github.com/ryvexdev/lan-cloud-v1.0.git
cd lan-cloud-v1.0
```

Atau melalui SSH:

```bash
git clone git@github.com:<USERNAME>/lan-cloud-v1.0.git
cd lan-cloud-v1.0
```

## 3. Buat Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install Dependencies

Jika tersedia `requirements.txt`:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Cek environment:

```bash
which python
python --version
```

## 5. Siapkan Registration Key

LAN CLOUD menggunakan registration key untuk mengontrol pendaftaran device.

```bash
export LAN_CLOUD_REGISTRATION_KEY='GANTI-DENGAN-KEY-RAHASIA'
```

Verifikasi tanpa mencetak secret:

```bash
test -n "$LAN_CLOUD_REGISTRATION_KEY" && echo "Registration key is set"
```

## 6. Jalankan Backend

```bash
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Server:

```text
http://<IP-SERVER-LAN>:8000
```

Cari IP server:

```bash
hostname -I
```

atau:

```bash
ip addr
```

Gunakan IP dari interface LAN/Wi-Fi yang sama dengan client.

## 7. Test Backend dari Client

Dari device lain di LAN:

```bash
curl http://<IP-SERVER-LAN>:8000/
```

Baseline response versi tervalidasi:

```json
{
  "name": "LAN Cloud",
  "version": "1.0.1",
  "scope": "private LAN"
}
```

Jika tidak terhubung, periksa IP server, LAN/Wi-Fi, firewall, port `8000`,
dan proses Uvicorn.

## 8. Register Device Client

```bash
cd lan-cloud-v1.0/client
source ../.venv/bin/activate
python client.py --server http://<IP-SERVER-LAN>:8000 --register
```

Contoh:

```bash
python client.py --server http://192.168.1.10:8000 --register
```

Setelah berhasil:

```text
✓ Device registered and encrypted vault saved.
```

Credential device disimpan dalam encrypted vault client.

## 9. Upload / Sync

```bash
mkdir -p ~/lan-cloud-data
echo "LAN CLOUD test" > ~/lan-cloud-data/test.txt

python client.py --server http://<IP-SERVER-LAN>:8000 \
  --sync ~/lan-cloud-data
```

## 10. Lihat File

```bash
python client.py --server http://<IP-SERVER-LAN>:8000 --list
```

## 11. Watch Mode

```bash
python client.py --server http://<IP-SERVER-LAN>:8000 \
  --watch ~/lan-cloud-data
```

Hentikan dengan:

```text
Ctrl+C
```

## 12. Download

```bash
python client.py --server http://<IP-SERVER-LAN>:8000 \
  --download test.txt \
  --output ~/lan-cloud-download
```

Untuk subdirectory:

```bash
python client.py --server http://<IP-SERVER-LAN>:8000 \
  --download docs/laporan.txt \
  --output ~/lan-cloud-download
```

Relative path tetap dipertahankan:

```text
docs/laporan.txt
→ ~/lan-cloud-download/docs/laporan.txt
```

Client juga menolak overwrite terhadap file target yang sudah ada.

## 13. Verifikasi SHA-256

```bash
sha256sum file-asli
sha256sum file-hasil-download
```

Hash yang sama berarti isi file identik secara byte-level.

---

# 🧪 First-Time Installation Checklist

```bash
source .venv/bin/activate
pytest -q
python -m compileall -q .
git status
```

Baseline validasi saat dokumentasi ini dibuat:

```text
pytest: 7 passed
compileall: PASS
```

Angka tersebut adalah baseline, bukan batas jumlah test project.

# 🔐 Registration Key

LAN CLOUD menggunakan registration key untuk mengontrol pendaftaran
device baru.

Set pada environment server:

``` bash
export LAN_CLOUD_REGISTRATION_KEY='GANTI-DENGAN-KEY-RAHASIA'
```

> **Jangan commit registration key ke Git dan jangan membagikannya di
> README publik.**

Untuk penggunaan permanen, lebih baik gunakan environment management
yang sesuai dengan server.

------------------------------------------------------------------------

# 🖥️ Menjalankan Backend

Dari root project:

``` bash
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Server akan tersedia pada:

``` text
http://<IP-SERVER-LAN>:8000
```

Contoh:

``` text
http://192.168.1.10:8000
```

### Mengetahui IP server

Linux:

``` bash
hostname -I
```

atau:

``` bash
ip addr
```

Gunakan alamat IP yang berada pada interface LAN/Wi-Fi yang sama dengan
client.

------------------------------------------------------------------------

# 📱 Register Device

Pada device client:

``` bash
cd ~/lan-cloud/lan-cloud-v1.0/client
```

Kemudian:

``` bash
python client.py --server http://<IP-SERVER-LAN>:8000 --register
```

Contoh:

``` bash
python client.py --server http://192.168.1.10:8000 --register
```

Client akan meminta:

1.  Nama device
2.  Registration Key
3.  One-time registration token / credential sesuai alur aplikasi

Setelah berhasil, credential device disimpan dalam encrypted vault
client.

Contoh hasil:

``` text
✓ Device registered and encrypted vault saved.
```

### ⚠️ Simpan credential dengan aman

Credential device memberikan akses ke LAN CLOUD. Jangan membagikannya
kepada orang lain.

------------------------------------------------------------------------

# 📤 Upload / Sync

Untuk melakukan sinkronisasi sebuah folder:

``` bash
python client.py \
  --server http://<IP-SERVER-LAN>:8000 \
  --sync ~/lan-cloud-test
```

Contoh:

``` bash
python client.py \
  --server http://192.168.1.10:8000 \
  --sync ~/Documents/LAN-CLOUD
```

LAN CLOUD akan mempertahankan struktur relatif file.

Contoh:

``` text
Documents/LAN-CLOUD/
├── test.txt
└── docs/
    └── laporan.txt
```

akan disimpan sebagai:

``` text
test.txt
docs/laporan.txt
```

dalam storage device tersebut.

------------------------------------------------------------------------

# 👀 Watch Mode

Untuk memantau perubahan file secara terus-menerus:

``` bash
python client.py \
  --server http://<IP-SERVER-LAN>:8000 \
  --watch ~/Documents/LAN-CLOUD
```

Ketika file berubah, watch mode akan mendeteksi perubahan dan melakukan
sinkronisasi sesuai mekanisme client.

Hentikan dengan:

``` text
Ctrl + C
```

------------------------------------------------------------------------

# 📋 Melihat Daftar File

Gunakan:

``` bash
python client.py \
  --server http://<IP-SERVER-LAN>:8000 \
  --list
```

Output akan menampilkan metadata file yang tersedia untuk device
tersebut.

Contoh:

``` text
docs/laporan.txt    19 bytes
test-upload.txt     155 bytes
```

------------------------------------------------------------------------

# 📥 Download

Download file:

``` bash
python client.py \
  --server http://<IP-SERVER-LAN>:8000 \
  --download docs/laporan.txt \
  --output ~/Downloads/LAN-CLOUD
```

> `--output` digunakan sebagai **direktori output**. Nama file dan
> struktur relatif akan dibentuk oleh client.

Contoh:

``` text
~/Downloads/LAN-CLOUD/
└── docs/
    └── laporan.txt
```

------------------------------------------------------------------------

# 🛡️ Download Safety

Client memiliki perlindungan terhadap overwrite file yang sudah ada.

Jika target sudah ada:

``` text
FileExistsError:
Refusing to overwrite existing file: ...
```

File lama tidak akan ditimpa secara diam-diam.

------------------------------------------------------------------------

# 🔐 File Integrity

LAN CLOUD menggunakan **SHA-256** untuk membantu memastikan file hasil
download sesuai dengan file yang di-upload.

Contoh pemeriksaan manual:

``` bash
sha256sum original.txt downloaded.txt
```

Jika kedua hash sama:

``` text
978d2563add9dae967a0b10a736b6243c70bcfdc9fca56a7aa7c1fc7b551894a
978d2563add9dae967a0b10a736b6243c70bcfdc9fca56a7aa7c1fc7b551894a
```

berarti konten identik berdasarkan SHA-256.

------------------------------------------------------------------------

# 💾 Database & Backup

Database utama:

``` text
database/cloud.db
```

Backup dapat dibuat menggunakan:

``` bash
python tools/backup.py cloud-backup.db
```

Contoh:

``` text
SQLite backup created: cloud-backup.db
```

## Memeriksa backup

Dengan Python:

``` bash
python -c "import sqlite3; c=sqlite3.connect('cloud-backup.db'); print(c.execute('PRAGMA integrity_check').fetchone()[0]); c.close()"
```

Output yang diharapkan:

``` text
ok
```

------------------------------------------------------------------------

# ♻️ Restore / Recovery

Untuk recovery, **jangan langsung mengganti database aktif** tanpa
memastikan backup valid.

Langkah aman:

1.  Buat backup database aktif.
2.  Validasi backup.
3.  Buat salinan backup untuk simulasi restore.
4.  Jalankan integrity check.
5.  Verifikasi jumlah record.
6.  Baru lakukan prosedur restore yang sesuai kebutuhan.

Contoh simulasi:

``` bash
cp cloud-backup.db restore-test.db
```

Kemudian:

``` bash
python -c "import sqlite3; c=sqlite3.connect('restore-test.db'); print('integrity:', c.execute('PRAGMA integrity_check').fetchone()[0]); print('devices:', c.execute('SELECT COUNT(*) FROM devices').fetchone()[0]); print('files:', c.execute('SELECT COUNT(*) FROM files').fetchone()[0]); c.close()"
```

------------------------------------------------------------------------

# 🧪 Testing

Jalankan seluruh test:

``` bash
pytest -q
```

Current validated baseline:

``` text
7 passed
```

Compile check:

``` bash
python -m compileall -q .
```

Jika tidak menghasilkan error, compile check berhasil.

------------------------------------------------------------------------

# 🔍 Storage Consistency Check

Karena storage dipisahkan berdasarkan device, path fisik mengikuti pola:

``` text
storage/<device_id>/<rel_path>
```

Consistency check:

``` bash
python -c "import sqlite3, os; c=sqlite3.connect('database/cloud.db'); rows=c.execute('SELECT device_id, rel_path, storage_path FROM files').fetchall(); missing=[]; mismatched=[]; print('DB records:',len(rows)); [missing.append((d,r,s)) for d,r,s in rows if not os.path.isfile(os.path.join('storage',d,r))]; [mismatched.append((d,r,s,os.path.join(d,r))) for d,r,s in rows if s != os.path.join(d,r)]; print('Missing storage files:',len(missing)); print('Missing:',missing); print('Storage path mismatches:',len(mismatched)); print('Mismatches:',mismatched); c.close()"
```

Expected:

``` text
DB records: 6
Missing storage files: 0
Missing: []
Storage path mismatches: 0
Mismatches: 0
```

> Jumlah record akan berubah sesuai penggunaan. Angka `6` di atas adalah
> baseline dari live testing, bukan batas sistem.

------------------------------------------------------------------------

# 🔒 Security Model

LAN CLOUD dirancang untuk **trusted private LAN**, bukan sebagai public
internet cloud.

### Device isolation

Setiap device memiliki storage namespace sendiri:

``` text
storage/
├── DEVICE-A/
└── DEVICE-B/
```

File milik satu device tidak seharusnya dapat diakses melalui credential
device lain.

### Path safety

Relative paths harus diproses sebagai path file dalam namespace device.
Traversal seperti:

``` text
../../etc/passwd
```

tidak boleh digunakan untuk keluar dari storage namespace.

### Authentication

Request client menggunakan credential device yang tersimpan pada
encrypted vault.

### Registration

Pendaftaran device baru dilindungi oleh registration key.

------------------------------------------------------------------------

# 🌐 LAN-Only Deployment

Desain utama:

``` text
Client ──LAN/Wi-Fi──> Ubuntu Server
```

Tidak diperlukan:

-   public cloud
-   VPS
-   domain publik
-   ngrok
-   reverse proxy internet

Server cukup dijalankan pada jaringan lokal.

------------------------------------------------------------------------

# ⚠️ Network Security

LAN CLOUD saat ini menggunakan HTTP pada jaringan lokal.

Artinya traffic LAN **tidak otomatis terenkripsi seperti HTTPS/TLS**.

Karena itu:

-   Gunakan pada jaringan yang dipercaya.
-   Hindari Wi-Fi publik.
-   Jangan membuka port server langsung ke internet.
-   Gunakan firewall.
-   Jangan membagikan credential device.
-   Jika membutuhkan akses melalui internet, gunakan lapisan keamanan
    tambahan yang memang dirancang untuk remote access.

------------------------------------------------------------------------

# 🌍 Optional Remote Access

Tunnel seperti **ngrok** dapat digunakan untuk pengujian remote
sementara jika memang diperlukan.

Namun:

> **ngrok bukan dependency production LAN CLOUD.**

Membuka backend ke internet meningkatkan attack surface dan bertentangan
dengan tujuan utama desain private-LAN.

Untuk deployment normal:

``` text
Internet
   ✕
   │
   ▼
LAN CLOUD
   │
   ├── Client
   ├── Client
   └── Client
```

------------------------------------------------------------------------

# 🧰 Operational Commands

### Start server

``` bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Register device

``` bash
python client.py --server http://SERVER-IP:8000 --register
```

### Sync

``` bash
python client.py --server http://SERVER-IP:8000 --sync ~/folder
```

### Watch

``` bash
python client.py --server http://SERVER-IP:8000 --watch ~/folder
```

### List

``` bash
python client.py --server http://SERVER-IP:8000 --list
```

### Download

``` bash
python client.py --server http://SERVER-IP:8000 --download path/to/file --output ~/Downloads/LAN-CLOUD
```

### Backup

``` bash
python tools/backup.py cloud-backup.db
```

### Tests

``` bash
pytest -q
```

### Compile check

``` bash
python -m compileall -q .
```

------------------------------------------------------------------------

# 🌐 Repository & Open Contribution

LAN CLOUD dikembangkan dengan workflow Git agar perubahan dapat diaudit dan
ditinjau secara terbuka.

## Clone Repository

```bash
git clone https://github.com/ryvexdev/lan-cloud-v1.0.git
cd lan-cloud-v1.0
```

## Buat Branch

```bash
git checkout -b fix/nama-perbaikan
```

Contoh:

```bash
git checkout -b fix/download-integrity
```

## Review Sebelum Commit

```bash
git status
git diff
```

Pastikan hanya perubahan yang diperlukan yang ikut masuk.

## Commit

Contoh:

```bash
git add .
git commit -m "fix: prevent download overwrite"
```

Prefix yang direkomendasikan:

```text
feat: fitur baru
fix: perbaikan bug
docs: dokumentasi
test: test/regression test
refactor: refactor
security: security hardening
chore: maintenance
```

## Push & Open Pull Request

```bash
git push -u origin fix/nama-perbaikan
```

Kemudian buka repository GitHub dan buat **Pull Request (PR)** ke branch
utama.

Sertakan:

- masalah yang ditemukan
- perubahan yang dilakukan
- alasan perubahan
- test yang dijalankan
- hasil test
- dampak terhadap sistem existing

### Prinsip Kontribusi

> **Jangan mengubah sistem yang sudah fixed tanpa alasan teknis yang jelas.**

Kontributor diharapkan menjaga fitur existing, menghindari refactor besar
yang tidak diperlukan, menambahkan regression test untuk bug bila memungkinkan,
dan tidak memasukkan secret, token, registration key, credential, atau data
pribadi ke repository.

### Contoh Workflow Lengkap

```bash
git clone https://github.com/ryvexdev/lan-cloud-v1.0.git
cd lan-cloud-v1.0

git checkout -b fix/my-bug

# lakukan perubahan...

git status
git diff

pytest -q
python -m compileall -q .

git add .
git commit -m "fix: describe the bug fix"
git push -u origin fix/my-bug
```

Lanjutkan dengan membuka Pull Request melalui repository GitHub.

---

# 🐛 Bug Report & Support

Untuk melaporkan bug, masalah instalasi, error runtime, atau perilaku sistem
yang tidak sesuai:

**WhatsApp:** `+62 878-9225-1045`

Sertakan jika aman untuk dibagikan:

```text
LAN CLOUD version:
OS:
Python version:
Command yang dijalankan:
Error message:
Langkah untuk mereproduksi:
Expected behavior:
Actual behavior:
```

> **Jangan kirim registration key, device token, encrypted vault, password,
> credential, database pribadi, atau secret lainnya.**

---

# 🩺 Troubleshooting

## Server tidak bisa diakses

Periksa server:

``` bash
ps aux | grep uvicorn
```

Periksa port:

``` bash
ss -lntp | grep 8000
```

Periksa IP:

``` bash
hostname -I
```

Pastikan client dan server berada di jaringan LAN yang sama.

------------------------------------------------------------------------

## Client mendapatkan connection refused

Pastikan backend sedang berjalan:

``` bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Kemudian gunakan IP LAN server, bukan `127.0.0.1`, jika client berada di
device berbeda.

------------------------------------------------------------------------

## Registration gagal

Periksa registration key pada server:

``` bash
echo "$LAN_CLOUD_REGISTRATION_KEY"
```

Pastikan key yang dimasukkan client sama dengan key yang dikonfigurasi
server.

**Jangan kirim registration key ke chat, log publik, atau repository.**

------------------------------------------------------------------------

## Download menolak overwrite

Jika muncul:

``` text
FileExistsError:
Refusing to overwrite existing file
```

itu merupakan perlindungan normal.

Gunakan direktori output lain atau pindahkan file lama terlebih dahulu.

------------------------------------------------------------------------

## Test gagal

Jalankan:

``` bash
pytest -q
```

Untuk compile check:

``` bash
python -m compileall -q .
```

Jangan langsung mengubah source berdasarkan satu error sebelum
mengetahui root cause-nya.

------------------------------------------------------------------------

# 📊 Current Validation Status

LAN CLOUD v1.0 telah melalui live verification untuk scope berikut:

  Component                     Status
  ---------------------------- --------
  Device registration             ✅
  Encrypted client vault          ✅
  Authentication                  ✅
  Upload                          ✅
  File listing                    ✅
  Download                        ✅
  SHA-256 integrity               ✅
  Collision protection            ✅
  Relative path preservation      ✅
  Sync/update                     ✅
  Watch mode                      ✅
  Database integrity              ✅
  Backup creation                 ✅
  Backup integrity                ✅
  Backup ↔ active DB count        ✅
  Restore simulation              ✅
  DB ↔ storage consistency        ✅
  Regression tests              ✅ 7/7
  Python compile check            ✅

### Validation baseline

Pada live test terakhir:

``` text
Database records: 6
Missing storage files: 0
Storage path mismatches: 0
```

Storage consistency menggunakan model:

``` text
storage/<device_id>/<rel_path>
```

------------------------------------------------------------------------

# 🛣️ Future Hardening

Beberapa area dapat ditingkatkan tanpa mengubah core architecture:

-   🔐 HTTPS/TLS untuk jaringan yang membutuhkan encryption
-   🚦 Registration rate limiting
-   🔑 Device revocation
-   🔄 Improved concurrent-operation handling
-   🧪 Expanded security regression tests
-   🔒 Stronger backup file permissions
-   📊 Better operational logging
-   🧰 Improved CLI help/argument handling

Fitur-fitur tersebut merupakan **hardening/future work**, bukan alasan
untuk mengubah sistem yang sudah tervalidasi sekarang.

------------------------------------------------------------------------

# 📌 Design Principles

LAN CLOUD mengikuti prinsip:

> **Private by default.**

> **Minimal changes.**

> **Device isolation.**

> **Verify before trusting.**

> **Do not silently overwrite user data.**

> **Keep existing working systems stable.**

> **Security fixes should be minimal, targeted, and regression-tested.**

------------------------------------------------------------------------

# 👤 Intended Use

LAN CLOUD cocok untuk:

-   Personal private cloud
-   Home LAN storage
-   Local device backup
-   File synchronization antar-device
-   Private development/testing environment
-   Self-hosted storage tanpa public cloud

LAN CLOUD **bukan dirancang sebagai public file-sharing service**.

------------------------------------------------------------------------

# 📄 License

## LAN CLOUD v1.0 — MIT License

LAN CLOUD v1.0 menggunakan **MIT License** untuk source code dan dokumentasi
project yang didistribusikan sebagai bagian dari project, kecuali komponen
yang memiliki lisensi berbeda.

Dependency pihak ketiga tetap mengikuti lisensi masing-masing.
  
```text
MIT License

Copyright (c) 2026 LAN CLOUD Project

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

---

# 🤝 Project Philosophy

LAN CLOUD dibuat dengan prinsip:

- **Private by design**
- **LAN-first**
- **Minimal attack surface**
- **Data isolation per device**
- **Integrity before convenience**
- **Transparent open development**
- **Minimal changes to fixed systems**
- **No public-cloud dependency**

Project ini ditujukan untuk penggunaan pribadi, internal, lab, development,
dan lingkungan LAN yang dikendalikan oleh pemiliknya.

dipublikasikan.

------------------------------------------------------------------------

## ☁️ LAN CLOUD

**Private. Local. Controlled.**

Built for your own network.
