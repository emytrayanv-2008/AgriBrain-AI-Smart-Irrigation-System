/*
 * Arduino Uno Firmware - Smart Irrigation Sensor Unit
 * Capstone Project: AI-Based Smart Irrigation System Using Sensors
 * 
 * Hardware Connections:
 * - Capacitive Soil Moisture Sensor: Analog Pin A0 (VCC: 5V, GND: GND)
 * - DHT11 / DHT22 Sensor: Digital Pin D4 (VCC: 5V, GND: GND)
 * - Rain Drop Sensor: Digital Pin D2 (Active LOW)
 * - 5V Single Channel Relay Module: Digital Pin D8 (Active LOW/HIGH)
 * - DC Submersible Water Pump (5V/12V): Connected through Relay COM and NO terminals
 */

#include <DHT.h>

#define DHTPIN 4
#define DHTTYPE DHT11   // Set to DHT22 if using white DHT22 sensor
#define SOIL_PIN A0
#define RAIN_PIN 2
#define RELAY_PIN 8

DHT dht(DHTPIN, DHTTYPE);

// Calibration constants for Capacitive Soil Moisture Sensor
// In air (dry): ~620 analog count
// In glass of water (wet): ~280 analog count
const int AIR_VALUE = 620;
const int WATER_VALUE = 280;

void setup() {
  Serial.begin(9600);
  while (!Serial) { ; } // wait for serial port to connect
  
  pinMode(RAIN_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  
  // Initialize Relay to OFF state (assuming active LOW relay, HIGH = OFF)
  digitalWrite(RELAY_PIN, HIGH);
  
  dht.begin();
  delay(1000);
}

void loop() {
  // Read DHT11 Temperature and Humidity
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature(); // Celsius
  
  // Read Raw Soil Moisture
  int rawMoisture = analogRead(SOIL_PIN);
  
  // Calibrate raw analog reading to percentage (0% to 100%)
  float soilMoisture = map(rawMoisture, AIR_VALUE, WATER_VALUE, 0, 100);
  soilMoisture = constrain(soilMoisture, 0.0, 100.0);
  
  // Read Rain Sensor (0 = Rain, 1 = Dry for typical active LOW rain module)
  int rainDigital = digitalRead(RAIN_PIN);
  int isRaining = (rainDigital == LOW) ? 1 : 0;
  
  // Check if valid sensor readings
  if (isnan(humidity) || isnan(temperature)) {
    humidity = 55.0;
    temperature = 28.0;
  }
  
  // Transmit JSON Telemetry String over Serial
  Serial.print("{\"moisture\":");
  Serial.print(soilMoisture, 1);
  Serial.print(",\"temp\":");
  Serial.print(temperature, 1);
  Serial.print(",\"humidity\":");
  Serial.print(humidity, 1);
  Serial.print(",\"rain\":");
  Serial.print(isRaining);
  Serial.println("}");
  
  // Listen for Actuation Commands from Python / AI System
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd == "PUMP_ON") {
      digitalWrite(RELAY_PIN, LOW); // Energize relay
    } else if (cmd == "PUMP_OFF") {
      digitalWrite(RELAY_PIN, HIGH); // De-energize relay
    }
  }
  
  delay(2000); // 2-second telemetry cycle
}
