import socket
import json
import mysql.connector
import os
import time
import RPi.GPIO as GPIO # Import library RPi.GPIO

# --- Konfigurasi Jaringan ---
HOST = '0.0.0.0'
PORT = 65432
LOCAL_CACHE_FILE = 'data_cache.json'

# --- Konfigurasi MySQL ---
DB_CONFIG = {
    "host": "localhost",
    "user": "sarva",
    "password": "sarva2025",
    "database": "db_ikan"
}

# --- Konfigurasi Hardware & Logika Penyortiran ---
# Pastikan koordinat ini sesuai dengan posisi fisik motor Anda
SORTING_BINS = {
    "Layur": [100, 50],  # Contoh: [steps_X, steps_Y]
    "Kakap": [200, 50],
    "Ikan B": [300, 50],
    # Tambahkan jenis ikan lain dan koordinatnya di sini
}
DEFAULT_COORDS = [0, 0] # Posisi default/reject (misal: posisi awal atau tempat sampah)

# --- KONFIGURASI PIN GPIO AKTUAL DI RASPBERRY PI ---
# SESUAIKAN DENGAN PIN YANG BENAR-BENAR ANDA GUNAKAN!
# RELAY_PIN tidak digunakan lagi karena simulasi
PUL_PIN = 17   # Contoh pin GPIO untuk PUL (Pulse) Stepper Driver
DIR_PIN = 27   # Contoh pin GPIO untuk DIR (Direction) Stepper Driver
ENA_PIN = 22   # Contoh pin GPIO untuk ENA (Enable) Stepper Driver

# --- KONFIGURASI MOTOR STEPPER ---
STEPS_PER_REVOLUTION = 200 # Umumnya 200 langkah/putaran untuk motor 1.8 derajat
MICROSTEPPING = 2         # SESUAIKAN dengan setting DIP switch di driver DMA860H Anda
PULSE_DELAY = 0.0005       # Delay antar pulsa (semakin kecil, semakin cepat). Sesuaikan!

# ==============================================================================
# === BAGIAN KONTROL HARDWARE ===
# ==============================================================================

# --- KELAS SIMULASI RELAY (Sesuai Permintaan Anda) ---
class SimulatedRelay:
    def __init__(self, pin):
        self.pin = pin # Pin ini hanya untuk tujuan logging simulasi
        print(f"✅ (Simulasi) Relay siap pada pin virtual {self.pin}")
    def on(self):
        print(f"🔌 (Simulasi) RELAY ON | Pin {self.pin} -> HIGH")
    def off(self):
        print(f"🔌 (Simulasi) RELAY OFF | Pin {self.pin} -> LOW")

# --- KELAS STEPPER MOTOR NYATA (RPi.GPIO) ---
class StepperMotor:
    def __init__(self, pul_pin, dir_pin, ena_pin, steps_per_rev, microstepping, pulse_delay):
        self.pul_pin = pul_pin
        self.dir_pin = dir_pin
        self.ena_pin = ena_pin
        self.steps_per_revolution = steps_per_rev
        self.microstepping = microstepping
        self.pulse_delay = pulse_delay
        self.total_steps_per_revolution = self.steps_per_revolution * self.microstepping
        self.current_position = [0, 0] # Asumsi posisi awal [0,0]

        GPIO.setup(self.pul_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.ena_pin, GPIO.OUT)

        # Inisialisasi pin pulsa ke LOW
        GPIO.output(self.pul_pin, GPIO.LOW)
        self.disable() # Pastikan motor nonaktif saat inisialisasi

        print(f"✅ Stepper Motor siap: PUL={self.pul_pin}, DIR={self.dir_pin}, ENA={self.ena_pin}")

    def enable(self):
        # Driver DMA860H umumnya LOW untuk enable
        GPIO.output(self.ena_pin, GPIO.LOW)
        print("⚙️  Stepper Driver Diaktifkan.")
        time.sleep(0.05) # Beri sedikit waktu untuk driver stabil

    def disable(self):
        # Driver DMA860H umumnya HIGH untuk disable
        GPIO.output(self.ena_pin, GPIO.HIGH)
        print("⚙️  Stepper Driver Dinonaktifkan.")
        time.sleep(0.05)

    def move_stepper_single_axis(self, target_steps, current_steps):
        """Menggerakkan motor pada satu sumbu (misal: X atau Y)."""
        steps_to_move = target_steps - current_steps
        if steps_to_move == 0:
            return current_steps # Tidak perlu bergerak

        direction_log = 'CW' if steps_to_move > 0 else 'CCW'
        actual_steps = abs(steps_to_move)

        # Set arah: sesuaikan jika arah CW/CCW terbalik
        if direction_log == 'CW':
            GPIO.output(self.dir_pin, GPIO.HIGH)
        else: # CCW
            GPIO.output(self.dir_pin, GPIO.LOW)

        print(f"  -> Bergerak {actual_steps} langkah ke arah {direction_log} (Delay: {self.pulse_delay}s)")

        self.enable() # Aktifkan driver sebelum bergerak
        for _ in range(actual_steps):
            GPIO.output(self.pul_pin, GPIO.HIGH)
            time.sleep(self.pulse_delay)
            GPIO.output(self.pul_pin, GPIO.LOW)
            time.sleep(self.pulse_delay)
        self.disable() # Nonaktifkan driver setelah bergerak (untuk hemat daya & mencegah panas)
        return target_steps # Mengembalikan posisi baru untuk sumbu ini

    def move_to(self, target_coords):
        """Menggerakkan motor ke koordinat target."""
        print(f"⚙️  MOTOR bergerak dari {self.current_position} menuju {target_coords}...")

        # Gerakkan sumbu X terlebih dahulu (sesuaikan urutan jika perlu)
        new_x = self.move_stepper_single_axis(target_coords[0], self.current_position[0])
        self.current_position[0] = new_x # Update posisi X

        # Gerakkan sumbu Y
        new_y = self.move_stepper_single_axis(target_coords[1], self.current_position[1])
        self.current_position[1] = new_y # Update posisi Y

        print(f"⚙️  MOTOR sampai di posisi {self.current_position}")
        time.sleep(0.5) # Jeda sebentar setelah mencapai posisi

