const int footSwitchPin = 11; // Pump control pin

void setup() {
  Serial.begin(57600); // Initialize Serial communication
  pinMode(footSwitchPin, OUTPUT); // Initialize the pump control pin as an output
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read(); // Read the incoming byte
    if (command == '1') {
      digitalWrite(footSwitchPin, HIGH); // Turn on the pump
    } else if (command == '0') {
      digitalWrite(footSwitchPin, LOW); // Turn off the pump
    }
  }
}
