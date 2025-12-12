#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_AHTX0.h>

#define LIGHT_SENSOR_PIN 33
#define PIR_SENSOR_PIN 32
#define LED_GOOD 26
#define LED_POOR 27

Adafruit_AHTX0 aht;

// Ideal sleep conditions
const float IDEAL_TEMP = 22.0;
const float IDEAL_HUMIDITY = 45.0;
const int IDEAL_LIGHT = 500;  // Adjust based on your readings

int calculateComfortScore(float temp, float humidity, int lightLevel, bool motion) {
  int score = 100;
  
  // Temperature penalty (±3°C is acceptable)
  float tempDiff = abs(temp - IDEAL_TEMP);
  if (tempDiff > 3.0) {
    score -= (tempDiff - 3.0) * 10;
  }
  
  // Humidity penalty (±15% is acceptable)
  float humidDiff = abs(humidity - IDEAL_HUMIDITY);
  if (humidDiff > 15.0) {
    score -= (humidDiff - 15.0) * 2;
  }
  
  // Light penalty (should be dark for sleep)
  if (lightLevel > IDEAL_LIGHT) {
    score -= (lightLevel - IDEAL_LIGHT) / 20;
  }
  
  // Motion penalty (restlessness during sleep)
  if (motion) {
    score -= 15;
  }
  
  return constrain(score, 0, 100);
}

void updateLEDs(int score) {
  static unsigned long lastBlink = 0;
  static bool blinkState = false;
  
  if (score >= 70) {
    // Good conditions - solid on LED_GOOD
    digitalWrite(LED_GOOD, HIGH);
    digitalWrite(LED_POOR, LOW);
  }
  else if (score >= 40) {
    // Fair - slow blink on LED_GOOD (1 Hz)
    if (millis() - lastBlink > 1000) {
      blinkState = !blinkState;
      lastBlink = millis();
    }
    digitalWrite(LED_GOOD, blinkState);
    digitalWrite(LED_POOR, LOW);
  }
  else {
    // Poor - fast blink on LED_POOR (4 Hz)
    if (millis() - lastBlink > 250) {
      blinkState = !blinkState;
      lastBlink = millis();
    }
    digitalWrite(LED_GOOD, LOW);
    digitalWrite(LED_POOR, blinkState);
  }
}

void setup() {
  Serial.begin(9600);
  Wire.begin();
  
  pinMode(LED_GOOD, OUTPUT);
  pinMode(LED_POOR, OUTPUT);
  pinMode(PIR_SENSOR_PIN, INPUT);
  
  if (!aht.begin()) {
    Serial.println("AHT20 sensor not found!");
    while (1);
  }
  
  Serial.println("Sleep Monitor Ready");
  Serial.println("Temp | Humidity | Light | Motion | Score");
  
  // Give PIR sensor time to calibrate
  Serial.println("Calibrating PIR sensor (30 sec)...");
  delay(30000);
  Serial.println("Ready!");
}

void loop() {
  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);
  
  int lightLevel = analogRead(LIGHT_SENSOR_PIN);
  bool motionDetected = digitalRead(PIR_SENSOR_PIN);
  
  int comfortScore = calculateComfortScore(temp.temperature, 
                                          humidity.relative_humidity,
                                          lightLevel,
                                          motionDetected);
  
  updateLEDs(comfortScore);
  
  // Serial logging
  Serial.printf("%.1f°C | %.1f%% | %d | %s | Score: %d\n",
                temp.temperature, 
                humidity.relative_humidity,
                lightLevel,
                motionDetected ? "MOTION" : "Still",
                comfortScore);
  
  delay(2000);
}