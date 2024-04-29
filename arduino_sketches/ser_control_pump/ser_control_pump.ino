const int feedPumpPin = 11; // Pump control pin
const int basePumpPin = 10;
const int bufferPumpPin = 9;
const int lysatePumpPin = 8;
const int RELAY_PIN = 12;

const int RELAY_DELAY = 500;

void setup() {
  Serial.begin(9600); // Initialize Serial communication
  pinMode(feedPumpPin, OUTPUT); // Initialize the pump control pin as an output
  pinMode(basePumpPin, OUTPUT);
  pinMode(bufferPumpPin, OUTPUT);
  pinMode(lysatePumpPin, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);

  digitalWrite(RELAY_PIN, HIGH);
  delay(RELAY_DELAY);
  digitalWrite(RELAY_PIN, LOW);
  delay(RELAY_DELAY);
  digitalWrite(RELAY_PIN, HIGH);
  
}

void loop() {
  digitalWrite(feedPumpPin, HIGH);
  digitalWrite(feedPumpPin, LOW);
  digitalWrite(feedPumpPin, HIGH);

  if (Serial.available() > 0) {
    char command = Serial.read(); // Read the incoming byte
    Serial.println(command);
    if (command == '1') {
      digitalWrite(feedPumpPin, HIGH); // Turn on feed pump
    } else if (command == '0') {
      digitalWrite(feedPumpPin, LOW); // Turn off feed pump
    } else if (command == '2') {
      digitalWrite(basePumpPin, LOW); // turn off base pump
    } else if (command == '3') {
      digitalWrite(basePumpPin, HIGH); // turn on base pump
    } else if (command == '4') {
      digitalWrite(bufferPumpPin, LOW); // turn off buffer pump
    } else if (command == '5') {
      digitalWrite(bufferPumpPin, HIGH); // turn on buffer pump
    } else if (command == '6') {
      digitalWrite(lysatePumpPin, LOW); // turn off lysate pump
    } else if (command == '7') {
      digitalWrite(lysatePumpPin, HIGH); // turn on lysate pump
    } else if (command == '8') {
      delay(RELAY_DELAY);
      digitalWrite(RELAY_PIN, LOW);
      delay(RELAY_DELAY);
      digitalWrite(RELAY_PIN, HIGH);
      delay(RELAY_DELAY);
      // switch back to grams
      digitalWrite(RELAY_PIN, LOW);
      delay(RELAY_DELAY);
      digitalWrite(RELAY_PIN, HIGH);
    }
  }
}
