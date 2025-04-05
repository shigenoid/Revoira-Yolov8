#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// WiFi credentials
const char* ssid = "RYAN AZMII";
const char* password = "sempati2148";

// API Endpoint
const char* apiUrl = "https://revoira.vercel.app/session-status";  // Change to your API's actual IP

// Initialize LCD (I2C Address 0x27, 20x4)
LiquidCrystal_I2C lcd(0x27, 20, 4);

void setup() {
    Serial.begin(115200);
    
    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(1000);
    }
    Serial.println("\nConnected to WiFi!");

    // Initialize LCD
    lcd.init();
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Waiting for QR...");
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(apiUrl);  // Connect to API
        int httpResponseCode = http.GET();

        if (httpResponseCode == 200) {
            String payload = http.getString();
            Serial.println("API Response: " + payload);

            // Parse JSON response
            StaticJsonDocument<200> doc;
            DeserializationError error = deserializeJson(doc, payload);

            if (!error) {
                bool turnOn = doc["turnOn"];

                lcd.clear();
                lcd.setCursor(0, 1);

                if (turnOn) {
                    lcd.print("Revoira Connected!");
                } else {
                    lcd.print("Revoira Disconnected...");
                }
            } else {
                Serial.println("JSON Parsing Error!");
            }
        } else {
            Serial.print("Error fetching data: ");
            Serial.println(httpResponseCode);
        }

        http.end();
    }

    delay(5000);  // Check status every 5 seconds
}
