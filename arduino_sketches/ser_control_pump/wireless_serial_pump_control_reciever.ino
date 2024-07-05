#include <Wire.h>
#include <esp_now.h>
#include <WiFi.h>

// Define pin assignments for all pumps
const int blackPump1Pin = 34;
const int blackPump2Pin = 35;
const int blackPump3Pin = 27;
const int blackPump4Pin = 14;
const int blackPump5Pin = 12;
const int whitePump1Pin = 19;
const int whitePump2Pin = 18;
const int whitePump3Pin = 5;

typedef struct command {
  int cmd;
  char pcu_id[4];
} command;

command commandData;

// This should be different for each receiver
const char pcu_id[] = "pcu1"; // Set to "pcu1" or "pcu2" accordingly

// Function to map commands to pins
int getPinForCommand(int cmd) {
    switch (cmd) {
        case 0: case 1: return blackPump1Pin;
        case 2: case 3: return blackPump2Pin;
        case 4: case 5: return blackPump3Pin;
        case 6: case 7: return blackPump4Pin;
        case 8: case 9: return blackPump5Pin;
        case 10: case 11: return whitePump1Pin;
        case 12: case 13: return whitePump2Pin;
        case 14: case 15: return whitePump3Pin;
        default: return -1; // Invalid command
    }
}

// Callback when data is received
void OnDataRecv(const esp_now_recv_info* info, const uint8_t* incomingData, int len) {
    memcpy(&commandData, incomingData, sizeof(commandData));
    if (strcmp(commandData.pcu_id, pcu_id) == 0) {
        Serial.print("Received command: ");
        Serial.println(commandData.cmd);
        int pin = getPinForCommand(commandData.cmd);
        if (pin != -1) {
            controlPump(pin, commandData.cmd);
        } else {
            Serial.println("Invalid command received.");
        }
    }
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

    // Initialize all pins as outputs
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