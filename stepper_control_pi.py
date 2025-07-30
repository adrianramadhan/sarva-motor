import RPi.GPIO as GPIO
import time
import threading
import serial
import argparse
import random

# —– Motor pins —
MOTOR_PINS = {
    'M1': {'step': 4,  'dir': 17},
    'M2': {'step': 22, 'dir': 23},
    'M3': {'step': 24, 'dir': 25},
    'M4': {'step': 5,  'dir': 6},
    'M5': {'step': 12, 'dir': 13},
    'M6': {'step': 19, 'dir': 26},
    'M7': {'step': 20, 'dir': 21},
}
ENA_PIN     = 27
PULSE_DELAY = 0.0005

# —– State & threading —
motor_states  = {m: False for m in MOTOR_PINS}
motor_threads = {}
state_lock    = threading.Lock()

# —– Serial / Simulate flag —
args = None

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ENA_PIN, GPIO.OUT)
    for pins in MOTOR_PINS.values():
        GPIO.setup(pins['step'], GPIO.OUT)
        GPIO.setup(pins['dir'],  GPIO.OUT)
        GPIO.output(pins['step'], GPIO.LOW)
    GPIO.output(ENA_PIN, GPIO.HIGH)
    print("GPIO Ready, drivers disabled.")

def enable_drivers():
    GPIO.output(ENA_PIN, GPIO.LOW)
    time.sleep(0.01)

def disable_drivers():
    GPIO.output(ENA_PIN, GPIO.HIGH)
    time.sleep(0.01)

def run_motor(motor, direction):
    pins = MOTOR_PINS[motor]
    GPIO.output(pins['dir'], GPIO.HIGH if direction=='CW' else GPIO.LOW)
    while True:
        with state_lock:
            if not motor_states[motor]:
                break
        GPIO.output(pins['step'], GPIO.HIGH)
        time.sleep(PULSE_DELAY)
        GPIO.output(pins['step'], GPIO.LOW)
        time.sleep(PULSE_DELAY)

def handle_line(line):
    # ex: "RLY3:ON" atau "RLY5:OFF"
    try:
        name, st = line.split(':')
        if not name.startswith('RLY'): return
        idx   = int(name[3:])     # 1…7
        motor = f'M{idx}'
        with state_lock:
            if st == 'ON' and not motor_states[motor]:
                motor_states[motor] = True
                if sum(motor_states.values()) == 1:
                    enable_drivers()
                t = threading.Thread(target=run_motor, args=(motor,'CW'))
                t.daemon = True
                motor_threads[motor] = t
                t.start()
                print(f"{motor} START")
            elif st == 'OFF' and motor_states[motor]:
                motor_states[motor] = False
                motor_threads.pop(motor, None)
                if not any(motor_states.values()):
                    disable_drivers()
                print(f"{motor} STOP")
    except Exception:
        pass

def serial_listener():
    """Baca dari /dev/serial0, terus parse line per line."""
    try:
        ser = serial.Serial('/dev/serial0', 115200, timeout=1)
    except serial.SerialException as e:
        print("Gagal buka serial:", e)
        return

    print("Listening on UART…")
    while True:
        try:
            raw = ser.readline()
        except serial.SerialException:
            continue
        if not raw:
            continue
        line = raw.decode('ascii', errors='ignore').strip()
        if line:
            print("←", line)
            handle_line(line)

def simulate_relays():
    """Thread simulasi: generate event RLYn:ON/OFF acak tiap 1–3 detik."""
    print("== Simulation mode ON ==")
    while True:
        ch = random.randint(1,7)
        handle_line(f"RLY{ch}:ON")
        time.sleep(1)
        handle_line(f"RLY{ch}:OFF")
        time.sleep(random.uniform(0.5,2.0))

def main():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument('--simulate', action='store_true',
                        help="jalankan tanpa serial; simulasi relay")
    args = parser.parse_args()

    setup_gpio()

    # start listener / simulator
    if args.simulate:
        t = threading.Thread(target=simulate_relays)
        t.daemon = True
        t.start()
    else:
        t = threading.Thread(target=serial_listener)
        t.daemon = True
        t.start()

    # keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutdown...")
    finally:
        with state_lock:
            for m in motor_states:
                motor_states[m] = False
        time.sleep(0.1)
        disable_drivers()
        GPIO.cleanup()

if __name__=='__main__':
    main()
