#include <Arduino.h>
#include <PDM.h>
#include <WiFi.h> 
#include <Adafruit_GFX.h>
#include "bme68xLibrary.h"
#include "BH1745NUC.h"
#include "AsyncMqtt_Generic.h"
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>
#include <BTstackLib.h>
#include <stdio.h>
#include <SPI.h>
#include "./env.cpp"

/*
 * BLE Broadcast periodically (Every 20 seconds)
 * Monitor Environment Data
 * Send details to server
*/

//-- Defines OLED screen dimensions ---
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET    -1 // Reset pin # 
#define SCREEN_ADDRESS 0x3C // OLED I2C address

// Creates OLED display object "display"
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Environment Sensor Stuff: 
Bme68x bme; // Climate
short sampleBuffer[512]; // Sound
volatile int samplesRead;
#define BH1745NUC_DEVICE_ADDRESS_38 0x38 // Light
BH1745NUC bh1745nuc = BH1745NUC();

// Location Sensor Timings:
#define ADVERTISEMENT_DURATION 30000
#define WAIT_DURATION 5000
unsigned long lastActionTime = 0;
bool isAdvertising = false;

// Sensor Changeables: 
#define ROOM_MAJOR_ID 1
#define SENSOR_MINOR_ID 1
#define PICO_TYPE 1
UUID ROOM_UUID = "12345678";

// WiFi Stuff:
const char* ssid = "grp3"; // CHANGE THIS FOR DIFFERENT NETWORKS (FIND ON ROUTERS) 
const char* password = "eqdf2376"; // THIS TOO!
// const char* serverIP = "185.213.2.0"; 
// const int serverPort = 4242;

WiFiClient client;

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

void sendToServer(String dataField);
void onPDMdata();
float calculateDecibels();
float readSoundSamples();

void setup(void) {
  Wire.begin();
  Serial.begin(115200);

  // Initialise Climate Sensors:
  bme.begin(0x76, Wire);
  if (bme.checkStatus()){
    if (bme.checkStatus() == BME68X_ERROR){
        Serial.println("Sensor error:" + bme.statusString());
      return;
      }
    else if (bme.checkStatus() == BME68X_WARNING){
      Serial.println("Sensor Warning:" + bme.statusString());
    }
  }
  bme.setTPH();

  // More Environmental Initialising:
  uint16_t temperatureProfile[10] = {100, 200, 320};
  uint16_t durationProfile[10] = {150, 150, 150};

  bme.setSeqSleep(BME68X_ODR_250_MS);
  bme.setHeaterProf(temperatureProfile, durationProfile, 3);
  bme.setOpMode(BME68X_SEQUENTIAL_MODE);

  // Light: 
  bh1745nuc.begin(BH1745NUC_DEVICE_ADDRESS_38);
  bh1745nuc.startMeasurement();

  // Noise:
  PDM.onReceive(onPDMdata);
  PDM.setCLK(3);
  PDM.setDIN(2);
  if(!PDM.begin(1, 16000)){
    display.clearDisplay();
    display.setCursor(0,0);
    display.write("Failed to start PDM");
    display.display();
    while(1);
  }

  // Initialise Bluetooth Stuff:
  BTstack.setup();
  BTstack.iBeaconConfigure(&ROOM_UUID, ROOM_MAJOR_ID, SENSOR_MINOR_ID);

  // Initialise the OLED display:
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("SSD1306 allocation failed");
    for (;;);
  }

  // Connect to Wi-Fi:
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(10); // Not sure if this is needed to be honest...
  }

  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCredentials(MQTT_TOKEN);

  mqttClient.onConnect(onMQTTConnect);
  mqttClient.onDisconnect(onMQTTDisconnect);

  mqttClient.connect();

  // Update display:
  display.clearDisplay();
  display.setTextSize(1);     
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("Setup complete.");
  display.println("Waiting to broadcast...");
  display.display(); 

  BTstack.startAdvertising();
}

// Big function to get all of the Environment Data and then send it to the server:
void environmentalData(){
  // Update display:
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Status: Getting Environment Data!");
  display.display(); 

  // Get the data:
  bme68xData data;
  bme.fetchData();
  while(bme.getData(data));
  bh1745nuc.read();

  // Process the data:
  float sound = readSoundSamples();
  String temperature =  String(data.temperature-4.49);
  String light = String(bh1745nuc.clear);

  // Send data to server via helpermethod:
  String dataLine = String(light) + "," + String(sound) + "," + String(temperature);
  sendToServer(dataLine);     
}

float readSoundSamples(){
  if (samplesRead > 0) {
    float decibels = calculateDecibels();
    samplesRead = 0; // Reset the sample count after processing
    return decibels;
  }
  return -1; 
}

float calculateDecibels(){
  float sum = 0;
  for (int i = 0; i < samplesRead; i++) {
    sum += abs(sampleBuffer[i]);
  }
  float average = sum / samplesRead;
  return -20.0f * log10(average / 32767.0f); // Convert average value to decibels
}

void onPDMdata() {
  int bytesAvailable = PDM.available();
  PDM.read(sampleBuffer, bytesAvailable);
  // 16-bit, 2 bytes per sample
  samplesRead = bytesAvailable / 2;
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


void sendToServer(String dataField) {
    // Update display:
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Status: Communicating.");
    display.println("Sending to Server...");
    display.println("Room ID: " + String(ROOM_MAJOR_ID));
    display.display(); 

    // Create JSON document to send to server:
    StaticJsonDocument<256> json;

    json["PicoID"] = SENSOR_MINOR_ID;
    json["RoomID"] = ROOM_MAJOR_ID;
    json["PicoType"] = PICO_TYPE;
    json["Data"] = dataField;

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

  if (currentTime - lastActionTime >= WAIT_DURATION) {
    lastActionTime = currentTime;
    environmentalData();
  }

  BTstack.loop();
}
