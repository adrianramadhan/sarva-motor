import socket
import sys

# --- Konfigurasi ---
PI_IP   = '192.168.30.185'  # Ganti dengan alamat IP Raspberry Pi Anda
PI_PORT = 65432
# ------------------

def kirim(perintah):
    """Fungsi untuk mengirim satu perintah ke Raspberry Pi."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # Timeout 5 detik
            s.connect((PI_IP, PI_PORT))
            s.sendall(perintah.encode('utf-8'))
            respons = s.recv(1024).decode('utf-8')
            print(f"Jawaban dari Pi: {respons}")
    except socket.timeout:
        print(f"❌ Error: Tidak ada jawaban dari {PI_IP}. Pastikan server Pi berjalan.")
    except ConnectionRefusedError:
        print(f"❌ Error: Koneksi ditolak. Pastikan server Pi berjalan di port {PI_PORT}.")
    except Exception as e:
        print(f"❌ Terjadi error: {e}")

if __name__ == "__main__":
    # Cek apakah argumen perintah diberikan saat menjalankan skrip
    if len(sys.argv) < 2:
        print("Gunakan format: python kirim_perintah.py \"perintah\"")
        print("Contoh: python kirim_perintah.py \"start:m1\"")
        sys.exit(1)
        
    # Gabungkan semua argumen menjadi satu string perintah
    perintah_untuk_dikirim = " ".join(sys.argv[1:])
    
    print(f"▶️  Mengirim perintah: '{perintah_untuk_dikirim}' ke {PI_IP}...")
    kirim(perintah_untuk_dikirim)