# Cinema Seat Booking System - Hybrid RPC + Flask

## 🎯 Overview

Hybrid architecture combining **XML-RPC** for Tkinter GUI clients and **Flask REST API** for web browsers. Both interfaces share the same SQLite database and support movie selection with customer booking.

## 🏗️ Architecture

```
┌─────────────────┐         RPC (Port 8000)        ┌──────────────────┐
│  Tkinter GUI    │ ◄──────────────────────────────►│                  │
│  (client.py)    │                                 │                  │
└─────────────────┘                                 │  Hybrid Server   │
                                                    │ (hybrid_server)  │
┌─────────────────┐      HTTP/REST (Port 5000)     │                  │
│  Web Browser    │ ◄──────────────────────────────►│  - RPC Server    │
│  (index.html)   │                                 │  - Flask Server  │
└─────────────────┘                                 │  - Database      │
                                                    └──────────────────┘
```

## 🚀 Quick Start

### 1. Start the Hybrid Server

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run hybrid server (RPC + Flask)
python hybrid_server.py
```

**Output:**
```
======================================================================
Cinema Seat Booking - Hybrid RPC + Flask Server
======================================================================
Server Information:
  - Local IP: 192.168.1.100

RPC Server (for Tkinter GUI):
  - Local:   http://localhost:8000
  - Network: http://192.168.1.100:8000

Flask Web Server (for Browser):
  - Local:   http://localhost:5000
  - Network: http://192.168.1.100:5000

For GUI client from other computer, use:
  SERVER_HOST = "192.168.1.100"
  SERVER_PORT = 8000
======================================================================
```

### 2. Access the System

**Option A: Web Browser**
- Open: `http://localhost:5000`
- Works on any device with browser
- Modern UI with animations

**Option B: Tkinter GUI**
```bash
# On same computer
python client.py

# On different computer (edit client.py first)
# Change: SERVER_HOST = "192.168.1.100"
python client.py
```

## 📁 File Structure

```
St/
├── hybrid_server.py        # ⭐ Main server (RPC + Flask)
├── client.py               # ⭐ Tkinter GUI client (RPC)
├── database.py             # Database operations
├── templates/
│   └── index.html         # Web interface
├── static/
│   ├── css/style.css      # Web styling
│   └── js/app.js          # Web JavaScript
├── cinema_booking.db       # SQLite database
├── requirements.txt        # Dependencies
├── server.py              # Legacy XML-RPC server
└── app.py                 # Legacy Flask-only server
```

⭐ = Main files for hybrid system

## 🔌 RPC API (Port 8000)

### Available RPC Methods

#### `get_movies()`
Get all available movies

**Returns:**
```python
[
    {
        'id': 1,
        'title': 'The Matrix Reloaded',
        'genre': 'Sci-Fi Action',
        'duration': '138 min',
        'showtime': '19:00',
        'poster_emoji': '🎭'
    },
    ...
]
```

#### `get_movie_by_id(movie_id)`
Get specific movie details

**Args:** `movie_id` (int)  
**Returns:** Movie dict or None

#### `get_seat_map(movie_id)`
Get seat map for a movie

**Args:** `movie_id` (int)  
**Returns:** 2D array `[[0,1,0,...], [...], ...]`

#### `book_seat(movie_id, row, col, customer_name, customer_email, customer_phone)`
Book a seat with customer details

**Args:**
- `movie_id` (int)
- `row` (int): 0-4
- `col` (int): 0-4
- `customer_name` (str)
- `customer_email` (str)
- `customer_phone` (str)

**Returns:** `True` if successful, `False` if failed

#### `get_booking_details(movie_id, row, col)`
Get booking information for a seat

**Returns:** Booking dict or None

#### `cancel_booking(movie_id, row, col)`
Cancel a booking

**Returns:** `True` if successful

## 🌐 Flask REST API (Port 5000)

Same endpoints as before:
- `GET /api/movies`
- `GET /api/seats/<movie_id>`
- `POST /api/book`
- `GET /api/booking/<movie_id>/<row>/<col>`
- `POST /api/cancel`
- `POST /api/reset`

## 🖥️ Tkinter GUI Features

### Movie Selection
- Displays all available movies
- Shows movie details (genre, duration, showtime)
- Large emoji icons
- Click to select movie

### Seat Map
- 5×5 grid for selected movie
- Color-coded seats:
  - 🟢 Green = Available
  - 🔴 Red = Booked
- Screen indicator at top
- Row labels for easy navigation

### Booking Form
- Modal dialog for customer details
- Required fields:
  - Full Name
  - Email
  - Phone Number
- Validation before submission
- Success/error messages

### Actions
- **Refresh**: Update seat map
- **Change Movie**: Return to movie selection

## 🔧 Configuration for Remote Access

### Server Side (Your Computer)

1. Find your IP address:
```bash
ipconfig  # Windows
ifconfig  # Linux/Mac
```

2. Run hybrid server:
```bash
python hybrid_server.py
```

3. Note the IP address shown (e.g., `192.168.1.100`)

### Client Side (Other Computer)

1. Edit `client.py`:
```python
# Change this line:
SERVER_HOST = "localhost"

# To your server's IP:
SERVER_HOST = "192.168.1.100"
```

