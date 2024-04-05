const int footSwitchPin = 11; // Pump control pin
const int RELAY_SIGNAL = 13; // Relay pin

void setup() {
  Serial.begin(57600); // Initialize Serial communication
  pinMode(footSwitchPin, OUTPUT); // Initialize the pump control pin as an output
  pinMode(RELAY_SIGNAL, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(RELAY_SIGNAL, HIGH);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read(); // Read the incoming byte
    if (command == '1') {
      digitalWrite(footSwitchPin, HIGH); // Turn on the pump
      digitalWrite(LED_BUILTIN, HIGH);
    } else if (command == '0') {
      digitalWrite(LED_BUILTIN, LOW);
      digitalWrite(footSwitchPin, LOW); // Turn off the pump
    } else if (command == '2') {
      digitalWrite(RELAY_SIGNAL, LOW);
      delay(500);
      digitalWrite(RELAY_SIGNAL, HIGH);
      delay(500);
      digitalWrite(RELAY_SIGNAL, LOW);
      delay(500);
      digitalWrite(RELAY_SIGNAL, HIGH);
    }
  }
}
