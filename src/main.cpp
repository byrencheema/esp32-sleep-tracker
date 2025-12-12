#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <HttpClient.h>
#include <Adafruit_AHTX0.h>

#define LIGHT_SENSOR_PIN 33
#define PIR_SENSOR_PIN 32
#define LED_GOOD 26
#define LED_POOR 27

Adafruit_AHTX0 aht;

// WiFi credentials
char ssid[] = "Antonio_iPhone";
char pass[] = "6c905uddqwp9g";

// Server details (update with your AWS IP)
const char serverIP[] = "3.22.233.94";  // Your AWS instance IP
const int serverPort = 5000;

// Ideal sleep conditions
const float IDEAL_TEMP = 22.0;
const float IDEAL_HUMIDITY = 45.0;
const int IDEAL_LIGHT = 500;

int calculateComfortScore(float temp, float humidity, int lightLevel, bool motion) {
  int score = 100;
  
  float tempDiff = abs(temp - IDEAL_TEMP);
  if (tempDiff > 3.0) {
    score -= (tempDiff - 3.0) * 10;
  }
  
  float humidDiff = abs(humidity - IDEAL_HUMIDITY);
  if (humidDiff > 15.0) {
    score -= (humidDiff - 15.0) * 2;
  }
  
  if (lightLevel > IDEAL_LIGHT) {
    score -= (lightLevel - IDEAL_LIGHT) / 20;
  }
  
  if (motion) {
    score -= 15;
  }
  
  return constrain(score, 0, 100);
}

void updateLEDs(int score) {
  static unsigned long lastBlink = 0;
  static bool blinkState = false;
  
  if (score >= 70) {
    digitalWrite(LED_GOOD, HIGH);
    digitalWrite(LED_POOR, LOW);
  }
  else if (score >= 40) {
    if (millis() - lastBlink > 1000) {
      blinkState = !blinkState;
      lastBlink = millis();
    }
    digitalWrite(LED_GOOD, blinkState);
    digitalWrite(LED_POOR, LOW);
  }
  else {
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
  
  // Connect to WiFi
  WiFi.begin(ssid, pass);
  Serial.print("Connecting to WiFi ");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  
  if (!aht.begin()) {
    Serial.println("AHT20 sensor not found!");
    while (1);
  }
  
  Serial.println("Sleep Monitor Ready");
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
  
  // Send data to server
  WiFiClient client;
  HttpClient http(client);
  
  String path = "/?temp=" + String(temp.temperature, 1) + 
                "&hum=" + String(humidity.relative_humidity, 1) +
                "&light=" + String(lightLevel) +
                "&motion=" + String(motionDetected ? 1 : 0) +
                "&score=" + String(comfortScore);
  
  int err = http.get(serverIP, serverPort, path.c_str(), NULL);
  
  if (err == 0) {
    Serial.println("Data sent to server!");
    http.responseStatusCode();
    http.skipResponseHeaders();
  } else {
    Serial.print("Send failed: ");
    Serial.println(err);
  }
  
  http.stop();
  delay(2000);
}