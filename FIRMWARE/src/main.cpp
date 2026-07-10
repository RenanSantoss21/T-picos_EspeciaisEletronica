#include <Arduino.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include "secrets.h"
#include "PayloadHandler.h"

// Pin Definitions
#define LED1_PIN 27
#define LED2_PIN 33
#define DHT_PIN 18
#define DHT_TYPE DHT11

// Global Objects
DHT dht(DHT_PIN, DHT_TYPE);
WebSocketsClient webSocket;

// Timing variables for telemetry push
unsigned long lastTelemetryTime = 0;
const unsigned long TELEMETRY_INTERVAL = 2000; // 2 seconds

// State for LED blinking
String current_pattern = "normal";
unsigned long lastBlinkTime = 0;
bool ledState = false;
bool leds_enabled = true;

// Function to handle WebSocket events
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("[WSc] Disconnected!");
            break;
        case WStype_CONNECTED:
            Serial.printf("[WSc] Connected to url: %s\n", payload);
            break;
        case WStype_TEXT: {
            Serial.printf("[WSc] get text: %s\n", payload);

            // Parse JSON payload
            JsonDocument doc;
            DeserializationError error = deserializeJson(doc, payload);

            if (error) {
                Serial.print(F("[WSc] deserializeJson() failed: "));
                Serial.println(error.f_str());
                return;
            }

            // Update pattern if present in the JSON
            if (!doc["pattern"].isNull()) {
                current_pattern = doc["pattern"].as<String>();
                Serial.printf("Pattern set to %s\n", current_pattern.c_str());
            }

            if (!doc["leds_on"].isNull()) {
                leds_enabled = doc["leds_on"].as<bool>();
            }
            break;
        }
        case WStype_BIN:
        case WStype_ERROR:
        case WStype_FRAGMENT_TEXT_START:
        case WStype_FRAGMENT_BIN_START:
        case WStype_FRAGMENT:
        case WStype_FRAGMENT_FIN:
        case WStype_PING:
        case WStype_PONG:
            break;
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\nStarting Sensor Node...");

    // Initialize Pins
    pinMode(LED1_PIN, OUTPUT);
    pinMode(LED2_PIN, OUTPUT);
    digitalWrite(LED1_PIN, LOW);
    digitalWrite(LED2_PIN, LOW);

    // Initialize DHT Sensor
    dht.begin();

    // Connect to WiFi
    Serial.printf("Connecting to WiFi: %s\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected.");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());

    // Setup WebSocket HTTP (Localtunnel)
    webSocket.begin(WS_HOST, WS_PORT, WS_URL);
    webSocket.setExtraHeaders("Bypass-Tunnel-Reminder: true\r\nngrok-skip-browser-warning: 1");
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);
}

void loop() {
    // Keep WebSocket connection alive and process incoming messages
    webSocket.loop();

    // Push telemetry data every TELEMETRY_INTERVAL
    if (millis() - lastTelemetryTime >= TELEMETRY_INTERVAL) {
        lastTelemetryTime = millis();

        if (webSocket.isConnected()) {
            // Read DHT11
            float humidity = dht.readHumidity();
            float temperature = dht.readTemperature();

            // Check if any reads failed
            if (isnan(humidity) || isnan(temperature)) {
                Serial.println(F("Failed to read from DHT sensor!"));
            } else {
                // Use the testable telemetry builder
                String jsonString = buildTelemetryJson(temperature, humidity);

                // Send over WebSocket
                webSocket.sendTXT(jsonString);
                Serial.printf("Sent telemetry: %s\n", jsonString.c_str());
            }
        }
    }

    // LED Blinking Logic based on current_pattern
    if (!leds_enabled || current_pattern == "normal") {
        digitalWrite(LED1_PIN, LOW);
        digitalWrite(LED2_PIN, LOW);
        ledState = false;
    } 
    else if (current_pattern == "upper_alert") {
        if (millis() - lastBlinkTime >= 100) {
            lastBlinkTime = millis();
            ledState = !ledState;
            digitalWrite(LED1_PIN, ledState ? HIGH : LOW);
            digitalWrite(LED2_PIN, ledState ? HIGH : LOW);
        }
    }
    else if (current_pattern == "lower_alert") {
        if (millis() - lastBlinkTime >= 300) {
            lastBlinkTime = millis();
            ledState = !ledState;
            digitalWrite(LED1_PIN, ledState ? HIGH : LOW);
            digitalWrite(LED2_PIN, !ledState ? HIGH : LOW);
        }
    }
    else if (current_pattern == "critical_mixed") {
        if (millis() - lastBlinkTime >= 50) {
            lastBlinkTime = millis();
            ledState = !ledState;
            digitalWrite(LED1_PIN, ledState ? HIGH : LOW);
            digitalWrite(LED2_PIN, !ledState ? HIGH : LOW);
        }
    }
}
