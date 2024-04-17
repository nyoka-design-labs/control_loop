const int footSwitchPin = 11; // Pump control pin
const int fsPump2 = 10;
const int SCALE_RELAY = 9;

const int RELAY_DELAY = 500;

void setup() {
  Serial.begin(57600); // Initialize Serial communication
  pinMode(footSwitchPin, OUTPUT); // Initialize the pump control pin as an output
  pinMode(fsPump2, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(SCALE_RELAY, OUTPUT);

  digitalWrite(SCALE_RELAY, HIGH);
  delay(RELAY_DELAY);
  digitalWrite(SCALE_RELAY, LOW);
  delay(RELAY_DELAY);
  digitalWrite(SCALE_RELAY, HIGH);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read(); // Read the incoming byte
    Serial.println(command);
    if (command == '1') {
      digitalWrite(footSwitchPin, HIGH); // Turn on the pump
    } else if (command == '0') {
      digitalWrite(footSwitchPin, LOW); // Turn off the pump
    } else if (command == '3') {
      digitalWrite(fsPump2, HIGH); // turn on pump 2
    } else if (command == '4') {
      digitalWrite(fsPump2, LOW); // turn off pump 2
    } else if (command == '5') {
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
    }
  }
}
