import network
import time
from machine import Pin, PWM, I2C
from umqtt.simple import MQTTClient
import urequests
import json
from lcd_i2c import LCD

# WiFi Configuration
WIFI_SSID = "noid"
WIFI_PASS = "pulogadung90"

# MQTT Configuration
MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = b"/predict/classes"
MQTT_PORT = 1883
CLIENT_ID = "mqttx_05bec4a0"

# API Configuration
API_URL = "https://revoira.vercel.app/session-status"
API_CHECK_INTERVAL = 2  # Seconds

# Servo Configuration
servo1_pin = 12
servo2_pin = 13
servo_freq = 50  # Hz (standard for servos)
min_duty = 20    # 0 degree position
max_duty = 120   # 180 degree position

# LCD Configuration
I2C_ADDR = 0x27
LCD_COLS = 20
LCD_ROWS = 4

# Global state variables
s1 = min_duty
s2 = min_duty
turn_on = False
last_api_check = 0

# Initialize hardware
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
lcd = LCD(I2C_ADDR, LCD_COLS, LCD_ROWS, i2c)
servo1 = PWM(Pin(servo1_pin), freq=servo_freq)
servo2 = PWM(Pin(servo2_pin), freq=servo_freq)
servo1.duty_u16(s1 * 100)  # Convert to 16-bit duty cycle
servo2.duty_u16(s2 * 100)

wlan = network.WLAN(network.STA_IF)
mqtt_client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)

def connect_wifi():
    if wlan.isconnected():
        print("[WiFi] Already connected")
        return
    
    print("\n[WiFi] Connecting to network...")
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    
    for _ in range(20):  # Wait up to 10 seconds
        if wlan.isconnected():
            break
        time.sleep(0.5)
        print(".", end="")
    
    if wlan.isconnected():
        print("\n[WiFi] Connected!")
        print("[WiFi] IP:", wlan.ifconfig()[0])
    else:
        print("\n[WiFi] Connection failed!")

def mqtt_callback(topic, msg):
    global turn_on
    if not turn_on:
        return
    
    message = msg.decode().strip()
    print(f"[MQTT] Received: {message}")
    lcd_update(message)
    
    if message in ["can-bottle", "plastic-bottle", "tetrapak"]:
        print("[System] Valid object detected")
        open_gate()
        time.sleep(3)
    
    print("[System] Resetting gate")
    reset()

def reconnect_mqtt():
    print("[MQTT] Attempting connection...")
    while not mqtt_client.is_connected() and turn_on:
        try:
            mqtt_client.connect()
            mqtt_client.subscribe(MQTT_TOPIC)
            print("[MQTT] Connected and subscribed!")
        except Exception as e:
            print(f"[MQTT] Connection failed: {e}")
            time.sleep(5)

def lcd_update(message):
    print(f"[LCD] Updating: {message}")
    lcd.set_cursor(0, 3)
    lcd.print(message.ljust(20))

def open_gate():
    print("[Servo] Opening gate")
    servo1.duty_u16(max_duty * 100)
    servo2.duty_u16(max_duty * 100)

def reset():
    print("[Servo] Resetting position")
    servo1.duty_u16(s1 * 100)
    servo2.duty_u16(s2 * 100)

def check_api_status():
    global turn_on, last_api_check
    
    if not wlan.isconnected():
        print("[WiFi] Reconnecting...")
        connect_wifi()
        return
    
    try:
        print(f"[API] Requesting: {API_URL}")
        response = urequests.get(API_URL)
        print(f"[API] Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.text)
            new_state = data["turnOn"]
            print(f"[API] New state: {'ON' if new_state else 'OFF'}")
            
            if new_state != turn_on:
                turn_on = new_state
                lcd.clear()
                lcd.set_cursor(0, 0)
                lcd.print("Revoira Connected! " if turn_on else "Scan QR to Start  ")
                lcd.set_cursor(0, 2)
                lcd.print("Detected Object:   ")
                
                if not turn_on:
                    print("[System] Resetting hardware")
                    reset()
        
        response.close()
    except Exception as e:
        print(f"[API] Error: {e}")

# Initial setup
print("[System] Initializing...")
lcd.backlight_on()
lcd.print("Initializing...    ")
connect_wifi()

mqtt_client.set_callback(mqtt_callback)

# Main loop
while True:
    try:
        current_time = time.time()
        if current_time - last_api_check >= API_CHECK_INTERVAL:
            check_api_status()
            last_api_check = current_time
        
        if turn_on:
            if not mqtt_client.is_connected():
                reconnect_mqtt()
            mqtt_client.check_msg()
        else:
            if mqtt_client.is_connected():
                mqtt_client.disconnect()
        
        time.sleep(0.1)
    except KeyboardInterrupt:
        print("[System] Exiting...")
        reset()
        mqtt_client.disconnect()
        lcd.clear()
        lcd.backlight_off()
        break
    except Exception as e:
        print(f"[System] Critical error: {e}")
        time.sleep(5)