# --- Inisialisasi GPIO dan Hardware (Relay Simulasi, Stepper Nyata) ---
GPIO.setmode(GPIO.BCM) # Gunakan penomoran BCM untuk pin GPIO

# Inisialisasi Relay sebagai SIMULASI
# Pin 17 di sini hanya untuk identifikasi simulasi, tidak benar-benar mengontrol GPIO
relay_sorter = SimulatedRelay(pin=17)

# Inisialisasi Stepper Motor sebagai NYATA dengan RPi.GPIO
stepper_motor = StepperMotor(
    pul_pin=PUL_PIN,
    dir_pin=DIR_PIN,
    ena_pin=ENA_PIN,
    steps_per_rev=STEPS_PER_REVOLUTION,
    microstepping=MICROSTEPPING,
    pulse_delay=PULSE_DELAY
)
# ==============================================================================

# --- SEMUA FUNGSI DATABASE & CACHE (Milik Anda, tanpa perubahan) ---
def get_db_connection():
    """Mencoba membuat koneksi ke database MySQL."""
    try:
        db_conn = mysql.connector.connect(**DB_CONFIG)
        print("[INFO] Koneksi MySQL berhasil.")
        return db_conn
    except mysql.connector.Error as err:
        print(f"[ERROR] Gagal terhubung ke MySQL: {err}")
        return None

def save_to_local_cache(data_record):
    """Menyimpan satu record data ke file JSON lokal."""
    records = []
    if os.path.exists(LOCAL_CACHE_FILE) and os.stat(LOCAL_CACHE_FILE).st_size > 0:
        try:
            with open(LOCAL_CACHE_FILE, 'r') as f:
                records = json.load(f)
        except json.JSONDecodeError:
            print("[WARNING] File cache JSON rusak. Membuat yang baru.")
            records = []
    records.append(data_record)
    with open(LOCAL_CACHE_FILE, 'w') as f:
        json.dump(records, f, indent=4)
    print(f"[INFO] Data disimpan sementara ke {LOCAL_CACHE_FILE}")

def process_cached_data(db_conn):
    """Memproses data yang tersimpan di cache lokal ke database MySQL."""
    if not os.path.exists(LOCAL_CACHE_FILE) or os.stat(LOCAL_CACHE_FILE).st_size == 0:
        print("[INFO] Tidak ada data di cache untuk diproses.")
        return
    print("[INFO] Mencoba memproses data dari cache...")

    records_to_process = []
    try:
        with open(LOCAL_CACHE_FILE, 'r') as f:
            records_to_process = json.load(f)

        if db_conn and db_conn.is_connected():
            cursor = db_conn.cursor()
            sql = "INSERT INTO log_ikan (jenis, berat, koordinatX, koordinatY, status) VALUES (%s, %s, %s, %s, %s)"

            processed_count = 0
            for record in records_to_process:
                try:
                    # Pastikan 'koordinat' ada dan memiliki 2 elemen
                    coords = record.get("koordinat", [0, 0])
                    if not isinstance(coords, list) or len(coords) != 2:
                        coords = [0, 0] # Fallback jika format koordinat salah

                    val = (record["jenis"], record["berat"], coords[0], coords[1], record["status"])
                    cursor.execute(sql, val)
                    db_conn.commit()
                    processed_count += 1
                except KeyError as ke:
                    print(f"[WARNING] Data cache tidak lengkap (KeyError: {ke}). Melewati record.")
                except mysql.connector.Error as err_inner:
                    print(f"[ERROR][DB Cache] Gagal menyimpan record dari cache: {err_inner}. Melewati record ini.")
                    # Jangan break, coba record berikutnya

            if processed_count > 0:
                print(f"[INFO] Berhasil memproses {processed_count} data dari cache ke MySQL.")
                # Hapus cache setelah berhasil diproses
                os.remove(LOCAL_CACHE_FILE)
                print("[INFO] Cache lokal dibersihkan.")
            else:
                print("[INFO] Tidak ada data valid yang berhasil diproses dari cache.")
        else:
            print("[WARNING] Koneksi MySQL tidak aktif, tidak dapat memproses cache.")

    except json.JSONDecodeError:
        print("[ERROR] File cache JSON rusak saat dibaca. Menghapus file cache.")
        os.remove(LOCAL_CACHE_FILE)
    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat memproses cache: {e}")


