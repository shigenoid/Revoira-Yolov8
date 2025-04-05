#include <WiFi.h>
#include <PubSubClient.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h>

// Wifi
#define WIFI_SSID "noid"
#define WIFI_PASS "pulogadung90"

// MQTT
#define MQTT_BROKER "broker.emqx.io"  
#define MQTT_TOPIC "/predict/classes"
#define MQTT_PORT 1883
#define CLIENT_ID "mqttx_05bec4a0"

LiquidCrystal_I2C lcd(0x27, 20, 4);  
WiFiClient espClient;
PubSubClient client(espClient);

Servo servo1;
Servo servo2;
Servo servo3;

const int servo1Pin = 12;
const int servo2Pin = 13;
const int servo3Pin = 14; // The bottom servo

// Servo starting angle
int s1 = 0;
int s2 = 0;
int s3 = 135;

// Functions
void setup_wifi();
void mqtt_callback(char* topic, byte* payload, unsigned int length);
void reconnect();
void lcd_update(String message);
void openGate();
void reset();

void setup() {
  Serial.begin(115200);

  // Servo Setup
  servo1.attach(servo1Pin);
  servo2.attach(servo2Pin);
  servo3.attach(servo3Pin);

  servo1.write(s1);
  delay(2000);
  servo2.write(s2);
  delay(2000);
  servo3.write(s3); // -45 = ke kanan, +45 = ke kiri
  delay(2000);
  
  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);            
  lcd.print("Revoira ⸙--------");     
  lcd.setCursor(0, 2);           
  lcd.print("Detected Object:");    
  
  setup_wifi();
  client.setServer(MQTT_BROKER, MQTT_PORT);
  client.setCallback(mqtt_callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}

void setup_wifi() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  // Convert payload to String
  String message = String((char*)payload).substring(0, length);
  message.trim(); // Remove any whitespace or special characters
  
  if (message == "NONE") {
    lcd_update(message);
    reset();
  }
  else if (message == "can-bottle") {
    lcd_update(message);
    delay(1000);
    servo3.write(s3 + 45);
    delay(1000);
    openGate();
    delay(3000);
  }
  else if (message == "glass-bottle") {
    lcd_update(message);
    reset();
  }
  else if (message == "plastic-bottle") {
    lcd_update(message);
    delay(1000);
    servo3.write(s3);
    delay(1000);
    openGate();
    delay(3000);
  }
  else if (message == "tetrapak") {
    lcd_update(message);
    delay(1000);
    servo3.write(s3 - 45);
    delay(1000);
    openGate();
    delay(3000);
  }
  reset();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect(CLIENT_ID)) {
      Serial.println("Connected to MQTT!");
      client.subscribe(MQTT_TOPIC);
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5s...");
      delay(5000);
    }
  }
}

void lcd_update(String message){
  lcd.setCursor(0, 3);
  lcd.print(message + "      ");
}

void openGate() {
  servo1.write(s1 + 180);
  servo2.write(s2 + 180);
}

void reset() {
  servo1.write(s1);
  delay(500);
  servo2.write(s2);
}
