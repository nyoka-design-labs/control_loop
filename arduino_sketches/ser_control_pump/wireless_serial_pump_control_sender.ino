#include <Wire.h>
#include <esp_now.h>
#include <WiFi.h>

uint8_t broadcastAddressPcu1[] = {0x24, 0x6F, 0x28, 0x4F, 0xF3, 0xD6}; // Replace with actual MAC address for pcu1
uint8_t broadcastAddressPcu2[] = {0x24, 0x6F, 0x28, 0x4F, 0xF3, 0xD7}; // Replace with actual MAC address for pcu2

typedef struct command {
  int cmd;
  char pcu_id[4];
} command;

command commandData;
esp_now_peer_info_t peerInfoPcu1;
esp_now_peer_info_t peerInfoPcu2;

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.print("\r\nLast Packet Send Status:\t");
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

void setup() {
    Serial.begin(9600);
    while (!Serial); // Wait for serial to be ready
    Serial.println("Starting sender setup...");

    WiFi.mode(WIFI_STA);

    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    esp_now_register_send_cb(OnDataSent);

    // Setup peer info for pcu1
    memcpy(peerInfoPcu1.peer_addr, broadcastAddressPcu1, 6);
    peerInfoPcu1.channel = 0;
    peerInfoPcu1.encrypt = false;
    if (esp_now_add_peer(&peerInfoPcu1) != ESP_OK) {
        Serial.println("Failed to add peer pcu1");
        return;
    }

    // Setup peer info for pcu2
    memcpy(peerInfoPcu2.peer_addr, broadcastAddressPcu2, 6);
    peerInfoPcu2.channel = 0;
    peerInfoPcu2.encrypt = false;
    if (esp_now_add_peer(&peerInfoPcu2) != ESP_OK) {
        Serial.println("Failed to add peer pcu2");
        return;
    }

    Serial.println("Sender setup completed.");
}

void loop() {
    if (Serial.available() > 0) {
        String incomingCommand = Serial.readStringUntil('\n');
        if (incomingCommand.length() > 4) {
            int cmd = incomingCommand.substring(0, incomingCommand.length() - 4).toInt();
            String pcu_id = incomingCommand.substring(incomingCommand.length() - 4);

            if (pcu_id == "pcu1") {
                sendCommand(cmd, broadcastAddressPcu1);
            } else if (pcu_id == "pcu2") {
                sendCommand(cmd, broadcastAddressPcu2);
            } else {
                Serial.println("Invalid PCU ID");
            }
        }
    }
}

void sendCommand(int cmd, uint8_t *address) {
    commandData.cmd = cmd;
    strcpy(commandData.pcu_id, (address == broadcastAddressPcu1) ? "pcu1" : "pcu2");

    esp_err_t result = esp_now_send(address, (uint8_t *)&commandData, sizeof(commandData));
    if (result == ESP_OK) {
        Serial.println("Sent with success");
    } else {
        Serial.println("Error sending the data");
    }
}