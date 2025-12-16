# 🎬 Cinema Seat Booking System

Sistem pemesanan kursi bioskop dengan **arsitektur hybrid** yang mendukung GUI desktop (Tkinter) dan web interface (Flask), menggunakan XML-RPC dan REST API.

## ✨ Fitur Utama

- 🎭 **Pemilihan Film**: 2 pilihan film (The Matrix Reloaded, Inception)
- 💺 **Seat Map**: Grid 5×5 untuk setiap film
- 📝 **Form Pemesanan**: Input data customer (nama, email, telepon)
- 🖥️ **Dual Interface**: GUI Tkinter + Web Browser
- 🌐 **Network Ready**: Bisa diakses dari komputer lain
- 💾 **Data Persistence**: SQLite database
- 🔒 **Thread-Safe**: Mendukung multiple clients concurrent

## 🏗️ Arsitektur

```
┌─────────────────┐         RPC (Port 8000)        ┌──────────────────┐
│  Tkinter GUI    │ ◄──────────────────────────────►│                  │
│  (client.py)    │                                 │  Hybrid Server   │
└─────────────────┘                                 │ (hybrid_server)  │
                                                    │                  │
┌─────────────────┐      HTTP/REST (Port 5000)     │  - RPC Server    │
│  Web Browser    │ ◄──────────────────────────────►│  - Flask Server  │
│  (index.html)   │                                 │  - SQLite DB     │
└─────────────────┘                                 └──────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Buat virtual environment
py -3 -m venv .venv

# Aktifkan virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Jalankan Server

```bash
python hybrid_server.py
```

Server akan berjalan di:
- **RPC Server**: `http://localhost:8000` (untuk GUI)
- **Flask Server**: `http://localhost:5000` (untuk Web)

### 3. Akses Sistem

**Opsi A: Web Browser**
```
http://localhost:5000
```

**Opsi B: GUI Tkinter**
```bash
python client.py
```

## 📁 Struktur Project

```
Cinema-Seat-Book/
├── hybrid_server.py        # Server utama (RPC + Flask)
├── client.py               # GUI Tkinter client
├── database.py             # Database operations
├── requirements.txt        # Dependencies
├── README.md              # Dokumentasi utama
├── README_HYBRID.md       # Dokumentasi hybrid system
├── templates/
│   └── index.html         # Web interface
├── static/
│   ├── css/style.css      # Web styling
│   └── js/app.js          # Web JavaScript
├── server.py              # Legacy RPC-only server
└── app.py                 # Legacy Flask-only server
```

## 🌐 Akses dari Komputer Lain

### Server (PC Anda)

1. Jalankan server:
```bash
python hybrid_server.py
```

2. Catat IP address yang ditampilkan (contoh: `192.168.1.100`)

### Client (PC Lain)

**Untuk GUI:**
1. Edit `client.py`, ubah:
```python
SERVER_HOST = "192.168.1.100"  # IP server Anda
```

2. Jalankan:
```bash
python client.py
```

**Untuk Web:**
- Buka browser: `http://192.168.1.100:5000`

## 🔧 Teknologi

- **Backend**: Python 3.x
- **GUI**: Tkinter
- **Web Framework**: Flask 3.0.0
- **Database**: SQLite3
- **RPC**: XML-RPC (built-in Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

## 📖 Dokumentasi

- [README_HYBRID.md](README_HYBRID.md) - Dokumentasi lengkap hybrid system
- [README_FLASK.md](README_FLASK.md) - Dokumentasi Flask-only version

## 🎯 Use Cases

### Use Case 1: Booking via GUI
1. Jalankan `client.py`
2. Pilih film
3. Klik kursi yang tersedia
4. Isi form pemesanan
5. Konfirmasi booking

### Use Case 2: Booking via Web
1. Buka `http://localhost:5000`
2. Klik card film
3. Pilih kursi hijau
4. Isi form di modal
5. Klik "Confirm Booking"

### Use Case 3: Multi-Client
- Beberapa GUI client bisa connect bersamaan
- Web browser bisa diakses dari multiple devices
- Semua booking tersimpan di database yang sama

## 🔒 Keamanan & Concurrency

- **Thread-Safe**: Database menggunakan thread-local connections
- **Transaction Isolation**: SQLite transactions mencegah race conditions
- **Input Validation**: Email dan phone number divalidasi
- **Error Handling**: Comprehensive error messages

## 📊 Database Schema

### Movies Table
```sql
CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    genre TEXT NOT NULL,
    duration TEXT NOT NULL,
    showtime TEXT NOT NULL,
    poster_emoji TEXT NOT NULL
)
```

### Seats Table
```sql
CREATE TABLE seats (
    movie_id INTEGER NOT NULL,
    row INTEGER NOT NULL,
    col INTEGER NOT NULL,
    status INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (movie_id, row, col)
)
```

### Bookings Table
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER NOT NULL,
    row INTEGER NOT NULL,
    col INTEGER NOT NULL,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Can't Connect from Other PC
1. Check firewall allows ports 8000 and 5000
2. Verify IP address is correct
3. Make sure both PCs are on same network

### Database Locked
```bash
# Delete database and restart
rm cinema_booking.db
python hybrid_server.py
```

## 👨‍💻 Author

Dibuat sebagai project mata kuliah SMS5 - Distributed Systems

## 📄 License

Educational project - Free to use for learning purposes

## 🙏 Acknowledgments

- Flask framework
- Python XML-RPC library
- Tkinter GUI toolkit
- SQLite database

---

**Note**: Untuk dokumentasi lengkap tentang hybrid architecture, lihat [README_HYBRID.md](README_HYBRID.md)
