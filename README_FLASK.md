# Cinema Seat Booking System - Flask Web Version

## 🎬 Overview

Modern web-based Cinema Seat Booking System built with Flask, SQLite, and vanilla JavaScript. This is a web integration of the original XML-RPC based system.

## ✨ Features

- **Real-time Seat Updates**: Auto-refresh every 5 seconds
- **Thread-Safe Booking**: SQLite transactions prevent race conditions
- **Data Persistence**: Bookings saved to SQLite database
- **Modern UI**: Dark theme with glassmorphism and smooth animations
- **Responsive Design**: Works on desktop, tablet, and mobile
- **REST API**: Clean API endpoints for integration

## 🚀 Quick Start

### 1. Setup Virtual Environment

```bash
# Create virtual environment
py -3 -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will be available at: **http://localhost:5000**

## 📁 Project Structure

```
St/
├── app.py                  # Flask application & API endpoints
├── database.py             # SQLite database operations
├── requirements.txt        # Python dependencies
├── cinema_booking.db       # SQLite database (auto-created)
├── templates/
│   └── index.html         # Web interface
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── app.js         # Frontend logic
├── server.py              # Legacy XML-RPC server
└── client.py              # Legacy Tkinter client
```

## 🔌 API Endpoints

### GET /api/seats
Get all seats status

**Response:**
```json
{
  "success": true,
  "seats": [[0,1,0,0,0], [0,0,1,0,0], ...]
}
```

### POST /api/book
Book a seat

**Request:**
```json
{
  "row": 0,
  "col": 0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Seat (0, 0) booked successfully!"
}
```

### POST /api/cancel
Cancel a booking

**Request:**
```json
{
  "row": 0,
  "col": 0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Booking for seat (0, 0) cancelled!"
}
```

### POST /api/reset
Reset all seats (admin function)

**Response:**
```json
{
  "success": true,
  "message": "All seats have been reset!"
}
```

## 🔒 Thread Safety & Concurrency

### Database Level
- **Thread-local connections**: Each thread gets its own database connection
- **Transaction isolation**: SQLite transactions ensure atomic operations
- **Context managers**: Automatic commit/rollback handling

### Application Level
- **Flask threading**: Built-in support for concurrent requests
- **CORS enabled**: Cross-origin requests supported

### Race Condition Prevention

```python
# Scenario: 2 clients try to book the same seat
Client A                    Client B
---------                   ---------
POST /api/book (0,0)       POST /api/book (0,0)
  BEGIN TRANSACTION          (waits for lock)
  SELECT status = 0 ✓
  UPDATE status = 1 ✓
  COMMIT ✓
                            BEGIN TRANSACTION
                            SELECT status = 1 ✗
                            return False ✓
                            COMMIT ✓
```

## 🆚 Comparison: XML-RPC vs Flask

| Feature | XML-RPC (Legacy) | Flask (New) |
|---------|------------------|-------------|
| Interface | Tkinter GUI | Web Browser |
| Protocol | XML-RPC | REST API |
| Data Storage | In-memory | SQLite |
| Persistence | ❌ No | ✅ Yes |
| Threading | ThreadingMixIn + Lock | SQLite Transactions |
| Cancel Booking | ❌ No | ✅ Yes |
| Reset Seats | ❌ No | ✅ Yes |
| Auto-refresh | Manual | Every 5 seconds |
| Mobile Support | ❌ No | ✅ Yes |

## 🎨 UI Features

- **Dark Theme**: Modern dark color scheme
- **Glassmorphism**: Frosted glass effects
- **Smooth Animations**: Hover effects and transitions
- **Color Coding**: 
  - 🟢 Green = Available
  - 🔴 Red = Booked
- **Responsive**: Adapts to all screen sizes

## 🧪 Testing

### Manual Testing

1. **Single Booking**:
   - Open http://localhost:5000
   - Click any green seat
   - Confirm booking
   - Verify seat turns red

2. **Concurrent Bookings**:
   - Open 2 browser tabs
   - Both try to book the same seat
   - Only one should succeed

3. **Data Persistence**:
   - Book some seats
   - Stop the server (Ctrl+C)
   - Restart the server
   - Verify bookings are still there

4. **Auto-refresh**:
   - Open 2 browser tabs
   - Book a seat in tab 1
   - Wait 5 seconds
   - Verify tab 2 updates automatically

### API Testing (curl)

```bash
# Get seats
curl http://localhost:5000/api/seats

# Book a seat
curl -X POST http://localhost:5000/api/book \
  -H "Content-Type: application/json" \
  -d '{"row": 0, "col": 0}'

# Cancel booking
curl -X POST http://localhost:5000/api/cancel \
  -H "Content-Type: application/json" \
  -d '{"row": 0, "col": 0}'

# Reset all
curl -X POST http://localhost:5000/api/reset
```

## 🔧 Configuration

### Change Port

Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port here
```

### Database File

Edit `database.py`:
```python
DATABASE_NAME = "cinema_booking.db"  # Change database name
```

### Auto-refresh Interval

Edit `static/js/app.js`:
```javascript
setInterval(refreshSeats, 5000);  // Change interval (milliseconds)
```

## 📝 Development Notes

### Adding More Seats

To change from 5x5 to 10x10:

1. Edit `database.py` - `init_database()`:
```python
for row in range(10):  # Change to 10
    for col in range(10):  # Change to 10
```

2. Edit `database.py` - `get_all_seats()`:
```python
seat_map = [[0 for _ in range(10)] for _ in range(10)]
```

3. Edit `database.py` - validation:
```python
if not (0 <= row < 10 and 0 <= col < 10):
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows: Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

### Database Locked
- Close all connections
- Delete `cinema_booking.db` and restart

### Virtual Environment Issues
```bash
# Deactivate and recreate
deactivate
rm -rf .venv
py -3 -m venv .venv
```

## 📄 License

Educational project for learning Flask, SQLite, and web development.

## 👨‍💻 Author

Created as part of SMS5 course project.
