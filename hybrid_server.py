"""
Cinema Booking System - Hybrid RPC + Flask Server
Combines XML-RPC server for GUI clients with Flask web interface
"""

from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import threading
import database
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import socket

# ============================================================
# RPC SERVER CLASS
# ============================================================

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    """Multi-threaded XML-RPC server"""
    pass

class CinemaBookingRPC:
    """RPC methods for Tkinter GUI clients"""
    
    def __init__(self):
        print("[RPC] Cinema Booking RPC initialized")
    
    # ========== Movie Methods ==========
    
    def get_movies(self):
        """
        Get all available movies
        Returns: List of movie dictionaries
        """
        print("[RPC] get_movies() called")
        return database.get_movies()
    
    def get_movie_by_id(self, movie_id):
        """
        Get specific movie details
        Args:
            movie_id (int): Movie ID
        Returns: Movie dictionary or None
        """
        print(f"[RPC] get_movie_by_id({movie_id}) called")
        movies = database.get_movies()
        for movie in movies:
            if movie['id'] == movie_id:
                return movie
        return None
    
    # ========== Seat Methods ==========
    
    def get_seat_map(self, movie_id):
        """
        Get seat map for specific movie
        Args:
            movie_id (int): Movie ID
        Returns: 2D array of seat status
        """
        print(f"[RPC] get_seat_map({movie_id}) called")
        return database.get_seats_by_movie(movie_id)
    
    # ========== Booking Methods ==========
    
    def book_seat(self, movie_id, row, col, customer_name, customer_email, customer_phone):
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
            bool: True if booking successful
        """
        print(f"[RPC] book_seat({movie_id}, {row}, {col}, {customer_name}) called")
        return database.book_seat(movie_id, row, col, customer_name, customer_email, customer_phone)
    
    def get_booking_details(self, movie_id, row, col):
        """
        Get booking details for a seat
        
        Args:
            movie_id (int): Movie ID
            row (int): Row number
            col (int): Column number
        
        Returns:
            dict: Booking details or None
        """
        print(f"[RPC] get_booking_details({movie_id}, {row}, {col}) called")
        return database.get_booking_details(movie_id, row, col)
    
    def cancel_booking(self, movie_id, row, col):
        """
        Cancel a booking
        
        Args:
            movie_id (int): Movie ID
            row (int): Row number
            col (int): Column number
        
        Returns:
            bool: True if cancellation successful
        """
        print(f"[RPC] cancel_booking({movie_id}, {row}, {col}) called")
        return database.cancel_booking(movie_id, row, col)

# ============================================================
# FLASK WEB SERVER
# ============================================================

app = Flask(__name__)
CORS(app)

# Web routes
@app.route('/')
def index():
    return render_template('index.html')

# API endpoints (same as before)
@app.route('/api/movies', methods=['GET'])
def get_movies():
    try:
        movies = database.get_movies()
        return jsonify({"success": True, "movies": movies})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/seats/<int:movie_id>', methods=['GET'])
def get_seats(movie_id):
    try:
        seat_map = database.get_seats_by_movie(movie_id)
        return jsonify({"success": True, "seats": seat_map})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/book', methods=['POST'])
def book_seat():
    try:
        data = request.get_json()
        movie_id = data.get('movie_id')
        row = data.get('row')
        col = data.get('col')
        customer_name = data.get('customer_name')
        customer_email = data.get('customer_email')
        customer_phone = data.get('customer_phone')
        
        if not all([movie_id, row is not None, col is not None, customer_name, customer_email, customer_phone]):
            return jsonify({"success": False, "message": "All fields are required"}), 400
        
        success = database.book_seat(movie_id, row, col, customer_name, customer_email, customer_phone)
        
        if success:
            return jsonify({"success": True, "message": f"Seat booked successfully for {customer_name}!"})
        else:
            return jsonify({"success": False, "message": "Seat already booked or invalid position"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/booking/<int:movie_id>/<int:row>/<int:col>', methods=['GET'])
def get_booking(movie_id, row, col):
    try:
        booking = database.get_booking_details(movie_id, row, col)
        if booking:
            return jsonify({"success": True, "booking": booking})
        else:
            return jsonify({"success": False, "message": "No booking found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/cancel', methods=['POST'])
def cancel_seat():
    try:
        data = request.get_json()
        movie_id = data.get('movie_id')
        row = data.get('row')
        col = data.get('col')
        
        if movie_id is None or row is None or col is None:
            return jsonify({"success": False, "message": "Movie ID, row and column are required"}), 400
        
        success = database.cancel_booking(movie_id, row, col)
        
        if success:
            return jsonify({"success": True, "message": "Booking cancelled successfully!"})
        else:
            return jsonify({"success": False, "message": "Seat is not booked or invalid position"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_seats():
    try:
        database.reset_all_seats()
        return jsonify({"success": True, "message": "All seats have been reset!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ============================================================
# MAIN - RUN BOTH SERVERS
# ============================================================

def run_rpc_server():
    """Run RPC server in separate thread"""
    RPC_HOST = "0.0.0.0"
    RPC_PORT = 8000
    
    rpc_server = ThreadedXMLRPCServer((RPC_HOST, RPC_PORT), allow_none=True)
    booking_rpc = CinemaBookingRPC()
    
    # Register RPC methods
    rpc_server.register_function(booking_rpc.get_movies, "get_movies")
    rpc_server.register_function(booking_rpc.get_movie_by_id, "get_movie_by_id")
    rpc_server.register_function(booking_rpc.get_seat_map, "get_seat_map")
    rpc_server.register_function(booking_rpc.book_seat, "book_seat")
    rpc_server.register_function(booking_rpc.get_booking_details, "get_booking_details")
    rpc_server.register_function(booking_rpc.cancel_booking, "cancel_booking")
    
    print("[RPC] XML-RPC server started on port 8000")
    rpc_server.serve_forever()

def main():
    # Initialize database
    database.init_database()
    
    # Get IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("=" * 70)
    print("Cinema Seat Booking - Hybrid RPC + Flask Server")
    print("=" * 70)
    print("Server Information:")
    print(f"  - Local IP: {local_ip}")
    print()
    print("RPC Server (for Tkinter GUI):")
    print(f"  - Local:   http://localhost:8000")
    print(f"  - Network: http://{local_ip}:8000")
    print()
    print("Flask Web Server (for Browser):")
    print(f"  - Local:   http://localhost:5000")
    print(f"  - Network: http://{local_ip}:5000")
    print()
    print("For GUI client from other computer, use:")
    print(f"  SERVER_HOST = \"{local_ip}\"")
    print(f"  SERVER_PORT = 8000")
    print("=" * 70)
    
    # Start RPC server in background thread
    rpc_thread = threading.Thread(target=run_rpc_server, daemon=True)
    rpc_thread.start()
    
    # Start Flask server in main thread
    print("[Flask] Starting Flask web server on port 5000...")
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == '__main__':
    main()
