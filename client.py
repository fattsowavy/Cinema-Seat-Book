"""
Cinema Seat Booking System - Tkinter GUI Client
Connects to RPC server with movie selection and booking form
Can be run from any computer on the network
"""

import tkinter as tk
from tkinter import messagebox, ttk
import xmlrpc.client

# ============================================================
# KONFIGURASI SERVER
# ============================================================
# Untuk koneksi LOKAL (komputer yang sama):
SERVER_HOST = "localhost"

# Untuk koneksi dari KOMPUTER LAIN di jaringan yang sama:
# Ganti "localhost" dengan IP address komputer server
# Contoh: SERVER_HOST = "192.168.1.100"
# ============================================================

SERVER_PORT = 8000

class CinemaBookingClient:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Cinema Seat Booking System")
        self.root.geometry("700x800")
        self.root.resizable(False, False)
        
        # Koneksi ke RPC Server
        try:
            self.server = xmlrpc.client.ServerProxy(f"http://{SERVER_HOST}:{SERVER_PORT}")
            print(f"[INFO] Connected to RPC server at {SERVER_HOST}:{SERVER_PORT}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
            self.root.destroy()
            return
        
        # State
        self.movies = []
        self.selected_movie = None
        self.seat_buttons = [[None for _ in range(5)] for _ in range(5)]
        
        # Setup UI
        self.setup_ui()
        
        # Load movies
        self.load_movies()
    
    def setup_ui(self):
        """Setup UI components"""
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🎬 Cinema Seat Booking System",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Movie selection frame
        self.movie_frame = tk.Frame(self.root, bg="white")
        self.movie_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        movie_label = tk.Label(
            self.movie_frame,
            text="Select a Movie",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        movie_label.pack(pady=10)
        
        self.movie_list_frame = tk.Frame(self.movie_frame, bg="white")
        self.movie_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Seat selection frame (hidden initially)
        self.seat_frame = tk.Frame(self.root, bg="white")
        
        # Screen indicator
        screen_frame = tk.Frame(self.seat_frame, bg="white", height=60)
        screen_frame.pack(fill=tk.X, pady=10)
        
        screen_label = tk.Label(
            screen_frame,
            text="🎥 SCREEN",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#34495e"
        )
        screen_label.pack(pady=15)
        
        # Seat grid container
        self.grid_frame = tk.Frame(self.seat_frame, bg="white")
        self.grid_frame.pack(pady=10)
        
        # Legend
        legend_frame = tk.Frame(self.seat_frame, bg="white")
        legend_frame.pack(pady=10)
        
        available_label = tk.Label(
            legend_frame,
            text="🟢 Available",
            font=("Arial", 12),
            bg="white"
        )
        available_label.pack(side=tk.LEFT, padx=20)
        
        booked_label = tk.Label(
            legend_frame,
            text="🔴 Booked",
            font=("Arial", 12),
            bg="white"
        )
        booked_label.pack(side=tk.LEFT, padx=20)
        
        # Action buttons
        action_frame = tk.Frame(self.seat_frame, bg="white")
        action_frame.pack(pady=10)
        
        refresh_btn = tk.Button(
            action_frame,
            text="🔄 Refresh",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            width=15,
            height=2,
            command=self.refresh_seats,
            cursor="hand2"
        )
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        change_movie_btn = tk.Button(
            action_frame,
            text="🎬 Change Movie",
            font=("Arial", 12, "bold"),
            bg="#9b59b6",
            fg="white",
            width=15,
            height=2,
            command=self.change_movie,
            cursor="hand2"
        )
        change_movie_btn.pack(side=tk.LEFT, padx=10)
    
    def load_movies(self):
        """Load movies from RPC server"""
        try:
            self.movies = self.server.get_movies()
            self.display_movies()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load movies: {e}")
    
    def display_movies(self):
        """Display movie selection cards"""
        # Clear existing
        for widget in self.movie_list_frame.winfo_children():
            widget.destroy()
        
        for movie in self.movies:
            movie_card = tk.Frame(
                self.movie_list_frame,
                bg="#ecf0f1",
                relief=tk.RAISED,
                borderwidth=2
            )
            movie_card.pack(fill=tk.X, padx=10, pady=10)
            
            # Emoji
            emoji_label = tk.Label(
                movie_card,
                text=movie['poster_emoji'],
                font=("Arial", 40),
                bg="#ecf0f1"
            )
            emoji_label.pack(pady=10)
            
            # Title
            title_label = tk.Label(
                movie_card,
                text=movie['title'],
                font=("Arial", 16, "bold"),
                bg="#ecf0f1"
            )
            title_label.pack()
            
            # Details
            details_text = f"{movie['genre']} • {movie['duration']} • {movie['showtime']}"
            details_label = tk.Label(
                movie_card,
                text=details_text,
                font=("Arial", 10),
                bg="#ecf0f1",
                fg="#7f8c8d"
            )
            details_label.pack(pady=5)
            
            # Select button
            select_btn = tk.Button(
                movie_card,
                text="Select This Movie",
                font=("Arial", 12, "bold"),
                bg="#27ae60",
                fg="white",
                command=lambda m=movie: self.select_movie(m),
                cursor="hand2"
            )
            select_btn.pack(pady=10)
    
    def select_movie(self, movie):
        """Select a movie and show seat map"""
        self.selected_movie = movie
        
        # Hide movie selection, show seat selection
        self.movie_frame.pack_forget()
        self.seat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Update title
        self.root.title(f"🎬 {movie['title']} - Seat Booking")
        
        # Load seats
        self.refresh_seats()
    
    def change_movie(self):
        """Go back to movie selection"""
        self.selected_movie = None
        
        # Hide seat selection, show movie selection
        self.seat_frame.pack_forget()
        self.movie_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Reset title
        self.root.title("🎬 Cinema Seat Booking System")
    
    def refresh_seats(self):
        """Load and display seat map for selected movie"""
        if not self.selected_movie:
            return
        
        try:
            # Clear existing grid
            for widget in self.grid_frame.winfo_children():
                widget.destroy()
            
            # Get seat map from RPC
            seat_map = self.server.get_seat_map(self.selected_movie['id'])
            
            # Create 5x5 grid
            for row in range(5):
                row_frame = tk.Frame(self.grid_frame, bg="white")
                row_frame.pack(pady=5)
                
                # Row label
                row_label = tk.Label(
                    row_frame,
                    text=f"Row {row + 1}",
                    font=("Arial", 12, "bold"),
                    bg="white",
                    width=8
                )
                row_label.pack(side=tk.LEFT, padx=10)
                
                for col in range(5):
                    status = seat_map[row][col]
                    btn = tk.Button(
                        row_frame,
                        text=f"{row}-{col}",
                        font=("Arial", 10, "bold"),
                        width=8,
                        height=3,
                        command=lambda r=row, c=col: self.book_seat(r, c)
                    )
                    
                    if status == 0:  # Available
                        btn.config(
                            bg="#2ecc71",
                            fg="white",
                            state=tk.NORMAL,
                            activebackground="#27ae60"
                        )
                    else:  # Booked
                        btn.config(
                            bg="#e74c3c",
                            fg="white",
                            state=tk.DISABLED
                        )
                    
                    btn.pack(side=tk.LEFT, padx=5)
                    self.seat_buttons[row][col] = btn
            
            print("[INFO] Seat map refreshed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh seat map: {e}")
    
    def book_seat(self, row, col):
        """Book a seat with customer details"""
        if not self.selected_movie:
            messagebox.showerror("Error", "Please select a movie first")
            return
        
        # Show booking form dialog
        self.show_booking_form(row, col)
    
    def show_booking_form(self, row, col):
        """Show booking form dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Complete Your Booking")
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header
        header = tk.Label(
            dialog,
            text="📝 Booking Information",
            font=("Arial", 16, "bold"),
            bg="#3498db",
            fg="white",
            pady=15
        )
        header.pack(fill=tk.X)
        
        # Info frame
        info_frame = tk.Frame(dialog, bg="#ecf0f1", pady=10)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            info_frame,
            text=f"Movie: {self.selected_movie['title']}",
            font=("Arial", 11),
            bg="#ecf0f1"
        ).pack()
        
        tk.Label(
            info_frame,
            text=f"Seat: Row {row + 1}, Column {col + 1}",
            font=("Arial", 11),
            bg="#ecf0f1"
        ).pack()
        
        # Form frame
        form_frame = tk.Frame(dialog, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Name
        tk.Label(form_frame, text="Full Name *", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W, pady=(10, 0))
        name_entry = tk.Entry(form_frame, font=("Arial", 11), width=35)
        name_entry.pack(pady=(0, 10))
        
        # Email
        tk.Label(form_frame, text="Email *", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        email_entry = tk.Entry(form_frame, font=("Arial", 11), width=35)
        email_entry.pack(pady=(0, 10))
        
        # Phone
        tk.Label(form_frame, text="Phone Number *", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        phone_entry = tk.Entry(form_frame, font=("Arial", 11), width=35)
        phone_entry.pack(pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(dialog, bg="white")
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def submit_booking():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()
            
            if not name or not email or not phone:
                messagebox.showerror("Error", "Please fill all fields", parent=dialog)
                return
            
            try:
                # Call RPC method
                success = self.server.book_seat(
                    self.selected_movie['id'],
                    row, col,
                    name, email, phone
                )
                
                if success:
                    messagebox.showinfo(
                        "Success",
                        f"Seat booked successfully for {name}! ✅",
                        parent=dialog
                    )
                    dialog.destroy()
                    self.refresh_seats()
                else:
                    messagebox.showerror(
                        "Booking Failed",
                        "Seat already booked! ❌\n\nSomeone else booked this seat first.",
                        parent=dialog
                    )
                    dialog.destroy()
                    self.refresh_seats()
            except Exception as e:
                messagebox.showerror("Error", f"Booking error: {e}", parent=dialog)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            width=12,
            command=dialog.destroy,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        confirm_btn = tk.Button(
            button_frame,
            text="Confirm Booking",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            width=15,
            command=submit_booking,
            cursor="hand2"
        )
        confirm_btn.pack(side=tk.RIGHT, padx=5)

def main():
    root = tk.Tk()
    app = CinemaBookingClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()
