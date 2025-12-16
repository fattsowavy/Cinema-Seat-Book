"""
Cinema Booking System - Database Module
Handles SQLite database operations with thread-safe transactions
"""

import sqlite3
import threading
from contextlib import contextmanager

DATABASE_NAME = "cinema_booking.db"

# Thread-local storage untuk database connections
thread_local = threading.local()

def get_db_connection():
    """
    Get thread-local database connection
    Setiap thread mendapat connection sendiri untuk thread safety
    """
    if not hasattr(thread_local, 'connection'):
        thread_local.connection = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
        thread_local.connection.row_factory = sqlite3.Row
    return thread_local.connection

@contextmanager
def get_db():
    """
    Context manager untuk database operations
    Ensures proper transaction handling dan cleanup
    """
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def init_database():
    """
    Initialize database schema
    Creates movies, seats, and bookings tables if not exists
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create movies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                genre TEXT NOT NULL,
                duration TEXT NOT NULL,
                showtime TEXT NOT NULL,
                poster_emoji TEXT NOT NULL
            )
        """)
        
        # Create seats table (modified to include movie_id)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seats (
                movie_id INTEGER NOT NULL,
                row INTEGER NOT NULL,
                col INTEGER NOT NULL,
                status INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (movie_id, row, col),
                FOREIGN KEY (movie_id) REFERENCES movies(id)
            )
        """)
        
        # Create bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                row INTEGER NOT NULL,
                col INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (movie_id) REFERENCES movies(id)
            )
        """)
        
        # Initialize movies if empty
        cursor.execute("SELECT COUNT(*) as count FROM movies")
        if cursor.fetchone()['count'] == 0:
            print("[INFO] Initializing movies...")
            movies_data = [
                ("The Matrix Reloaded", "Sci-Fi Action", "138 min", "19:00", "🎭"),
                ("Inception", "Sci-Fi Thriller", "148 min", "21:00", "🌀")
            ]
            cursor.executemany(
                "INSERT INTO movies (title, genre, duration, showtime, poster_emoji) VALUES (?, ?, ?, ?, ?)",
                movies_data
            )
            print("[INFO] 2 movies initialized")
        
        # Initialize seats for each movie if empty
        cursor.execute("SELECT COUNT(*) as count FROM seats")
        if cursor.fetchone()['count'] == 0:
            print("[INFO] Initializing seat grids for all movies...")
            cursor.execute("SELECT id FROM movies")
            movie_ids = [row['id'] for row in cursor.fetchall()]
            
            for movie_id in movie_ids:
                for row in range(5):
                    for col in range(5):
                        cursor.execute(
                            "INSERT INTO seats (movie_id, row, col, status) VALUES (?, ?, ?, ?)",
                            (movie_id, row, col, 0)
                        )
            print(f"[INFO] Initialized {len(movie_ids)} x 25 seats")

def get_movies():
    """
    Get all available movies
    Returns: List of movie dictionaries
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movies ORDER BY id")
        movies = []
        for row in cursor.fetchall():
            movies.append({
                'id': row['id'],
                'title': row['title'],
                'genre': row['genre'],
                'duration': row['duration'],
                'showtime': row['showtime'],
                'poster_emoji': row['poster_emoji']
            })
        return movies

def get_seats_by_movie(movie_id):
    """
    Get all seats for a specific movie as 2D array
    Args:
        movie_id (int): Movie ID
    Returns: List[List[int]] - 5x5 matrix
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT row, col, status FROM seats WHERE movie_id = ? ORDER BY row, col",
            (movie_id,)
        )
        
        # Convert to 2D array
        seat_map = [[0 for _ in range(5)] for _ in range(5)]
        for seat in cursor.fetchall():
            seat_map[seat['row']][seat['col']] = seat['status']
        
        return seat_map

def get_all_seats():
    """
    Get all seats for first movie (backward compatibility)
    Returns: List[List[int]] - 5x5 matrix
    """
    return get_seats_by_movie(1)

