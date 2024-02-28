int x;

void setup() { 
  Serial.begin(115200); // Make sure this baud rate matches the one in your Python script
  pinMode(LED_BUILTIN, OUTPUT); // Initialize the digital pin as an output
}

void loop() { 
  while (!Serial.available()); // Wait for data
  x = Serial.readString().toInt(); // Read the incoming data as integer
  Serial.print(x + 1); // Send back the incremented value
  delay(1000);
  
  for (int i = 0; i < x; i++) {
    digitalWrite(LED_BUILTIN, HIGH); // Turn the LED on
    delay(500); // Wait for half a second
    digitalWrite(LED_BUILTIN, LOW); // Turn the LED off
    delay(500); // Wait for half a second
  }
}