2. Run client:
```bash
python client.py
```

### Firewall Settings

Make sure ports are open:
- **Port 8000**: RPC server
- **Port 5000**: Flask web server

**Windows Firewall:**
```powershell
# Allow port 8000
netsh advfirewall firewall add rule name="RPC Server" dir=in action=allow protocol=TCP localport=8000

# Allow port 5000
netsh advfirewall firewall add rule name="Flask Server" dir=in action=allow protocol=TCP localport=5000
```

## 🔄 How It Works

### 1. Server Initialization
```python
# hybrid_server.py starts both servers
├── Initialize database
├── Start RPC server (port 8000) in background thread
└── Start Flask server (port 5000) in main thread
```

### 2. GUI Client Flow
```
User opens client.py
    ↓
Connect to RPC server (port 8000)
    ↓
Load movies via get_movies()
    ↓
User selects movie
    ↓
Load seats via get_seat_map(movie_id)
    ↓
User clicks available seat
    ↓
Show booking form dialog
    ↓
User fills details and confirms
    ↓
Call book_seat() via RPC
    ↓
Seat updates in database
    ↓
Refresh seat map
```

### 3. Web Client Flow
```
User opens browser to localhost:5000
    ↓
Flask serves index.html
    ↓
JavaScript calls GET /api/movies
    ↓
User selects movie
    ↓
JavaScript calls GET /api/seats/<movie_id>
    ↓
User clicks seat → booking modal
    ↓
User fills form → POST /api/book
    ↓
Flask calls database functions
    ↓
Seat updates in database
    ↓
Auto-refresh every 5 seconds
```

## 🔒 Thread Safety

### RPC Server
- Uses `ThreadingMixIn` for concurrent requests
- Database context managers ensure transaction safety
- Multiple GUI clients can connect simultaneously

### Flask Server
- Built-in threading support
- Same database context managers
- Web and GUI clients share database safely

### Database
- Thread-local connections
- Transaction isolation
- Atomic operations prevent race conditions

## 📊 Example Usage

### Python RPC Client
```python
import xmlrpc.client

# Connect to RPC server
server = xmlrpc.client.ServerProxy("http://192.168.1.100:8000")

# Get movies
movies = server.get_movies()
print(movies)

# Get seats for movie 1
seats = server.get_seat_map(1)
print(seats)

# Book a seat
success = server.book_seat(
    1,  # movie_id
    0, 0,  # row, col
    "John Doe",
    "john@example.com",
    "08123456789"
)
print(f"Booking: {success}")
```

### JavaScript Web Client
```javascript
// Get movies
fetch('/api/movies')
    .then(res => res.json())
    .then(data => console.log(data.movies));

// Book seat
fetch('/api/book', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        movie_id: 1,
        row: 0,
        col: 0,
        customer_name: "John Doe",
        customer_email: "john@example.com",
        customer_phone: "08123456789"
    })
})
.then(res => res.json())
.then(data => console.log(data.message));
```

## 🆚 Comparison: RPC vs REST

| Feature | RPC (GUI) | REST (Web) |
|---------|-----------|------------|
| **Protocol** | XML-RPC | HTTP/JSON |
| **Port** | 8000 | 5000 |
| **Client** | Tkinter GUI | Web Browser |
| **Platform** | Desktop only | Any device |
| **UI** | Native widgets | HTML/CSS/JS |
| **Updates** | Manual refresh | Auto-refresh (5s) |
| **Network** | Same protocol | Standard HTTP |

## 🐛 Troubleshooting

### GUI Can't Connect
```
Error: Cannot connect to server
```
**Solution:**
1. Check server is running
2. Verify IP address in `client.py`
3. Check firewall allows port 8000
4. Ping server: `ping 192.168.1.100`

### Web Can't Load
```
Error: This site can't be reached
```
**Solution:**
1. Check server is running
2. Verify URL: `http://localhost:5000`
3. Check firewall allows port 5000
4. Try server IP: `http://192.168.1.100:5000`

### Port Already in Use
```
Error: Address already in use
```
**Solution:**
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port in code
```

## 📝 Dependencies

```
Flask==3.0.0
Flask-CORS==4.0.0
```

No additional dependencies needed for RPC (built into Python).

## ✨ Advantages of Hybrid Approach

1. **Flexibility**: Users choose GUI or web
2. **Single Server**: One server for both interfaces
3. **Shared Database**: All bookings in one place
4. **Network Ready**: Both support remote access
5. **Thread Safe**: Concurrent access handled properly
6. **Modern + Classic**: Web UI + Desktop GUI

## 🎓 Key Concepts

### Why Hybrid?
- **RPC**: Fast, efficient for desktop apps
- **REST**: Standard for web, works everywhere
- **Both**: Best of both worlds

### Threading Model
- RPC server runs in background thread
- Flask server runs in main thread
- Both share database via thread-safe operations

### Data Consistency
- Single SQLite database
- Transaction-based updates
- Context managers ensure atomicity

## 📄 License

Educational project for learning RPC, Flask, and hybrid architectures.

## 👨‍💻 Author

Created as part of SMS5 course project - Hybrid RPC-Flask Architecture.
