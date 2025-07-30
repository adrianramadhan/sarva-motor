import RPi.GPIO as GPIO
import time

# --- Konfigurasi Pin GPIO Anda Berdasarkan Tabel ---
# Struktur data dictionary untuk menyimpan pin STEP dan DIR untuk setiap motor
MOTOR_PINS = {
    'M1': {'step': 4,  'dir': 17},
    'M2': {'step': 22, 'dir': 23},
    'M3': {'step': 24, 'dir': 25},
    'M4': {'step': 5,  'dir': 6},
    'M5': {'step': 12, 'dir': 13},
    'M6': {'step': 19, 'dir': 26},
    'M7': {'step': 20, 'dir': 21}
}

# Pin ENA (Enable) yang digunakan bersama untuk semua motor
ENA_PIN = 27

# --- Konfigurasi Motor dan Driver ---
STEPS_PER_REVOLUTION = 200
MICROSTEPPING = 16
TOTAL_STEPS = STEPS_PER_REVOLUTION * MICROSTEPPING

# --- Kecepatan Motor (semakin kecil delay, semakin cepat motor) ---
PULSE_DELAY = 0.0005 # 0.5 milidetik

def setup_gpio():
    """Mengatur mode GPIO dan semua pin motor sebagai output."""
    GPIO.setmode(GPIO.BCM)  # Gunakan penomoran BCM
    
    # Setup pin ENA yang digunakan bersama
    GPIO.setup(ENA_PIN, GPIO.OUT)
    
    # Loop melalui semua motor dan setup pin STEP dan DIR mereka
    for motor_name, pins in MOTOR_PINS.items():
        GPIO.setup(pins['step'], GPIO.OUT)
        GPIO.setup(pins['dir'], GPIO.OUT)
        print(f"Setup pin untuk {motor_name}: STEP={pins['step']}, DIR={pins['dir']}")
        
    print("GPIO Setup Selesai.")

def enable_driver():
    """Mengaktifkan semua driver motor (via shared ENA pin)."""
    GPIO.output(ENA_PIN, GPIO.LOW) # Asumsi LOW untuk mengaktifkan
    print("Semua Driver Diaktifkan.")
    time.sleep(0.1)

def disable_driver():
    """Menonaktifkan semua driver motor."""
    GPIO.output(ENA_PIN, GPIO.HIGH) # Asumsi HIGH untuk menonaktifkan
    print("Semua Driver Dinonaktifkan.")
    time.sleep(0.1)

def move_stepper(motor_name, steps, direction, delay):
    """
    Menggerakkan satu motor stepper yang spesifik.

    Args:
        motor_name (str): Nama motor yang akan digerakkan (e.g., 'M1', 'M2').
        steps (int): Jumlah langkah (pulsa) yang akan digerakkan.
        direction (str): 'CW' (searah jarum jam) atau 'CCW' (berlawanan arah).
        delay (float): Jeda waktu antar pulsa untuk mengontrol kecepatan.
    """
    # Ambil pin untuk motor yang dipilih dari dictionary
    pins = MOTOR_PINS.get(motor_name)
    if not pins:
        print(f"Error: Motor '{motor_name}' tidak ditemukan di konfigurasi.")
        return

    step_pin = pins['step']
    dir_pin = pins['dir']
    
    # Atur arah putaran
    if direction == 'CW':
        GPIO.output(dir_pin, GPIO.HIGH)
    elif direction == 'CCW':
        GPIO.output(dir_pin, GPIO.LOW)
    else:
        print("Arah tidak valid. Gunakan 'CW' atau 'CCW'.")
        return

    print(f"Menggerakkan motor {motor_name}: {steps} langkah {direction}...")
    
    # Kirim pulsa STEP
    for _ in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(delay)

def main():
    try:
        setup_gpio()
        enable_driver()

        print("\n--- Mulai Pengujian 7 Motor Stepper (Secara Berurutan) ---")

        # Jumlah langkah untuk pengujian (misal: 1/4 putaran)
        test_steps = TOTAL_STEPS // 4 

        # Gerakkan setiap motor searah jarum jam (CW) secara berurutan
        print("\n--- Tes Gerak CW ---")
        for motor_name in MOTOR_PINS.keys():
            move_stepper(motor_name, test_steps, 'CW', PULSE_DELAY)
            time.sleep(0.5) # Jeda antar motor

        time.sleep(2) # Jeda lebih lama sebelum tes berikutnya

        # Gerakkan setiap motor berlawanan arah jarum jam (CCW) secara berurutan
        print("\n--- Tes Gerak CCW ---")
        for motor_name in MOTOR_PINS.keys():
            move_stepper(motor_name, test_steps, 'CCW', PULSE_DELAY)
            time.sleep(0.5)

        # Contoh menggerakkan motor spesifik (Motor 3)
        # print("\n--- Tes Motor Spesifik (M3) ---")
        # move_stepper('M3', TOTAL_STEPS, 'CW', 0.0003) # Gerakkan M3 1 putaran penuh lebih cepat
        # time.sleep(1)


        print("\n--- Pengujian Selesai ---")

    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")
    except Exception as e:
        print(f"\nTerjadi kesalahan: {e}")
    finally:
        disable_driver() # Pastikan semua driver dinonaktifkan
        GPIO.cleanup()   # Bersihkan pengaturan GPIO
        print("GPIO dibersihkan.")

if __name__ == "__main__":
    main()
