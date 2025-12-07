"""
Cinema Seat Booking System - Client
GUI menggunakan Tkinter untuk visualisasi dan booking kursi
"""

import tkinter as tk
from tkinter import messagebox
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
        self.root.title("Cinema Seat Booking System")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Koneksi ke RPC Server
        try:
            self.server = xmlrpc.client.ServerProxy("http://localhost:8000")
            print("[INFO] Connected to server")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
            self.root.destroy()
            return
        
        # Matriks untuk menyimpan button widgets
        self.seat_buttons = [[None for _ in range(5)] for _ in range(5)]
        
        # Setup UI
        self.setup_ui()
        
        # Load initial seat map
        self.refresh_seats()
    
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
        
        # Screen indicator
        screen_frame = tk.Frame(self.root, bg="white", height=60)
        screen_frame.pack(fill=tk.X, pady=20)
        
        screen_label = tk.Label(
            screen_frame,
            text="🎥 SCREEN",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#34495e"
        )
        screen_label.pack(pady=15)
        
        # Seat grid container
        grid_frame = tk.Frame(self.root, bg="white")
        grid_frame.pack(pady=20)
        
        # Create 5x5 grid of buttons
        for row in range(5):
            row_frame = tk.Frame(grid_frame, bg="white")
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
                btn = tk.Button(
                    row_frame,
                    text=f"{row}-{col}",
                    font=("Arial", 10, "bold"),
                    width=8,
                    height=3,
                    command=lambda r=row, c=col: self.book_seat(r, c)
                )
                btn.pack(side=tk.LEFT, padx=5)
                self.seat_buttons[row][col] = btn
        
        # Legend
        legend_frame = tk.Frame(self.root, bg="white")
        legend_frame.pack(pady=20)
        
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
        
        # Refresh button
        refresh_btn = tk.Button(
            self.root,
            text="🔄 Refresh Seat Map",
            font=("Arial", 14, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            width=20,
            height=2,
            command=self.refresh_seats,
            cursor="hand2"
        )
        refresh_btn.pack(pady=20)
    
    def refresh_seats(self):
        """
        Memanggil RPC get_seat_map() dan update warna tombol
        """
        try:
            # Panggil fungsi RPC
            seat_map = self.server.get_seat_map()
            
            # Update warna dan status setiap tombol
            for row in range(5):
                for col in range(5):
                    status = seat_map[row][col]
                    btn = self.seat_buttons[row][col]
                    
                    if status == 0:  # Available
                        btn.config(
                            bg="#2ecc71",  # Hijau
                            fg="white",
                            state=tk.NORMAL,
                            activebackground="#27ae60"
                        )
                    else:  # Booked
                        btn.config(
                            bg="#e74c3c",  # Merah
                            fg="white",
                            state=tk.DISABLED
                        )
            
            print("[INFO] Seat map refreshed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh seat map: {e}")
    
    def book_seat(self, row, col):
        """
        Melakukan booking kursi dengan memanggil RPC book_seat()
        
        Args:
            row (int): Nomor baris
            col (int): Nomor kolom
        """
        # Konfirmasi booking
        confirm = messagebox.askyesno(
            "Confirm Booking",
            f"Do you want to book seat at Row {row + 1}, Column {col + 1}?"
        )
        
        if not confirm:
            return
        
        try:
            # Panggil fungsi RPC book_seat
            success = self.server.book_seat(row, col)
            
            if success:
                # Booking sukses
                messagebox.showinfo(
                    "Success",
                    f"Seat Row {row + 1}, Column {col + 1} booked successfully! ✅"
                )
                # Refresh untuk update tampilan
                self.refresh_seats()
            else:
                # Booking gagal (kursi sudah diambil)
                messagebox.showerror(
                    "Booking Failed",
                    "Kursi sudah diambil! ❌\n\nSomeone else booked this seat first."
                )
                # Refresh untuk update tampilan
                self.refresh_seats()
        
        except Exception as e:
            messagebox.showerror("Error", f"Booking error: {e}")

def main():
    root = tk.Tk()
    app = CinemaBookingClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()