def book_seat(movie_id, row, col, customer_name, customer_email, customer_phone):
    """
    Book a seat with customer details
    
    Args:
        movie_id (int): Movie ID
        row (int): Row number (0-4)
        col (int): Column number (0-4)
        customer_name (str): Customer name
        customer_email (str): Customer email
        customer_phone (str): Customer phone
    
    Returns:
        bool: True if booking successful, False otherwise
    """
    # Validate input
    if not (0 <= row < 5 and 0 <= col < 5):
        print(f"[ERROR] Invalid seat position: ({row}, {col})")
        return False
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if seat is available
        cursor.execute(
            "SELECT status FROM seats WHERE movie_id = ? AND row = ? AND col = ?",
            (movie_id, row, col)
        )
        result = cursor.fetchone()
        
        if result and result['status'] == 0:
            # Seat available, book it
            cursor.execute(
                "UPDATE seats SET status = 1 WHERE movie_id = ? AND row = ? AND col = ?",
                (movie_id, row, col)
            )
            
            # Create booking record
            cursor.execute(
                """INSERT INTO bookings (movie_id, row, col, customer_name, customer_email, customer_phone)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (movie_id, row, col, customer_name, customer_email, customer_phone)
            )
            print(f"[SUCCESS] Seat ({row}, {col}) booked successfully")
            return True
        else:
            print(f"[FAILED] Seat ({row}, {col}) already booked")
            return False

def get_booking_details(movie_id, row, col):
    """
    Get booking details for a specific seat
    
    Args:
        movie_id (int): Movie ID
        row (int): Row number (0-4)
        col (int): Column number (0-4)
    
    Returns:
        dict: Booking details or None
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT b.*, m.title as movie_title 
               FROM bookings b 
               JOIN movies m ON b.movie_id = m.id 
               WHERE b.movie_id = ? AND b.row = ? AND b.col = ?""",
            (movie_id, row, col)
        )
        result = cursor.fetchone()
        if result:
            return {
                'id': result['id'],
                'movie_id': result['movie_id'],
                'movie_title': result['movie_title'],
                'row': result['row'],
                'col': result['col'],
                'customer_name': result['customer_name'],
                'customer_email': result['customer_email'],
                'customer_phone': result['customer_phone'],
                'booking_time': result['booking_time']
            }
        return None

def cancel_booking(movie_id, row, col):
    """
    Cancel a booking at position (row, col) for a specific movie
    
    Args:
        movie_id (int): Movie ID
        row (int): Row number (0-4)
        col (int): Column number (0-4)
    
    Returns:
        bool: True if cancellation successful, False otherwise
    """
    if not (0 <= row < 5 and 0 <= col < 5):
        print(f"[ERROR] Invalid seat position: ({row}, {col})")
        return False
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT status FROM seats WHERE movie_id = ? AND row = ? AND col = ?",
            (movie_id, row, col)
        )
        result = cursor.fetchone()
        
        if result and result['status'] == 1:
            # Seat is booked, cancel it
            cursor.execute(
                "UPDATE seats SET status = 0 WHERE movie_id = ? AND row = ? AND col = ?",
                (movie_id, row, col)
            )
            
            # Delete booking record
            cursor.execute(
                "DELETE FROM bookings WHERE movie_id = ? AND row = ? AND col = ?",
                (movie_id, row, col)
            )
            print(f"[SUCCESS] Booking for seat ({row}, {col}) cancelled")
            return True
        else:
            print(f"[FAILED] Seat ({row}, {col}) is not booked")
            return False

def reset_all_seats():
    """
    Reset all seats to available (admin function)
    
    Returns:
        bool: True if reset successful
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE seats SET status = 0, booked_at = NULL")
        print("[INFO] All seats reset to available")
        return True

if __name__ == "__main__":
    # Test database operations
    print("Initializing database...")
    init_database()
    
    print("\nCurrent seat map:")
    seat_map = get_all_seats()
    for row in seat_map:
        print(row)
    
    print("\nTesting booking...")
    print(f"Book (0,0): {book_seat(0, 0)}")
    print(f"Book (0,0) again: {book_seat(0, 0)}")
    print(f"Book (1,1): {book_seat(1, 1)}")
    
    print("\nSeat map after booking:")
    seat_map = get_all_seats()
    for row in seat_map:
        print(row)
