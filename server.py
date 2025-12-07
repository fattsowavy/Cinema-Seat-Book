"""
Cinema Seat Booking System - Server
Menggunakan XML-RPC dengan Threading untuk mendukung multiple clients
"""

from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import threading

# Threading Mix-in untuk mendukung multi-threaded requests
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class CinemaBookingSystem:
    def __init__(self):
        # Matriks 5x5 untuk menyimpan status kursi
        # 0 = Available (Kosong), 1 = Booked (Terisi)
        self.seat_map = [[0 for _ in range(5)] for _ in range(5)]
        
        # Lock untuk mencegah race condition
        # Lock memastikan hanya 1 thread yang bisa mengakses critical section
        self.lock = threading.Lock()
        
        print("Cinema Booking System initialized")
        print("Seat map (5x5): All seats available")
    
    def get_seat_map(self):
        """
        Mengembalikan status semua kursi dalam bentuk list 2D
        Returns: List[List[int]] - Matriks 5x5 dengan status kursi
        """
        print(f"[INFO] get_seat_map() called by client")
        return self.seat_map
    
    def book_seat(self, row, col):
        """
        Melakukan booking kursi pada posisi (row, col)
        
        Args:
            row (int): Nomor baris (0-4)
            col (int): Nomor kolom (0-4)
        
        Returns:
            bool: True jika booking sukses, False jika gagal
        
        MEKANISME LOCKING:
        1. Lock.acquire() - Thread mendapatkan lock (masuk critical section)
        2. Cek apakah kursi masih available (0)
        3. Jika available, ubah menjadi booked (1)
        4. Lock.release() - Thread melepas lock (keluar critical section)
        
        Dengan lock, meskipun 2 client mencoba book kursi yang sama secara bersamaan,
        hanya 1 yang akan sukses karena mereka harus antri untuk masuk critical section.
        """
        
        # Validasi input
        if not (0 <= row < 5 and 0 <= col < 5):
            print(f"[ERROR] Invalid seat position: ({row}, {col})")
            return False
        
        # CRITICAL SECTION - Hanya 1 thread yang bisa masuk pada satu waktu
        self.lock.acquire()
        try:
            # Cek apakah kursi masih available
            if self.seat_map[row][col] == 0:
                # Kursi available, lakukan booking
                self.seat_map[row][col] = 1
                print(f"[SUCCESS] Seat ({row}, {col}) booked successfully")
                return True
            else:
                # Kursi sudah terisi
                print(f"[FAILED] Seat ({row}, {col}) already booked")
                return False
        finally:
            # Pastikan lock selalu dilepas, bahkan jika terjadi error
            self.lock.release()

def main():
    # Inisialisasi sistem booking
    booking_system = CinemaBookingSystem()
    
    # Buat threaded XML-RPC server pada port 8000
    # Gunakan "0.0.0.0" agar bisa diakses dari komputer lain di jaringan
    HOST = "0.0.0.0"  # Bind ke semua network interfaces
    PORT = 8000
    
    server = ThreadedXMLRPCServer((HOST, PORT), allow_none=True)
    
    # Dapatkan IP address komputer ini
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("=" * 60)
    print("Cinema Seat Booking Server")
    print("=" * 60)
    print(f"Server running on:")
    print(f"  - Local:   http://localhost:{PORT}")
    print(f"  - Network: http://{local_ip}:{PORT}")
    print()
    print("Untuk koneksi dari komputer lain, gunakan:")
    print(f"  http://{local_ip}:{PORT}")
    print("=" * 60)
    print("Waiting for client connections...")
    print("=" * 60)
    
    # Register fungsi-fungsi yang bisa dipanggil oleh client
    server.register_function(booking_system.get_seat_map, "get_seat_map")
    server.register_function(booking_system.book_seat, "book_seat")
    
    # Jalankan server (blocking call)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server shutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
