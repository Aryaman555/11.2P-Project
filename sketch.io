#include <WiFiNINA.h>
#include <PubSubClient.h>

const char* ssid = "Aryaman";
const char* pass = "arya2703";
const char* broker = "mqtt-dashboard.com";
const char* clientId = "clientId-YxI557mS3Z";
const char* coTopic = "co_level";

const int MQ9AnalogPin = A0;  // Connect the analog output of the MQ-9 sensor to A1

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

unsigned long lastMillis = 0;
const unsigned long timeout = 60000;

void setup() {
  Serial.begin(9600);
  delay(1000);

  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");

  mqttClient.setServer(broker, 1883);
  pinMode(MQ9AnalogPin, INPUT);
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - lastMillis > timeout) {
    NVIC_SystemReset();
  }

  if (!mqttClient.connected()) {
    if (mqttClient.connect(clientId)) {
      Serial.println("Connected to MQTT broker");
    } else {
      Serial.println("Failed to connect to MQTT broker");
    }
  }

  int coLevel = analogRead(MQ9AnalogPin);

  char coLevelStr[10];
  snprintf(coLevelStr, sizeof(coLevelStr), "%d", coLevel);

  Serial.print("CO Level: ");
  Serial.println(coLevelStr);

  if (mqttClient.publish(coTopic, coLevelStr)) {
    Serial.println("Published CO level to MQTT broker");
  } else {
    Serial.println("Failed to publish CO level to MQTT broker");
  }

  lastMillis = currentMillis;
  delay(1000);
}
