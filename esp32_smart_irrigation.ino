/*
 * ESP32 NodeMCU Firmware - IoT AI Smart Irrigation System
 * Capstone Project: AI-Based Smart Irrigation System Using Sensors
 * 
 * Hardware Connections:
 * - Capacitive Soil Moisture Sensor: GPIO 34 (ADC1_CH6) (3.3V, GND)
 * - DHT11 / DHT22 Sensor: GPIO 4 (3.3V, GND)
 * - Rain Drop Sensor: GPIO 15 (Active LOW)
 * - 5V/3.3V Relay Module: GPIO 23
 * - Mini Submersible DC Pump: Driven via Relay
 */

#include <WiFi.h>
#include <DHT.h>

#define DHTPIN 4
#define DHTTYPE DHT11   // or DHT22
#define SOIL_PIN 34
#define RAIN_PIN 15
#define RELAY_PIN 23

DHT dht(DHTPIN, DHTTYPE);

// ESP32 has a 12-bit ADC (0 - 4095)
const int AIR_VALUE = 3200;    // Dry sensor in air
const int WATER_VALUE = 1350;  // Submerged in water

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  pinMode(RAIN_PIN, INPUT_PULLUP);
  pinMode(RELAY_PIN, OUTPUT);
  
  // Set default relay state to OFF
  digitalWrite(RELAY_PIN, LOW); // Active high for 3.3V optocoupler
  
  dht.begin();
  Serial.println("[ESP32] Smart Irrigation IoT Node Initialized.");
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  int rawMoisture = analogRead(SOIL_PIN);
  float soilMoisture = map(rawMoisture, AIR_VALUE, WATER_VALUE, 0, 100);
  soilMoisture = constrain(soilMoisture, 0.0, 100.0);
  
  int rainDigital = digitalRead(RAIN_PIN);
  int isRaining = (rainDigital == LOW) ? 1 : 0;
  
  if (isnan(humidity) || isnan(temperature)) {
    humidity = 58.0;
    temperature = 29.0;
  }
  
  // Broadcast JSON String to Serial / Python Bridge
  Serial.print("{\"moisture\":");
  Serial.print(soilMoisture, 1);
  Serial.print(",\"temp\":");
  Serial.print(temperature, 1);
  Serial.print(",\"humidity\":");
  Serial.print(humidity, 1);
  Serial.print(",\"rain\":");
  Serial.print(isRaining);
  Serial.println("}");
  
  // Actuation Command Parser
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "PUMP_ON") {
      digitalWrite(RELAY_PIN, HIGH);
    } else if (cmd == "PUMP_OFF") {
      digitalWrite(RELAY_PIN, LOW);
    }
  }
  
  delay(2000);
}
