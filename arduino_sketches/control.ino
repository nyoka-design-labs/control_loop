#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 dac;

#define DAC_RESOLUTION(9)

// voltage range from 0-5
const int LOW_SPEED = 1;
const int MEDIUM_SPEED = 2;
const int HIGH_SPEED = 4;

const int PUMP_RELAY = 11; // Pump control (on/off) pin
const int PUMP_DIRECTION_RELAY = 10; // Pump direction pin
const int SCALE_RELAY = 12; // Relay control pin

const int RELAY_DELAY = 500;
const int PUMP_DIR = 1; // 1=positive, 0=negative

void setup() {
  Serial.begin(9600); // Initialize Serial communication
  pinMode(PUMP_RELAY, OUTPUT); // Initialize the pump control pin as an output
  pinMode(SCALE_RELAY, OUTPUT);
  dac.begin(0x60);

  digitalWrite(SCALE_RELAY, HIGH); // high signal indicates relay is off
  digitalWrite(PUMP_DIRECTION_RELAY, LOW); // pump direction is initially positive
}

void loop() {
  
  if (Serial.available() > 0) {
    int command = Serial.parseInt(); // Read the incoming byte

    switch (command) {
      case 0: { // turn off the pump
        digitalWrite(PUMP_RELAY, LOW);
        break;
      }
      case 1: { // turn on the pump
        digitalWrite(PUMP_RELAY, HIGH);
        break;
      }
      case 2: { // bypass M25 scale autoshutoff (called every ~3 min)
        // switch to ounces
        delay(RELAY_DELAY);
        digitalWrite(SCALE_RELAY, LOW);
        delay(RELAY_DELAY);
        digitalWrite(SCALE_RELAY, HIGH);
        delay(RELAY_DELAY);
        // switch back to grams
        digitalWrite(SCALE_RELAY, LOW);
        delay(RELAY_DELAY);
        digitalWrite(SCALE_RELAY, HIGH);
        break;
      }
      case 3: { // toggle pump direction
        break;
      }
      case 4: { // low pump rate
        dac.setVoltage((LOW_SPEED*4095)/5, false);
        break;
      }
      case 5: { // medium pump rate
        dac.setVoltage((MEDIUM_SPEED*4095)/5, false);
        break;
      }
      case 6: { // high pump rate
        dac.setVoltage((HIGH_SPEED*4095)/5, false);
        break;
      }
    }
  }
}