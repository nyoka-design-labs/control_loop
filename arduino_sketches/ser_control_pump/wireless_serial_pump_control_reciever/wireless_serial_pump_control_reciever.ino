#include <Wire.h>
#include <esp_now.h>
#include <WiFi.h>

// Define pin assignments for all pumps
const int blackPump1Pin = 23;
const int blackPump2Pin = 32;
const int blackPump3Pin = 27;
const int blackPump4Pin = 14;
const int blackPump5Pin = 12;
const int whitePump1Pin = 19;
const int whitePump2Pin = 18;
const int whitePump3Pin = 5;

typedef struct command {
  int cmd;
  char pcu_id[5];
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

// Callback when data is received via ESP-NOW
void OnDataRecv(const esp_now_recv_info *info, const uint8_t *incomingData, int len) {
    Serial.println("Data received via ESP-NOW");
    Serial.print("Sender MAC: ");
    for (int i = 0; i < 6; i++) {
        Serial.print(info->src_addr[i], HEX);
        if (i < 5) Serial.print(":");
    }
    Serial.println();
    Serial.print("Data length: ");
    Serial.println(len);

    memcpy(&commandData, incomingData, sizeof(commandData));
    commandData.pcu_id[4] = '\0'; // Ensure null-termination
    Serial.print("Received pcu_id: ");
    Serial.println(commandData.pcu_id); // Debugging line

    if (strcmp(commandData.pcu_id, pcu_id) == 0) { // Compare pcu_id in the command with the receiver's pcu_id
        Serial.print("Received command via ESP-NOW: ");
        Serial.println(commandData.cmd);

        int pin = getPinForCommand(commandData.cmd);
        Serial.print("Pin determined: ");
        Serial.println(pin);

        if (pin != -1) {
            controlPump(pin, commandData.cmd);
        } else {
            Serial.println("Invalid command received.");
        }
    } else {
        Serial.println("PCU ID mismatch");
    }
}

void controlPump(int pin, int cmd) {
    Serial.println("pump being controlled");
    digitalWrite(pin, cmd % 2 == 1 ? HIGH : LOW); // Odd commands turn ON, even commands turn OFF
}

void setup() {
    Serial.begin(460800);
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
    if (Serial.available() > 0) {
        String incomingCommand = Serial.readStringUntil('\n');
        Serial.println("Command received: ");
        Serial.println(incomingCommand + "\n");

        if (incomingCommand.length() > 4) {
            int cmd = incomingCommand.substring(0, incomingCommand.length() - 4).toInt();
            String pcu_id = incomingCommand.substring(incomingCommand.length() - 4);

            Serial.println("Pin command received: ");
            Serial.println(cmd);  // Print the integer directly

            Serial.println("PCU ID received: ");
            Serial.println(pcu_id + "\n");

            if (pcu_id == "pcu1") {
                strncpy(commandData.pcu_id, pcu_id.c_str(), 4);
                commandData.pcu_id[4] = '\0'; // Ensure null-termination

                int pin = getPinForCommand(cmd);  // Correctly use cmd instead of commandData.cmd
                Serial.println("Pin that needs to turn on: ");
                Serial.println(pin);  // Print the integer directly

                if (pin != -1) {
                    controlPump(pin, cmd);  // Use cmd instead of commandData.cmd
                } else {
                    Serial.println("Invalid command received.");
                }
            } else {
                Serial.println("Invalid PCU ID");
            }
        }
    }
}
