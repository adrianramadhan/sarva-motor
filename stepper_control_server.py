import RPi.GPIO as GPIO
import time
import socket
import threading
import socket as pysocket  # untuk kirim ke ESP32

# --- Konfigurasi Jaringan ---
HOST = '0.0.0.0'
PORT = 65432
ESP32_IP   = '192.168.30.185'
ESP32_PORT = 65432

# --- Konfigurasi Pin GPIO Berdasarkan Tabel ---
MOTOR_PINS = {
    'M1': {'step': 4,  'dir': 17},
    'M2': {'step': 22, 'dir': 23},
    'M3': {'step': 24, 'dir': 25},
    'M4': {'step': 5,  'dir': 6},
    'M5': {'step': 12, 'dir': 13},
    'M6': {'step': 19, 'dir': 26},
    'M7': {'step': 20, 'dir': 21}
}
ENA_PIN = 27

# --- Konfigurasi Motor ---
PULSE_DELAY = 0.0005

# --- Variabel Kontrol Global & State Management ---
motor_states = {name: False for name in MOTOR_PINS.keys()}
motor_threads = {}
state_lock = threading.Lock()

def send_relay_command(cmd: str):
    try:
        with pysocket.create_connection((ESP32_IP, ESP32_PORT), timeout=1) as s:
            s.sendall((cmd+"\n").encode())
    except Exception as e:
        print(f"[WARN] Gagal kirim ke ESP32: {e}")

def setup_gpio():
    """Mengatur mode GPIO dan semua pin motor sebagai output."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ENA_PIN, GPIO.OUT)
    for motor_name, pins in MOTOR_PINS.items():
        GPIO.setup(pins['step'], GPIO.OUT)
        GPIO.setup(pins['dir'], GPIO.OUT)
        GPIO.output(pins['step'], GPIO.LOW)
    print("GPIO Setup Selesai untuk 7 motor.")

def enable_drivers():
    """Mengaktifkan semua driver motor."""
    GPIO.output(ENA_PIN, GPIO.LOW)
    print("Driver Diaktifkan.")
    time.sleep(0.01)

def disable_drivers():
    """Menonaktifkan semua driver motor."""
    GPIO.output(ENA_PIN, GPIO.HIGH)
    print("Driver Dinonaktifkan.")
    time.sleep(0.01)

def run_motor_continuously(motor_name, direction, delay):
    """Fungsi yang dijalankan di dalam thread untuk satu motor."""
    pins = MOTOR_PINS[motor_name]
    step_pin = pins['step']
    dir_pin = pins['dir']

    if direction == 'CW':
        GPIO.output(dir_pin, GPIO.HIGH)
    else:
        GPIO.output(dir_pin, GPIO.LOW)

    print(f"Thread untuk motor {motor_name} dimulai, arah: {direction}.")

    while True:
        with state_lock:
            if not motor_states[motor_name]:
                break

        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(delay)

    print(f"Thread untuk motor {motor_name} berhenti.")

def main():
    setup_gpio()
    disable_drivers()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print(f"\n[SERVER SIAP] Menunggu perintah di {HOST}:{PORT}")
            print("Perintah: 'start:mX', 'stop:mX', 'startall', 'stopall'")

            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"\nTerhubung dengan klien: {addr}")
                    data = conn.recv(1024)
                    if not data:
                        continue

                    received_command = data.decode('utf-8').strip().lower()
                    print(f"Menerima data: '{received_command}'")

                    # --- Logika Pemrosesan Perintah ---
                    with state_lock:
                        # PERINTAH BARU: STARTALL
                        if received_command == "start":
                            enable_drivers()
                            for motor_name in MOTOR_PINS.keys():
                                if not motor_states[motor_name]:
                                    motor_states[motor_name] = True
                                    thread = threading.Thread(target=run_motor_continuously, args=(motor_name, 'CW', PULSE_DELAY))
                                    thread.daemon = True
                                    motor_threads[motor_name] = thread
                                    thread.start()
                            conn.sendall(b"Semua motor dimulai.")
                        
                        # PERINTAH BARU: STOPALL
                        elif received_command == "stop":
                            for motor_name in MOTOR_PINS.keys():
                                motor_states[motor_name] = False
                            
                            # Beri waktu thread untuk berhenti sebelum menonaktifkan driver
                            time.sleep(0.1) 
                            disable_drivers()
                            motor_threads.clear() # Hapus semua referensi thread
                            conn.sendall(b"Semua motor dihentikan.")

                        # LOGIKA LAMA: Perintah per motor
                        elif ':' in received_command:
                            try:
                                command, motor_id = received_command.split(':')
                                motor_name = motor_id.upper()

                                if motor_name not in MOTOR_PINS:
                                    conn.sendall(f"Error: Motor '{motor_name}' tidak dikenal.".encode())
                                    continue
                                
                                if command == "start":
                                    if not motor_states[motor_name]:
                                        if not any(motor_states.values()): enable_drivers()
                                        motor_states[motor_name] = True
                                        thread = threading.Thread(target=run_motor_continuously, args=(motor_name, 'CW', PULSE_DELAY))
                                        thread.daemon = True
                                        motor_threads[motor_name] = thread
                                        thread.start()
                                        conn.sendall(f"Motor {motor_name} dimulai.".encode())
                                    else:
                                        conn.sendall(f"Motor {motor_name} sudah berjalan.".encode())

                                elif command == "stop":
                                    if motor_states[motor_name]:
                                        motor_states[motor_name] = False
                                        motor_threads.pop(motor_name, None)
                                        if not any(motor_states.values()): disable_drivers()
                                        conn.sendall(f"Perintah stop untuk {motor_name} dikirim.".encode())
                                    else:
                                        conn.sendall(f"Motor {motor_name} sudah berhenti.".encode())
                                else:
                                    conn.sendall(b"Perintah tidak dikenal.")

                            except ValueError:
                                conn.sendall(b"Error: Format perintah salah.")
                        else:
                            conn.sendall(b"Perintah tidak dikenal.")

    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")
    finally:
        print("Memulai prosedur shutdown...")
        with state_lock:
            for motor_name in list(motor_states.keys()):
                motor_states[motor_name] = False
        time.sleep(1)
        disable_drivers()
        GPIO.cleanup()
        print("GPIO dibersihkan. Program selesai.")

if __name__ == "__main__":
    main()
