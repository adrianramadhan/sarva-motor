import RPi.GPIO as GPIO
import time
import socket
import threading
import serial  # Import library serial

# ===============================================================
# KONFIGURASI
# ===============================================================

# 1. Konfigurasi Server Jaringan (untuk PC)
PI_SERVER_HOST = '0.0.0.0'
PI_SERVER_PORT = 65432

# 2. Konfigurasi Serial Port (untuk ESP32)
# Port serial di GPIO biasanya /dev/ttyS0 atau /dev/serial0
# Baud rate harus sama dengan di kode ESP32
try:
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    print("✅ Port serial /dev/ttyS0 berhasil dibuka.")
except serial.SerialException as e:
    print(f"🔥 Gagal membuka port serial: {e}")
    print("Pastikan serial sudah diaktifkan via 'raspi-config' dan tidak ada program lain yang menggunakannya.")
    exit()

# 3. Konfigurasi Motor (Sama seperti sebelumnya)
MOTOR_PINS = {
    'M1': {'step': 4,  'dir': 17}, 'M2': {'step': 22, 'dir': 23},
    'M3': {'step': 24, 'dir': 25}, 'M4': {'step': 5,  'dir': 6},
    'M5': {'step': 12, 'dir': 13}, 'M6': {'step': 19, 'dir': 26},
    'M7': {'step': 20, 'dir': 21}
}
ENA_PIN = 27
PULSE_DELAY = 0.0005

# ===============================================================
# KODE UTAMA
# ===============================================================

motor_states = {name: False for name in MOTOR_PINS.keys()}
motor_threads = {}
state_lock = threading.Lock()

def send_serial_command(cmd: str):
    """Mengirim perintah ke ESP32 melalui koneksi serial."""
    try:
        # Tambahkan newline karena ESP32 membaca sampai newline
        full_cmd = (cmd + '\n').encode('utf-8')
        ser.write(full_cmd)
        print(f"[SERIAL CMD] -> Perintah '{cmd}' dikirim ke ESP32.")
    except Exception as e:
        print(f"[ERROR] Gagal mengirim perintah serial: {e}")

# ... (Fungsi setup_gpio, enable/disable_drivers, run_motor_continuously tidak berubah) ...
def setup_gpio():
    GPIO.setwarnings(False); GPIO.setmode(GPIO.BCM); GPIO.setup(ENA_PIN, GPIO.OUT)
    for pins in MOTOR_PINS.values():
        GPIO.setup(pins['step'], GPIO.OUT); GPIO.setup(pins['dir'], GPIO.OUT)
def enable_drivers(): GPIO.output(ENA_PIN, GPIO.LOW); print("🔌 Driver diaktifkan.")
def disable_drivers(): GPIO.output(ENA_PIN, GPIO.HIGH); print("🔌 Driver dinonaktifkan.")
def run_motor_continuously(motor_name):
    pins = MOTOR_PINS[motor_name]; GPIO.output(pins['dir'], GPIO.HIGH)
    while True:
        with state_lock:
            if not motor_states[motor_name]: break
        GPIO.output(pins['step'], GPIO.HIGH); time.sleep(PULSE_DELAY)
        GPIO.output(pins['step'], GPIO.LOW); time.sleep(PULSE_DELAY)

def process_command(command_str):
    """Memproses perintah dari PC, mengontrol motor, dan mengirim perintah ke ESP32."""
    with state_lock:
        try:
            command, motor_id = command_str.lower().split(':')
            motor_name = motor_id.upper()
            if motor_name not in MOTOR_PINS: return "Error: Motor tidak dikenal."
            relay_num = motor_name[1:]

            if command == "start":
                if not motor_states[motor_name]:
                    if not any(motor_states.values()): enable_drivers()
                    motor_states[motor_name] = True
                    thread = threading.Thread(target=run_motor_continuously, args=(motor_name,))
                    thread.daemon = True; thread.start()
                    send_serial_command(f"RLY{relay_num}:ON") # <-- Kirim via Serial
                    return f"Motor {motor_name} dimulai."
                return f"Motor {motor_name} sudah berjalan."

            elif command == "stop":
                if motor_states[motor_name]:
                    motor_states[motor_name] = False
                    if not any(motor_states.values()): disable_drivers()
                    send_serial_command(f"RLY{relay_num}:OFF") # <-- Kirim via Serial
                    return f"Perintah stop untuk {motor_name} dikirim."
                return f"Motor {motor_name} sudah berhenti."
            return "Error: Perintah tidak dikenal."
        except ValueError:
            return "Error: Format perintah salah."

def main():
    """Fungsi utama untuk menjalankan server di Raspberry Pi."""
    setup_gpio(); disable_drivers()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((PI_SERVER_HOST, PI_SERVER_PORT))
        s.listen()
        print(f"\n🚀 [SERVER PI SIAP] Menunggu perintah dari PC di port {PI_SERVER_PORT}")
        try:
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    if not data: continue
                    received_command = data.decode('utf-8').strip()
                    print(f"\nPerintah dari PC diterima: '{received_command}'")
                    response = process_command(received_command)
                    conn.sendall(response.encode('utf-8'))
        except KeyboardInterrupt: print("\nProgram dihentikan.")
        finally:
            print("Memulai shutdown...")
            # Kirim perintah stop untuk semua motor yang masih jalan
            for name, is_running in motor_states.items():
                if is_running:
                    send_serial_command(f"RLY{name[1:]}:OFF")
            
            time.sleep(0.5)  # Beri waktu agar perintah terkirim
            
            # Baru tutup port serial setelah semua perintah dikirim
            ser.close() 
            
            disable_drivers()
            GPIO.cleanup()
            print("✅ Serial port ditutup, GPIO dibersihkan.")

if __name__ == "__main__":
    main()
