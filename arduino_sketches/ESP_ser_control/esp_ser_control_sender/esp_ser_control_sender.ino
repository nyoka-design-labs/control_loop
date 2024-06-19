#include <Wire.h>
#include <esp_now.h>
#include <WiFi.h>

const int blackPump1Pin = 25;
const int blackPump2Pin = 26;
const int blackPump3Pin = 27;
const int blackPump4Pin = 14;
const int blackPump5Pin = 12;
const int whitePump1Pin = 19;
const int whitePump2Pin = 18;
const int whitePump3Pin = 5;

const int RELAY_DELAY = 500;
uint8_t broadcastAddress[] = {0xfc, 0xb4, 0x67, 0xf3, 0xc6, 0xe0};

typedef struct command {
  int cmd;
  int pin;
} command;

command commandData;
esp_now_peer_info_t peerInfo;

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.print("\r\nLast Packet Send Status:\t");
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

void setup() {
    Serial.begin(9600);
    while (!Serial); // Wait for serial to be ready
    Serial.println("\n Starting sender setup...");

    WiFi.mode(WIFI_STA);

    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    esp_now_register_send_cb(OnDataSent);

    memcpy(peerInfo.peer_addr, broadcastAddress, 6);
    peerInfo.channel = 0;
    peerInfo.encrypt = false;

    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("Failed to add peer");
        return;
    }

    pinMode(blackPump1Pin, OUTPUT);
    pinMode(blackPump2Pin, OUTPUT);
    pinMode(blackPump3Pin, OUTPUT);
    pinMode(blackPump4Pin, OUTPUT);
    pinMode(blackPump5Pin, OUTPUT);
    pinMode(whitePump1Pin, OUTPUT);
    pinMode(whitePump2Pin, OUTPUT);
    pinMode(whitePump3Pin, OUTPUT);
    Serial.println("Sender setup completed.");
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        if (command.startsWith("R")) {
            int voltage = command.substring(1).toInt();
            setRPM(voltage);
        } else {
            int cmd = command.toInt();
            handlePumpCommand(cmd);
        }
    }
}

void handlePumpCommand(int cmd) {
    Serial.print("Received command: ");
    Serial.println(cmd);
    switch (cmd) {
        case 0: case 1: sendCommand(blackPump1Pin, cmd); break;
        case 2: case 3: sendCommand(blackPump2Pin, cmd); break;
        case 4: case 5: sendCommand(blackPump3Pin, cmd); break;
        case 6: case 7: sendCommand(blackPump4Pin, cmd); break;
        case 8: case 9: sendCommand(blackPump5Pin, cmd); break;
        case 10: case 11: sendCommand(whitePump1Pin, cmd); break;
        case 12: case 13: sendCommand(whitePump2Pin, cmd); break;
        case 14: case 15: sendCommand(whitePump3Pin, cmd); break;
        default: Serial.println("Unknown command"); return;
    }
}

void setRPM(int voltage) {
    // Placeholder function
}

void controlPump(int pin, int cmd) {
    digitalWrite(pin, cmd % 2 == 1 ? HIGH : LOW);
}

void sendCommand(int pin, int cmd) {
    commandData.pin = pin;
    commandData.cmd = cmd;

    esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *)&commandData, sizeof(commandData));
    if (result == ESP_OK) {
        Serial.println("Sent with success");
    } else {
        Serial.println("Error sending the data");
    }
}
