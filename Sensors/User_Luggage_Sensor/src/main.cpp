#include <BTstackLib.h>
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_NeoPixel.h>
#include <WiFi.h> 
#include <ArduinoJson.h>
#include "AsyncMqtt_Generic.h"
#include "./env.cpp"


/*
 * Listen for BLE Broadcasts
 * Take details of BLE Broadcasts
 * Stop listening for BLE Broadcasts
 * Determine which signal received was the strongest
 * Copy the MajorID and send to server
*/

/*
 * Display a colour correspoding to Luggage / User colour
 * Two Picos that have the same colour = User & Luggage Pair 
*/


//MQTT Stuff
#define MQTT_SERVER "mqtt.flespi.io"
#define MQTT_PORT 1883

#ifndef MQTT_TOKEN
#define MQTT_TOKEN ""
#endif

AsyncMqttClient mqttClient;
bool connectedToMQTT = false;

// Function Declarations:
void onMQTTConnect(bool sessionPresent);
void onMQTTDisconnect(AsyncMqttClientDisconnectReason reason);
void onMQTTMessage(char* topic, char* payload, const AsyncMqttClientMessageProperties& properties,
                   const size_t& len, const size_t& index, const size_t& total);
void onMqttPublish(const uint16_t& packetId);


// For LED Stuff:
Adafruit_NeoPixel WS2812B(3, 6, NEO_GRB + NEO_KHZ800);

//-- defines OLED screen dimensions ---
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET    -1 // Reset pin #
#define SCREEN_ADDRESS 0x3C // OLED I2C address
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define SCAN_DURATION 9500
#define WAIT_DURATION 500

unsigned long lastActionTime = 0;
bool isScanning = false;

int oldMajorID = -1; // The room the user / luggage is currently in, according to the majorID picked up


int strongestMajorID = -1;
int strongestRSSI = -10000;

// WiFi Stuff:
const char* ssid = "grp3"; // CHANGE THIS FOR DIFFERENT NETWORKS (FIND ON ROUTERS) 
const char* password = "eqdf2376"; // THIS TOO!
// const char* serverIP = "172.20.10.10"; 
// const int serverPort = 4242;

WiFiClient client;

// Sensor Changeables:
#define SENSOR_MINOR_ID 2
uint32_t colour = WS2812B.Color(255, 0, 0); // Colour of our sensor (change for each luggage sensor pair)
#define PICO_TYPE 2; // Determines whether the sensor is luggage or a user. (2 = luggage, 3 = user)

void advertisementCallback(BLEAdvertisement *adv) {
  if (adv->isIBeacon()) {
    int majorID = adv->getIBeaconMajorID();
    int rssi = adv->getRssi();

    display.clearDisplay();
    display.setTextSize(1);     
    display.setTextColor(WHITE);
    display.setCursor(0, 0);
    display.println("Received BLE Signal.");
    display.println("RSSI: " + String(rssi));
    display.println("Room ID: " + String(majorID));
    display.display(); 

    if (rssi > strongestRSSI) {
      strongestRSSI = rssi;
      strongestMajorID = majorID;
    }
  }
}

void onMQTTDisconnect(AsyncMqttClientDisconnectReason reason)
{
  (void) reason;

  connectedToMQTT = false;

  Serial.println("Disconnected from MQTT.");
}

void onMQTTConnect(bool sessionPresent) {
  connectedToMQTT = true;
  
  Serial.println("Connected to MQTT.");
}

void onMQTTMessage(char* topic, char* payload, const AsyncMqttClientMessageProperties& properties, const size_t& len, const size_t& index, const size_t& total) {
  return;
}

void onMqttPublish(const uint16_t& packetId)
{
  Serial.println("Publish acknowledged.");
  Serial.print("  packetId: ");
  Serial.println(packetId);
}


void setup(void) {
  Wire.begin();
  Serial.begin(115200);


  // Initialise the OLED display:
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("SSD1306 allocation failed");
    for (;;);
  }

  // Update display:
  display.clearDisplay();
  display.setTextSize(1);     
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("Beginning Setup");
  display.println("Setting up bluetooth...");
  display.display(); 

  // Initialize Bluetooth
  BTstack.setup();
  BTstack.setBLEAdvertisementCallback(advertisementCallback);

  // Colour System:
  WS2812B.begin(); // initializes WS2812B strip object (REQUIRED)
  WS2812B.setPixelColor(1, colour);
  WS2812B.show();


  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Setting Up");
  display.printf("Connecting to WiFi ssid: %s...", ssid);
  display.display(); 

  // Connect to Wi-Fi:
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000); // Not sure if this is needed to be honest...
  }


  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCredentials(MQTT_TOKEN);

  mqttClient.onConnect(onMQTTConnect);
  mqttClient.onDisconnect(onMQTTDisconnect);
  mqttClient.onPublish(onMqttPublish);

  mqttClient.connect();

  // Update display:
  display.clearDisplay();
  display.setTextSize(1);     
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("Setup complete.");
  display.println("Waiting to start scanning..");
  display.println("Room ID: " + String(oldMajorID));
  display.display(); 
}

void sendToServer(int majorID) {
    // Update display:
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Status: Communicating.");
    display.println("Sending to Server...");
    display.println("Room ID: " + String(majorID));
    display.display(); 

    // Create JSON document to send to server:
    StaticJsonDocument<256> json;

    json["PicoID"] = SENSOR_MINOR_ID;
    json["RoomID"] = majorID;
    json["PicoType"] = PICO_TYPE;
    json["Data"] = majorID;

    String jsonString;
    serializeJson(json, jsonString);

    String macAddress = WiFi.macAddress();
    macAddress.replace(":", "");
    String topic = "feeds/hardware-data/" + macAddress;
    //WiFi.macAddress();
    Serial.printf("Publishing message in topic '%s': %s\n", topic.c_str(), jsonString.c_str());

    if (!connectedToMQTT) {
      mqttClient.connect();
    }
    if (connectedToMQTT) {
      mqttClient.publish(topic.c_str(), 2, true, jsonString.c_str());
    }
}

void loop(void) {
  unsigned long currentTime = millis();

  // Start scanning if not currently scanning and the wait period has elapsed:
  if (!isScanning && (currentTime - lastActionTime >= WAIT_DURATION)) {
    BTstack.bleStartScanning();

    // Reset the strongest signal tracking variables:
    strongestRSSI = -10000;

    isScanning = true;
    lastActionTime = currentTime;

    // Update display:
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Status: Scanning!");
    display.println("Scanning for BLE signal!");
    display.println("Room ID: " + String(oldMajorID));
    display.display(); 
  }

  // Stop scanning after the scan duration:
  if (isScanning && (currentTime - lastActionTime >= SCAN_DURATION)) {
    Serial.println("Stopping scan...");
    BTstack.bleStopScanning();

    isScanning = false;
    lastActionTime = currentTime;

    // Update display:
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Status: Idle.");
    display.println("Waiting to scan..");
    display.println("Room ID: " + String(oldMajorID));
    display.display(); 

    // After scanning, process the strongest signal:
    if (strongestMajorID != -1 && strongestRSSI != -1) {
      // Update MajorID:
      oldMajorID = strongestMajorID;

      // Send the new MajorID to the server:
      sendToServer(strongestMajorID);
    }
  }
  BTstack.loop();
}
