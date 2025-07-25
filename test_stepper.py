import RPi.GPIO as GPIO
import time

PUL_PIN = 17
DIR_PIN = 27
ENA_PIN = 22

STEPS_PER_REVOLUTION = 200
MICROSTEPPING = 16 # Sesuai DIP switch Anda
PULSE_DELAY = 0.0005 # Mulai dengan nilai yang cukup besar

GPIO.setmode(GPIO.BCM)
GPIO.setup(PUL_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(ENA_PIN, GPIO.OUT)

# Inisialisasi
GPIO.output(PUL_PIN, GPIO.LOW)
# Coba logika ENA_PIN yang berbeda jika LOW tidak bekerja:
GPIO.output(ENA_PIN, GPIO.LOW) # Asumsi LOW = enable (coba HIGH jika tidak berfungsi)
print("Driver diaktifkan...")
time.sleep(1)

try:
    # Arah: HIGH atau LOW (sesuaikan jika terbalik)
    GPIO.output(DIR_PIN, GPIO.HIGH)
    print(f"Menggerakkan {2*MICROSTEPPING} langkah CW...") # Gerakkan 2 langkah mikro

    for _ in range(2 * MICROSTEPPING): # Cukup dua langkah mikro untuk tes
        GPIO.output(PUL_PIN, GPIO.HIGH)
        time.sleep(PULSE_DELAY)
        GPIO.output(PUL_PIN, GPIO.LOW)
        time.sleep(PULSE_DELAY)
    print("Selesai bergerak.")
    time.sleep(2)

except KeyboardInterrupt:
    print("\nDihentikan.")
finally:
    GPIO.output(ENA_PIN, GPIO.HIGH) # Menonaktifkan driver
    print("Driver dinonaktifkan.")
    GPIO.cleanup()
    print("GPIO dibersihkan.")
