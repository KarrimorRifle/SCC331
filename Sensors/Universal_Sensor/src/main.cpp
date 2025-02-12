#include <Arduino.h>
#include <PDM.h>
#include <WiFi.h> 
#include <Adafruit_GFX.h>
#include "BH1745NUC.h"
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>
#include <BTstackLib.h>
#include <stdio.h>
#include <SPI.h>
#include "bsec.h"
#include <Adafruit_NeoPixel.h>
#include "MqttConnection.hpp"
#include "RoomSensor.hpp"


int minorID;          // The Pico's unique ID
int majorID = -1;     // The RoomID, defaulted to -1 for People Sensors
int picoType = ROOM_PICO;         // The Type of methods this Pico will be utilising 

uint32_t LEDColour;   // The colour of the LEDs for Passenger / Luggage pairing
UUID ROOM_UUID;		  // The unique Room UUID, for Room Sensors only



// WiFi Stuff:
const char* ssid = "grp3"; // CHANGE THIS FOR DIFFERENT NETWORKS (FIND ON ROUTERS) 
const char* password = "eqdf2376"; // THIS TOO!
WiFiClient client;
MqttConnection mqtt = MqttConnection();



// Display Stuff:
Adafruit_NeoPixel WS2812B(3, 6, NEO_GRB + NEO_KHZ800); // LEDs

#define SCREEN_WIDTH 128 // Screen
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
bool warningActive = false; 
String warningMessage = "";



// Variables to be used by different picoTypes:

// BLE Scanning Variables:
int strongestMajorID = -1;
int strongestRSSI = -10000;
#define SCAN_DURATION 9500
#define WAIT_DURATION 500
unsigned long lastActionTime = 0;
bool isScanning = false;
int oldMajorID = -1; // The room the user / luggage is currently in, according to the majorID picked up


// Pico Configurables:
#define SERVER_PICO 0
#define ROOM_PICO 1
#define LUGGAGE_PICO 2
#define PASSENGER_PICO 3
#define STAFF_PICO 4
#define SECURITY_PICO 5

SensorType *currentSensorConfig;
RoomSensor roomSensorConfig = RoomSensor(&display, &mqtt);


// Bluetooth Receiver Methods:
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
	  majorID = majorID;
	}
  }
}


// Send To Server Method:
void sendToServer(String data)
{
	// Update display:
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Status: Communicating.");
    display.println("Sending to Server...");
    display.println("Room ID: " + String(majorID));
    display.display(); 

    // Create JSON document to send to server:
    StaticJsonDocument<256> json;

    json["PicoID"] = minorID;
    json["RoomID"] = majorID;
    json["PicoType"] = picoType;
    json["Data"] = data;

    String jsonString;
    serializeJson(json, jsonString);

	mqtt.publishDataWithIdentifier(jsonString, "feeds/hardware-data/");
}



// Setup Methods:
void passengerAndLuggageSetup()
{
  // Colour System:
  WS2812B.begin(); // initializes WS2812B strip object (REQUIRED)
  WS2812B.setPixelColor(1, 4294967295);
  WS2812B.show();
}



void setup(void) 
{
	// Start by setting up universal required setup:
	Wire.begin();
  	Serial.begin(115200);

	// Initialise the OLED display:
	if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
		Serial.println("SSD1306 allocation failed");
	}

	// Update display:
	display.clearDisplay();
	display.setTextSize(1);     
	display.setTextColor(WHITE);
	display.setCursor(0, 0);
	display.println("Setting up...");
	display.printf("Connecting to router %s", ssid);
	display.display(); 

	// Connect to Wi-Fi:
	WiFi.begin(ssid, password);
	while (WiFi.status() != WL_CONNECTED) {
		delay(1000); // Not sure if this is needed to be honest...
	}

	// MQTT Setup:	
	display.clearDisplay();
	display.setCursor(0, 0);
	display.println("Connected.");
	display.println("Connecting to mqtt broker...");
	display.display(); 
  	mqtt.connectToBroker();
	
	// Bluetooth Setup:
  	BTstack.setup();
	
	// Update display:
	display.clearDisplay();
	display.setCursor(0, 0);
	display.println("Initial Setup complete.");
	display.println("Waiting for PicoType from Server");
	display.display(); 
	
	
	// TODO WAIT FOR REMOTE SETUP FROM SERVER
	
	/* Now, setup based on the picoType:
	 * 0 = Server
	 * 1 = Room
	 * 2 = Luggage
	 * 3 = Passenger
	 * 4 = Staff
	 * 5 = Security Guard
	*/

	switch (picoType)
	{
	case 0: // Server
		break;
	
	case ROOM_PICO: // Room
		currentSensorConfig = &roomSensorConfig;
		currentSensorConfig->setup();
		break;
		
	case 2: // Luggage
  		BTstack.setBLEAdvertisementCallback(advertisementCallback);
		passengerAndLuggageSetup();
		break;
		
	case 3: // Passenger
  		BTstack.setBLEAdvertisementCallback(advertisementCallback);
		passengerAndLuggageSetup();
		break;
	 
	case 4: // Staff
  		BTstack.setBLEAdvertisementCallback(advertisementCallback);
	
		break;
	
	case 5: // Security Guard
  		BTstack.setBLEAdvertisementCallback(advertisementCallback);
	
		break;
	
	default:
		return;
		break;
	}
}



// Looping Methods:
void bluetoothReceiverLoop() {
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
	display.println("Room ID: " + String(majorID));
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
	  majorID = strongestMajorID;

	  // Send the new MajorID to the server:
	  sendToServer(String(strongestMajorID));
	}
  }
  BTstack.loop();
}



void loop(void)
{
	/* Loop based on the picoType:
	 * 0 = Server
	 * 1 = Room
	 * 2 = Luggage
	 * 3 = Passenger
	 * 4 = Staff
	 * 5 = Security Guard
	*/

switch (picoType)
	{
	case 0: // Server
		break;
	
	case ROOM_PICO: // Room
		currentSensorConfig->loop();
		break;
		
	case 2: // Luggage
		bluetoothReceiverLoop();
		break;
		
	case 3: // Passenger
		bluetoothReceiverLoop();
		break;
	 
	case 4: // Staff
		bluetoothReceiverLoop();
		break;
	
	case 5: // Security Guard
		bluetoothReceiverLoop();
		break;
	
	default:
		break;
	}
}