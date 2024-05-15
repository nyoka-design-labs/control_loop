//#include <Adafruit_MCP4725.h>
//#include <Wire.h>
////Adafruit_MCP4725 dac;
//
//#define DAC_RESOLUTION  (9)
//
//const int feedPumpPin = 12; // Pump control pin
//const int basePumpPin = 11;
//const int bufferPumpPin = 9;
//const int lysatePumpPin = 8;
//const int RELAY_PIN = 7;
//
//const int RELAY_DELAY = 500;
//
//
//
//void setup() {
//  Serial.begin(9600); // Initialize Serial communication
//  pinMode(feedPumpPin, OUTPUT); // Initialize the pump control pin as an output
//  pinMode(basePumpPin, OUTPUT);
//  pinMode(bufferPumpPin, OUTPUT);
//  pinMode(lysatePumpPin, OUTPUT);
//
//  pinMode(LED_BUILTIN, OUTPUT);
//  pinMode(RELAY_PIN, OUTPUT);
//
//  digitalWrite(feedPumpPin, LOW);
//  digitalWrite(basePumpPin, LOW);
//  digitalWrite(bufferPumpPin, LOW);
//  digitalWrite(lysatePumpPin, LOW);
//
//  dac.begin(0x60);
//
//
//  digitalWrite(RELAY_PIN, HIGH);
//  delay(RELAY_DELAY);
//  digitalWrite(RELAY_PIN, LOW);
//  delay(RELAY_DELAY);
//  digitalWrite(RELAY_PIN, HIGH);
//
//
//}
//
//void loop() {
//
//  if (Serial.available() > 0) {
//    char command = Serial.read(); // Read the incoming byte
//    Serial.println(command);
//    if  (command == '0') {
//      digitalWrite(feedPumpPin, LOW); // Turn off feed pump
//    } 
//    else if (command == '1') {
//      digitalWrite(feedPumpPin, HIGH); // Turn on feed pump (for some reason setting the pin low turns pump on)
//    } 
//    
//    else if (command == '2') {
//      digitalWrite(basePumpPin, LOW); // turn off base pump
//    } 
//    
//    else if (command == '3') {
//      digitalWrite(basePumpPin, HIGH); // turn on base pump
//    } 
//    
//    else if (command == '4') {
//      digitalWrite(bufferPumpPin, LOW); // turn off buffer pump
//    } 
//    
//    else if (command == '5') {
//      digitalWrite(bufferPumpPin, HIGH); // turn on buffer pump
//    } 
//    
//    else if (command == '6') {
//      digitalWrite(lysatePumpPin, LOW); // turn off lysate pump
//    } 
//    
//    else if (command == '7') {
//      digitalWrite(lysatePumpPin, HIGH); // turn on lysate pump
//    } 
//    
//    // IGNORE commands 8 and a
//    else if (command == '8') {
//      // switches the units on the Dymo Scale twice
//      delay(RELAY_DELAY);
//      digitalWrite(RELAY_PIN, LOW);
//      delay(RELAY_DELAY);
//      digitalWrite(RELAY_PIN, HIGH);
//      delay(RELAY_DELAY);
//      // switch back to grams
//      digitalWrite(RELAY_PIN, LOW);
//      delay(RELAY_DELAY);
//      digitalWrite(RELAY_PIN, HIGH);
//    }
//    else if (command == 'a') {
//      // switches the units on the Dymo Scale once
//      delay(RELAY_DELAY);
//      digitalWrite(RELAY_PIN, LOW);
//      delay(RELAY_DELAY);
//      digitalWrite(RELAY_PIN, HIGH);
//      delay(RELAY_DELAY);
//    }
//
//    else if (command == '9') {
//        float voltage = Serial.parseFloat();
//        delay(RELAY_DELAY);
//        digitalWrite(blackPump1Pin, LOW); // Turn off feed pump
//        delay(RELAY_DELAY);
//        dac.setVoltage((voltage*4095)/5, false);
//        delay(RELAY_DELAY);
//        digitalWrite(blackPump1Pin, HIGH); // Turn on feed pump (for some reason setting the pin low turns pump on)
//        delay(RELAY_DELAY);
//    }
//  }
//}
