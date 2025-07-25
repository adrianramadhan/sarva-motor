import serial
import time

# Inisialisasi koneksi serial
# Pastikan port '/dev/ttyS0' sudah benar untuk serial hardware di Pi 3B+
try:
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    ser.flush()
    print("✅ Koneksi serial ke ESP32 berhasil dibuka.")
except Exception as e:
    print(f"❌ Gagal membuka koneksi serial: {e}")
    exit()

def kirim_perintah(perintah):
    """Fungsi untuk mengirim perintah ke ESP32"""
    print(f"Mengirim perintah: {perintah}")
    # Tambahkan newline (\n) sebagai penanda akhir perintah
    ser.write(f"{perintah}\n".encode('utf-8'))
    time.sleep(0.1) # Beri jeda singkat

# --- Contoh Penggunaan ---
try:
    while True:
        print("\n--- Siklus Uji Coba ---")
        kirim_perintah("RLY1_ON")
        time.sleep(1)
        kirim_perintah("RLY1_OFF")
        time.sleep(1)

        kirim_perintah("RLY2_ON")
        time.sleep(1)
        kirim_perintah("RLY2_OFF")
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Program dihentikan.")
finally:
    ser.close()
    print("Koneksi serial ditutup.")
