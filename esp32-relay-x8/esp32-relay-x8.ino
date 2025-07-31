// ---------- Pin Relay & LED Heartbeat ----------
const uint8_t RELAY_PINS[7] = {32, 33, 25, 26, 27, 14, 12};
const uint8_t LED_PIN       = 23;

// Kita akan menggunakan Serial2 (Pin 16=RX, Pin 17=TX) untuk komunikasi dengan Pi
// Ini membuat Serial utama (USB) bebas untuk debugging.
#define SERIAL_PI Serial2

// ---------- Fungsi Toggle Relay ----------
void handleCommand(const String &cmd) {
  // format: "RLYn:ON" atau "RLYn:OFF"
  int colon = cmd.indexOf(':');
  if (colon < 0) return;

  String name = cmd.substring(0, colon);
  String action = cmd.substring(colon + 1);
  if (!name.startsWith("RLY")) return;

  int idx = name.substring(3).toInt() - 1; // RLY1→0, … RLY7→6
  if (idx < 0 || idx >= 7) return;

  if (action == "ON") {
    digitalWrite(RELAY_PINS[idx], HIGH);
    Serial.printf("→ Relay %d ON\n", idx + 1); // Debug ke USB Monitor
  } else if (action == "OFF") {
    digitalWrite(RELAY_PINS[idx], LOW);
    Serial.printf("→ Relay %d OFF\n", idx + 1); // Debug ke USB Monitor
  }
}

// ---------- Setup ----------
void setup() {
  // Serial untuk debugging via USB
  Serial.begin(115200);
  
  // Serial2 untuk komunikasi dengan Raspberry Pi
  // Baud rate harus sama dengan di skrip Python (9600)
  SERIAL_PI.begin(9600, SERIAL_8N1, 16, 17); // RX=16, TX=17

  // Inisialisasi pin relay
  for (int i = 0; i < 7; i++) {
    pinMode(RELAY_PINS[i], OUTPUT);
    digitalWrite(RELAY_PINS[i], LOW);
  }
  pinMode(LED_PIN, OUTPUT);
  Serial.println("ESP32 siap menerima perintah serial dari Raspberry Pi.");
}

// ---------- Loop Utama ----------
void loop() {
  // Heartbeat LED
  static uint32_t t0 = millis();
  if (millis() - t0 > 500) {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    t0 = millis();
  }

  // Cek jika ada data masuk dari Raspberry Pi
  if (SERIAL_PI.available()) {
    String command = SERIAL_PI.readStringUntil('\n');
    command.trim();
    if (command.length() > 0) {
      Serial.print("Diterima dari Pi: "); // Debug ke USB Monitor
      Serial.println(command);
      handleCommand(command);
    }
  }
}