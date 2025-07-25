import RPi.GPIO as GPIO
import time

# --- Konfigurasi Pin GPIO Anda ---
PUL_PIN = 17  # GPIO17 untuk Pulse
DIR_PIN = 27  # GPIO27 untuk Direction
ENA_PIN = 22  # GPIO22 untuk Enable

# --- Konfigurasi Motor dan Driver ---
# Jumlah langkah per putaran penuh motor (tanpa microstepping)
# Stepper NEMA 34 umumnya 1.8 derajat per langkah, jadi 360/1.8 = 200 langkah
STEPS_PER_REVOLUTION = 200

# Pengaturan Microstepping pada driver DMA860H Anda
# Contoh: Jika Anda mengatur microstepping ke 1/16, maka:
MICROSTEPPING = 16
# Total langkah per putaran dengan microstepping
TOTAL_STEPS = STEPS_PER_REVOLUTION * MICROSTEPPING

# --- Kecepatan Motor (semakin kecil delay, semakin cepat motor) ---
# Delay antar pulsa dalam detik. Sesuaikan untuk mendapatkan kecepatan yang diinginkan.
# Nilai yang terlalu kecil bisa membuat motor macet/bergetar.
PULSE_DELAY = 0.0005 # Contoh: 0.5 milidetik per pulsa

def setup_gpio():
    """Mengatur mode GPIO dan pin sebagai output."""
    GPIO.setmode(GPIO.BCM)  # Gunakan penomoran BCM
    GPIO.setup(PUL_PIN, GPIO.OUT)
    GPIO.setup(DIR_PIN, GPIO.OUT)
    GPIO.setup(ENA_PIN, GPIO.OUT)
    print("GPIO Setup Selesai.")

def enable_driver():
    """Mengaktifkan driver motor."""
    # Sinyal ENA biasanya low (0V) untuk enable, high (3.3V) untuk disable.
    # Namun, beberapa driver bisa terbalik, cek datasheet Anda.
    # Di sini kita asumsikan low = enable.
    GPIO.output(ENA_PIN, GPIO.LOW)
    print("Driver Diaktifkan.")
    time.sleep(0.1) # Beri sedikit waktu untuk driver stabil

def disable_driver():
    """Menonaktifkan driver motor."""
    GPIO.output(ENA_PIN, GPIO.HIGH) # High = disable
    print("Driver Dinonaktifkan.")
    time.sleep(0.1)

def move_stepper(steps, direction, delay):
    """
    Menggerakkan motor stepper.

    Args:
        steps (int): Jumlah pulsa (langkah) yang akan digerakkan.
        direction (str): 'CW' untuk Clockwise (searah jarum jam) atau 'CCW' untuk Counter-Clockwise.
        delay (float): Jeda waktu antar pulsa (untuk mengontrol kecepatan).
    """
    if direction == 'CW':
        GPIO.output(DIR_PIN, GPIO.HIGH) # HIGH untuk satu arah
        print(f"Menggerakkan {steps} langkah CW...")
    elif direction == 'CCW':
        GPIO.output(DIR_PIN, GPIO.LOW) # LOW untuk arah lain
        print(f"Menggerakkan {steps} langkah CCW...")
    else:
        print("Arah tidak valid. Gunakan 'CW' atau 'CCW'.")
        return

    for _ in range(steps):
        GPIO.output(PUL_PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(PUL_PIN, GPIO.LOW)
        time.sleep(delay)

def main():
    try:
        setup_gpio()
        enable_driver()

        print("\n--- Mulai Pengujian Motor Stepper ---")

        # Gerakkan motor 1 putaran penuh searah jarum jam
        print(f"\nMemutar 1 putaran ({TOTAL_STEPS} langkah) searah jarum jam...")
        move_stepper(TOTAL_STEPS, 'CW', PULSE_DELAY)
        time.sleep(1) # Jeda sebentar

        # Gerakkan motor 1 putaran penuh berlawanan jarum jam
        print(f"\nMemutar 1 putaran ({TOTAL_STEPS} langkah) berlawanan jarum jam...")
        move_stepper(TOTAL_STEPS, 'CCW', PULSE_DELAY)
        time.sleep(1) # Jeda sebentar

        # Contoh bergerak 1/2 putaran
        print(f"\nMemutar 1/2 putaran ({TOTAL_STEPS // 2} langkah) searah jarum jam...")
        move_stepper(TOTAL_STEPS // 2, 'CW', PULSE_DELAY)
        time.sleep(1)

        print("\n--- Pengujian Selesai ---")

    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")
    except Exception as e:
        print(f"\nTerjadi kesalahan: {e}")
    finally:
        disable_driver() # Pastikan driver dinonaktifkan saat selesai
        GPIO.cleanup() # Bersihkan pengaturan GPIO
        print("GPIO dibersihkan.")

if __name__ == "__main__":
    main()
