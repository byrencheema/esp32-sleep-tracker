# Sleep Environment Monitor

ESP32-based sleep environment monitoring system that tracks temperature, humidity, light levels, and motion to calculate a sleep comfort score.

## Hardware

- ESP32 DevKit
- AHT20 Temperature/Humidity Sensor (I2C)
- Photoresistor (GPIO 33)
- PIR Motion Sensor (GPIO 32)
- Green LED - Good conditions (GPIO 26)
- Red LED - Poor conditions (GPIO 27)

## Features

- Real-time environmental monitoring
- Comfort score calculation (0-100) based on:
  - Temperature (ideal: 22°C)
  - Humidity (ideal: 45%)
  - Light levels (ideal: <500)
  - Motion detection
- LED status indicators with variable blink patterns
- Data transmission to remote server via HTTP

## LED Indicators

| Score | Indicator |
|-------|-----------|
| 70-100 | Green LED solid |
| 40-69 | Green LED slow blink |
| 0-39 | Red LED fast blink |

## Setup

1. Install [PlatformIO](https://platformio.org/)
2. Update WiFi credentials in `src/main.cpp`
3. Update server IP if needed
4. Build and upload:
   ```
   pio run -t upload
   ```

## Dependencies

- Adafruit AHTX0
- Adafruit SSD1306
- Adafruit GFX Library
