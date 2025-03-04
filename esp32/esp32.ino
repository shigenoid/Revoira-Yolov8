#include <ESP32Servo.h>

// Inisialisasi servo
Servo servo1;
Servo servo2;
Servo servo3;

// Pin untuk LED dan servo
const int led1 = 16;  // LED hijau
const int led2 = 15;  // LED merah
const int servo1Pin = 12;
const int servo2Pin = 13;
const int servo3Pin = 14;

int s1 = 45;
int s2 = 60;
int s3 = 135;

void setup() {
  // Inisialisasi serial
  Serial.begin(115200);

  // Attach servo ke pin
  servo1.attach(servo1Pin);
  servo2.attach(servo2Pin);
  servo3.attach(servo3Pin);

  // Set posisi awal servo
  servo1.write(s1);
  delay(2000);
  servo2.write(s2);
  delay(2000);
  servo3.write(s3); // -45 = ke kanan, +45 = ke kiri
  delay(2000);

  // Inisialisasi LED
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  digitalWrite(led1, LOW);
  digitalWrite(led2, LOW);
}

void loop() {
  // Baca perintah dari serial
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Hilangkan spasi atau newline

    if (command == "NONE") {
      reset();
    } else if (command == "GLASS") {
      invalid();
      delay(1000);
      servo_reset();
      delay(5000);
    } else if (command == "CAN") {
      valid();
      delay(1000);
      servo3.write(s3 + 45);
      delay(5000);
      openGate();
      delay(5000);
     } else if (command == "PLASTIC") {
      valid();
      delay(1000);
      servo3.write(s3);
      delay(5000);
      openGate();
      delay(5000);
     } else if (command == "TETRAPAK") {
        valid();
        delay(1000);
        servo3.write(s3 - 45);
        delay(5000);
        openGate();
        delay(5000);
    }
    reset();
  }     
}

void openGate() {
  servo1.write(s1 + 90);
  servo2.write(s2 + 90);
}

void reset() {
  pinMode(led1, LOW);
  pinMode(led2, LOW);
  delay(1000);
  servo_reset();
}

void valid() {
  pinMode(led1, HIGH);
  pinMode(led2, LOW);
}

void invalid() {
  pinMode(led1, LOW);
  pinMode(led2, HIGH);
}

void servo_reset() {
  servo1.write(s1);
  servo2.write(s2);
  delay(1000);
  servo3.write(s3);
}
