#include <Wire.h>
#include <esp_now.h>
#include <WiFi.h>

// Define pin assignments for all pumps
const int blackPump1Pin = 25;
const int blackPump2Pin = 26;
const int blackPump3Pin = 27;
const int blackPump4Pin = 14;
const int blackPump5Pin = 12;
const int whitePump1Pin = 19;
const int whitePump2Pin = 18;
const int whitePump3Pin = 5;

const int RELAY_DELAY = 500;

typedef struct command {
  int cmd;
  int pin;
} command;

command commandData;

// Callback when data is received
void OnDataRecv(const esp_now_recv_info* info, const uint8_t* incomingData, int len) {
    memcpy(&commandData, incomingData, sizeof(commandData));
    Serial.print("Received data - Pin: ");
    Serial.print(commandData.pin);
    Serial.print(", Command: ");
    Serial.println(commandData.cmd);
    controlPump(commandData.pin, commandData.cmd);
}

void controlPump(int pin, int cmd) {
    digitalWrite(pin, cmd % 2 == 1 ? HIGH : LOW); // Odd commands turn ON, even commands turn OFF
}

void setup() {
    Serial.begin(9600);
    while (!Serial); // Wait for serial to be ready
    Serial.println("Starting receiver setup...");

    WiFi.mode(WIFI_STA);

    // Init ESP-NOW
    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    // Register for a callback function when a data is received
    esp_now_register_recv_cb(OnDataRecv);

    pinMode(blackPump1Pin, OUTPUT);
    pinMode(blackPump2Pin, OUTPUT);
    pinMode(blackPump3Pin, OUTPUT);
    pinMode(blackPump4Pin, OUTPUT);
    pinMode(blackPump5Pin, OUTPUT);
    pinMode(whitePump1Pin, OUTPUT);
    pinMode(whitePump2Pin, OUTPUT);
    pinMode(whitePump3Pin, OUTPUT);
    Serial.println("Receiver setup completed.");
}

void loop() {
    // Empty loop
}
