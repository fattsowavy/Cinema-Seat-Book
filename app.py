"""
Cinema Booking System - Flask Web Application
REST API untuk booking kursi bioskop dengan web interface dan movie selection
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import database
import os

app = Flask(__name__)
CORS(app)  # Enable CORS untuk API access

# Initialize database saat startup
database.init_database()

# ============================================================
# WEB ROUTES
# ============================================================

@app.route('/')
def index():
    """Render main web interface"""
    return render_template('index.html')

# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """
    Get all available movies
    
    Returns:
        JSON: {
            "success": true,
            "movies": [{id, title, genre, duration, showtime, poster_emoji}, ...]
        }
    """
    try:
        movies = database.get_movies()
        return jsonify({
            "success": True,
            "movies": movies
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/seats/<int:movie_id>', methods=['GET'])
def get_seats(movie_id):
    """
    Get all seats for a specific movie
    
    Args:
        movie_id: Movie ID from URL
    
    Returns:
        JSON: {
            "success": true,
            "seats": [[0,1,0,...], [...], ...]
        }
    """
    try:
        seat_map = database.get_seats_by_movie(movie_id)
        return jsonify({
            "success": True,
            "seats": seat_map
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/book', methods=['POST'])
def book_seat():
    """
    Book a seat with customer details
    
    Request Body:
        {
            "movie_id": 1,
            "row": 0,
            "col": 0,
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "customer_phone": "08123456789"
        }
    
    Returns:
        JSON: {
            "success": true/false,
            "message": "..."
        }
    """
    try:
        data = request.get_json()
        movie_id = data.get('movie_id')
        row = data.get('row')
        col = data.get('col')
        customer_name = data.get('customer_name')
        customer_email = data.get('customer_email')
        customer_phone = data.get('customer_phone')
        
        # Validation
        if not all([movie_id, row is not None, col is not None, customer_name, customer_email, customer_phone]):
            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400
        
        success = database.book_seat(movie_id, row, col, customer_name, customer_email, customer_phone)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Seat booked successfully for {customer_name}!"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Seat already booked or invalid position"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/booking/<int:movie_id>/<int:row>/<int:col>', methods=['GET'])
def get_booking(movie_id, row, col):
    """
    Get booking details for a specific seat
    
    Returns:
        JSON: {
            "success": true,
            "booking": {...}
        }
    """
    try:
        booking = database.get_booking_details(movie_id, row, col)
        if booking:
            return jsonify({
                "success": True,
                "booking": booking
            })
        else:
            return jsonify({
                "success": False,
                "message": "No booking found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/cancel', methods=['POST'])
def cancel_seat():
    """
    Cancel a booking
    
    Request Body:
        {
            "movie_id": 1,
            "row": 0,
            "col": 0
        }
    
    Returns:
        JSON: {
            "success": true/false,
            "message": "..."
        }
    """
    try:
        data = request.get_json()
        movie_id = data.get('movie_id')
        row = data.get('row')
        col = data.get('col')
        
        if movie_id is None or row is None or col is None:
            return jsonify({
                "success": False,
                "message": "Movie ID, row and column are required"
            }), 400
        
        success = database.cancel_booking(movie_id, row, col)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Booking cancelled successfully!"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Seat is not booked or invalid position"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_seats():
    """
    Reset all seats (admin function)
    
    Returns:
        JSON: {
            "success": true,
            "message": "..."
        }
    """
    try:
        database.reset_all_seats()
        return jsonify({
            "success": True,
            "message": "All seats have been reset!"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Cinema Seat Booking - Flask Web Server")
    print("=" * 60)
    print("Server running on: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