# --- FUNGSI UTAMA UNTUK MEMPROSES PERMINTAAN ---
def handle_client_request(parsed_data, db_connection):
    """Fungsi ini menggabungkan kontrol hardware DAN penyimpanan data."""

    # 1. Kontrol Perangkat Keras
    print("\n--- Memulai Aksi Hardware ---")
    try:
        jenis_ikan = parsed_data.get("jenis")
        status_mesin = parsed_data.get("status", "OFF").upper()

        if status_mesin == "ON":
            target_coords = SORTING_BINS.get(jenis_ikan, DEFAULT_COORDS)
            print(f"[AKSI] Jenis: '{jenis_ikan}', target koordinat: {target_coords}")

            relay_sorter.on() # Relay simulasi
            stepper_motor.move_to(target_coords) # Stepper motor nyata
            time.sleep(0.5) # Beri jeda setelah gerakan
            relay_sorter.off() # Relay simulasi

            print("[AKSI] Proses penyortiran selesai.")
            # Update koordinat di data yang akan disimpan
            parsed_data["koordinat"] = target_coords
        else:
            print("[AKSI] Status 'OFF', tidak ada aksi hardware.")
            parsed_data["koordinat"] = DEFAULT_COORDS # Atur koordinat default jika tidak ada aksi

    except Exception as e:
        print(f"[ERROR][HARDWARE] Gagal melakukan aksi: {e}")
        parsed_data["koordinat"] = DEFAULT_COORDS # Set koordinat default jika terjadi error hardware


    # 2. Simpan Log Aksi ke Database atau Cache
    print("\n--- Memulai Penyimpanan Data ---")
    if db_connection and db_connection.is_connected():
        try:
            cursor = db_connection.cursor()
            sql = "INSERT INTO log_ikan (jenis, berat, koordinatX, koordinatY, status) VALUES (%s, %s, %s, %s, %s)"

            # Pastikan 'koordinat' ada dan memiliki 2 elemen sebelum diakses
            coords = parsed_data.get("koordinat", [0, 0])
            if not isinstance(coords, list) or len(coords) != 2:
                coords = [0, 0] # Fallback jika format koordinat salah

            val = (parsed_data["jenis"], parsed_data["berat"], coords[0], coords[1], parsed_data["status"])
            cursor.execute(sql, val)
            db_connection.commit()
            print(f"[DB] Berhasil menyimpan {cursor.rowcount} data ke MySQL.")
        except mysql.connector.Error as err:
            print(f"[ERROR][DB] Gagal menyimpan ke MySQL: {err}")
            print("[FALLBACK] Menyimpan data ke cache lokal.")
            save_to_local_cache(parsed_data)
            # Set koneksi jadi None agar dicoba sambung ulang di loop utama
            if db_connection: db_connection.close()
            return None # Mengembalikan koneksi yang sudah tidak valid
    else:
        print("[INFO] Koneksi MySQL tidak aktif. Menyimpan data ke cache lokal.")
        save_to_local_cache(parsed_data)

    return db_connection # Kembalikan koneksi yang masih valid


# --- Logika Utama Server (Gabungan) ---
def run_server():
    # Inisialisasi GPIO sudah dilakukan di bagian inisialisasi hardware
    current_db_connection = get_db_connection()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"\n✅ [SERVER SIAP] Menunggu koneksi dari PC di {HOST}:{PORT}")

        # Coba proses data cache saat server pertama kali mulai
        if current_db_connection:
            process_cached_data(current_db_connection)

        while True:
            # Cek koneksi DB dan coba sambung ulang jika perlu
            if not current_db_connection or not current_db_connection.is_connected():
                print("\n[INFO] Mencoba menyambung kembali ke MySQL...")
                current_db_connection = get_db_connection()
                if current_db_connection:
                    # Jika berhasil nyambung lagi, proses cache yang mungkin tertinggal
                    process_cached_data(current_db_connection)

            print("\n[INFO] Menunggu koneksi client...")
            conn, addr = s.accept()
            with conn:
                print(f"➡️  Terhubung dengan client: {addr}")
                data = conn.recv(1024)
                if data:
                    try:
                        parsed_data = json.loads(data.decode('utf-8'))
                        print(f"[DATA DITERIMA] {parsed_data}")

                        # Panggil fungsi utama untuk proses semuanya
                        current_db_connection = handle_client_request(parsed_data, current_db_connection)

                    except json.JSONDecodeError:
                        print("[ERROR] Data yang diterima bukan format JSON yang valid.")
                    except Exception as e:
                        print(f"[ERROR] Terjadi kesalahan tak terduga: {e}")

if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n🛑 Server dihentikan oleh pengguna.")
    finally:
        # Tambahkan GPIO.cleanup() di sini untuk memastikan pin dibersihkan
        GPIO.cleanup()
        print("Server ditutup & GPIO dibersihkan.")
