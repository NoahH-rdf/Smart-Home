#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ESP32Servo.h>

// WiFi (Wokwi-intern)
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";

// MQTT-Broker
const char* MQTT_BROKER = "broker.hivemq.com";
const int   MQTT_PORT   = 1883;
const char* CLIENT_ID   = "smarthome-esp32-julius";

// Pins
#define LED_PIN   2
#define BTN_PIN   4
#define DHT_PIN   15
#define PIR_PIN   13
#define SERVO_PIN 12

// Topics
#define TOPIC_LIGHT       "home/livingroom/light"
#define TOPIC_BLINDS      "home/livingroom/blinds"
#define TOPIC_TEMPERATURE "home/kitchen/temperature"
#define TOPIC_PIR         "home/bedroom/pir"
#define TOPIC_BUTTON      "home/button"
#define TOPIC_GESTURE     "home/gesture"

DHT dht(DHT_PIN, DHT22);
Servo blindsServo;
WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

unsigned long lastSensorRead = 0;
bool lastBtnState = HIGH;
bool lastPirState = LOW;

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  String t = String(topic);

  if (t == TOPIC_LIGHT || t == TOPIC_GESTURE) {
    if (msg == "ON" || msg == "licht_an") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("[LED] AN");
    } else if (msg == "OFF" || msg == "licht_aus") {
      digitalWrite(LED_PIN, LOW);
      Serial.println("[LED] AUS");
    }
  }

  if (t == TOPIC_BLINDS) {
    if (msg == "OPEN") {
      blindsServo.write(90);
      Serial.println("[ROLLO] Offen");
    } else if (msg == "CLOSE") {
      blindsServo.write(0);
      Serial.println("[ROLLO] Geschlossen");
    }
  }
}

void connectWiFi() {
  Serial.print("Verbinde mit WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" verbunden!");
}

void connectMQTT() {
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setCallback(mqttCallback);
  while (!mqtt.connected()) {
    Serial.print("Verbinde mit MQTT...");
    if (mqtt.connect(CLIENT_ID)) {
      Serial.println(" verbunden!");
      mqtt.subscribe(TOPIC_LIGHT);
      mqtt.subscribe(TOPIC_BLINDS);
      mqtt.subscribe(TOPIC_GESTURE);
      Serial.println("Subscribed: " TOPIC_LIGHT ", " TOPIC_BLINDS ", " TOPIC_GESTURE);
    } else {
      Serial.print(" Fehler rc=");
      Serial.println(mqtt.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BTN_PIN, INPUT_PULLUP);
  pinMode(PIR_PIN, INPUT);

  blindsServo.attach(SERVO_PIN);
  blindsServo.write(0);

  dht.begin();
  connectWiFi();
  connectMQTT();
}

void loop() {
  if (!mqtt.connected()) connectMQTT();
  mqtt.loop();

  // Taster prüfen
  bool btnState = digitalRead(BTN_PIN);
  if (btnState == LOW && lastBtnState == HIGH) {
    mqtt.publish(TOPIC_BUTTON, "PRESSED");
    Serial.println("[BUTTON] Gedrückt -> MQTT gesendet");
    delay(50);
  }
  lastBtnState = btnState;

  // PIR prüfen
  bool pirState = digitalRead(PIR_PIN);
  if (pirState != lastPirState) {
    mqtt.publish(TOPIC_PIR, pirState ? "DETECTED" : "CLEAR");
    Serial.printf("[PIR] %s\n", pirState ? "Bewegung erkannt" : "Klar");
    lastPirState = pirState;
  }

  // DHT22 alle 5 Sekunden
  if (millis() - lastSensorRead >= 5000) {
    lastSensorRead = millis();
    float temp = dht.readTemperature();
    float hum  = dht.readHumidity();
    if (!isnan(temp) && !isnan(hum)) {
      char buf[32];
      snprintf(buf, sizeof(buf), "%.1f", temp);
      mqtt.publish(TOPIC_TEMPERATURE, buf);
      Serial.printf("[DHT22] Temp: %.1f°C  Feuchte: %.1f%%\n", temp, hum);
    }
  }
}
