#include <Adafruit_MCP4725.h>
#include <Wire.h>
Adafruit_MCP4725 dac;

// Define pin assignments for all pumps
const int blackPump1Pin = 12;
const int blackPump2Pin = 11;
const int blackPump3Pin = 10;
const int blackPump4Pin = 9;
const int blackPump5Pin = 8;
const int whitePump1Pin = 7;
const int whitePump2Pin = 6;
const int whitePump3Pin = 5;

const int dymoRelayPin = 4;
const int RELAY_DELAY = 500;

void setup() {
    Serial.begin(9600);
    pinMode(blackPump1Pin, OUTPUT);
    pinMode(blackPump2Pin, OUTPUT);
    pinMode(blackPump3Pin, OUTPUT);
    pinMode(blackPump4Pin, OUTPUT);
    pinMode(blackPump5Pin, OUTPUT);
    pinMode(whitePump1Pin, OUTPUT);
    pinMode(whitePump2Pin, OUTPUT);
    pinMode(whitePump3Pin, OUTPUT);
    dac.begin(0x60);

    // switch the units on dymo from lb to grams
    digitalWrite(dymoRelayPin, HIGH);
    delay(RELAY_DELAY);
    digitalWrite(dymoRelayPin, LOW);
    delay(RELAY_DELAY);
    digitalWrite(dymoRelayPin, HIGH);
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        if (command.startsWith("R")) {
            // Handle RPM setting for blackPump1
            int rpm = command.substring(1).toInt(); // Extract RPM value from command
            dac.setVoltage((rpm * 4095) / 5, false);
            digitalWrite(blackPump1Pin, HIGH);
        }
        else if (command.startsWith("T")) {
            toggleRelayTwice();
        }
        else if (command.startsWith("S")) {
            toggleRelayOnce();
        }
         else {
            // Handle regular pump commands
            int cmd = command.toInt(); // Convert command to integer
            handlePumpCommand(cmd);
        }
    }
}

void handlePumpCommand(int cmd) {
    int pin;
    switch (cmd) {
        case 0: case 1: pin = blackPump1Pin; break;
        case 2: case 3: pin = blackPump2Pin; break;
        case 4: case 5: pin = blackPump3Pin; break;
        case 6: case 7: pin = blackPump4Pin; break;
        case 8: case 9: pin = blackPump5Pin; break;
        case 10: case 11: pin = whitePump1Pin; break;
        case 12: case 13: pin = whitePump2Pin; break;
        case 14: case 15: pin = whitePump3Pin; break;
        default: return; // Ignore unknown commands
    }
    digitalWrite(pin, cmd % 2 == 1 ? HIGH : LOW); // Odd commands turn ON, even commands turn OFF
}

void toggleRelayTwice() {
    for (int i = 0; i < 2; i++) {
        digitalWrite(RELAY_PIN, LOW);
        delay(500);
        digitalWrite(RELAY_PIN, HIGH);
        delay(500);
    }
}

void toggleRelayOnce() {
    digitalWrite(RELAY_PIN, LOW);
    delay(500);
    digitalWrite(RELAY_PIN, HIGH);
    delay(500);
}