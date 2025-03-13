#include <Arduino.h>
#include <WiFi.h> 
#include <Adafruit_SSD1306.h>
#include <BTstackLib.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include "MqttConnection.hpp"
#include "RoomSensor.hpp"
#include "BluetoothSensor.hpp"
#include "UnassignedSensor.hpp"


uint16_t bluetoothID = 0;
String readableID = "";

// WiFi Stuff:
const char* ssid = "grp3"; // CHANGE THIS FOR DIFFERENT NETWORKS (FIND ON ROUTERS) 
const char* password = "eqdf2376"; // THIS TOO!
WiFiClient client;
MqttConnection mqtt = MqttConnection();
MqttSubscription configSubscription;


// Display Stuff:
Adafruit_NeoPixel led(3, 6, NEO_GRB + NEO_KHZ800); // LEDs
#define SCREEN_WIDTH 128 // Screen
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

UnassignedSensor configUnassigned = UnassignedSensor();
SensorType *currentSensorConfig = &configUnassigned;
RoomSensor roomSensorConfig = RoomSensor(&display, &mqtt, bluetoothID, &readableID);
BluetoothSensor bluetoothSensorConfig = BluetoothSensor(&display, &mqtt, &led, "", &readableID);


void setupDisplay() {
	// Initialise the OLED display:
	if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
		Serial.println("SSD1306 allocation failed");
	}
	// clear the display to not show garbled data
	display.clearDisplay();
	display.display();
}


void setupWIFI() {
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
	if (WiFi.waitForConnectResult(15000) != WL_CONNECTED) {
		display.clearDisplay();
		display.setTextSize(1);     
		display.setTextColor(WHITE);
		display.setCursor(0, 0);
		display.println("Connection Failed");
		display.printf("To router %s", ssid);
		display.println("");
		display.println("Please Reset Device");
		display.display(); 
		exit(-1);
	}

	display.clearDisplay();
	display.display();
}


void setupMQTT() {
	// MQTT Setup:	
	display.clearDisplay();
	display.setCursor(0, 0);
	display.println("Connected.");
	display.println("Connecting to mqtt broker...");
	display.display(); 

  	mqtt.connectToBroker();

	display.clearDisplay();
	display.display();
}


void handleConfigMessage(String message) {
	Serial.print("Message Recieved:");
	Serial.println(message);
	String hardwareID = mqtt.getHardwareIdentifier();

	StaticJsonDocument<1000> doc;

	DeserializationError error = deserializeJson(doc, message);
  
	if (error) {
		display.clearDisplay();
		display.setCursor(0, 0);
		display.println("Waiting for PicoType from Server");
		display.println("Invalid Message Recieved.");
		display.println("Hardware ID: " + hardwareID);
		display.display(); 
		return;
	}

	if (doc.containsKey("PicoType")) {
		int recievedPicoType = doc["PicoType"].as<int>();
		Serial.print("Recieved Pico Type: ");
		Serial.println(recievedPicoType);
		if (recievedPicoType == UNASSIGNED_PICO) {
			currentSensorConfig->unsetup();
			currentSensorConfig = &configUnassigned;
			display.clearDisplay();
			display.setCursor(0, 0);
			display.println("Message recieved.");
			display.println("Currently unassigned, awaiting assignment.");
			display.println("Hardware ID: " + hardwareID);
			display.display(); 
		}

		else if (currentSensorConfig->getSensorType() != recievedPicoType) {
			currentSensorConfig->unsetup();
			switch (recievedPicoType) {
				case ROOM_PICO:
					currentSensorConfig = &roomSensorConfig;
					break;
				case TRACKER_PICO:
					currentSensorConfig = &bluetoothSensorConfig;
					break;
				default:
					currentSensorConfig = &configUnassigned;
					display.clearDisplay();
					display.setCursor(0, 0);
					display.println("Message recieved.");
					display.println("Currently unassigned, awaiting assignment.");
					display.println("Hardware ID: " + hardwareID);
					display.display(); 
					break;
			}
			currentSensorConfig->setup();
		}
	}
  
	if (doc.containsKey("ReadableID")) {
		  readableID = doc["ReadableID"].as<String>();
	}

	if (doc.containsKey("BluetoothID")) {
		bluetoothID = doc["BluetoothID"].as<uint16_t>();
		
		roomSensorConfig.setBluetoothID(bluetoothID);
	}

	if (doc.containsKey("TrackerGroup")) {
		String bluetoothTrackerGroup = doc["TrackerGroup"].as<String>();
		bluetoothSensorConfig.setCurrentTrackerGroup(bluetoothTrackerGroup);
	}
}


void getInitialSensorType() {
	currentSensorConfig = &configUnassigned;
	String hardwareID = mqtt.getHardwareIdentifier();

	// Update display:
	display.clearDisplay();
	display.setCursor(0, 0);
	display.println("Initial Setup complete.");
	display.println("Waiting for PicoType from Server");
	display.println("Hardware ID: " + hardwareID);
	display.println("Device Name: " + readableID );
	display.display(); 
	
	configSubscription = MqttSubscription("hardware_config/server_message/" + hardwareID);
	mqtt.addSubscription(&configSubscription);
	Serial.print("Added subscription to ");
	Serial.println(configSubscription.getSubscriptionRoute());

	mqtt.publishToMQTT("{\"PicoID\": \"" + hardwareID + "\"}", "hardware_config/hardware_message/" + hardwareID);

	bool sensorTypeNotFound = true;
	uint32_t last_keep_alive = millis();
	while(sensorTypeNotFound) {
		if (last_keep_alive + 30000 < millis()) {
			mqtt.publishToMQTT("{\"PicoID\": \"" + hardwareID + "\"}", "hardware_config/hardware_message/" + hardwareID);
			last_keep_alive = millis();
		}
		
		if (configSubscription.hasMessage()) {
			handleConfigMessage(configSubscription.getMessage());
			if (currentSensorConfig->getSensorType() != UNASSIGNED_PICO) {
				sensorTypeNotFound = false;
			}
		}
	}

	display.clearDisplay();
	display.display();
}


void setup(void) 
{
	// Start by setting up universal required setup:
	Wire.begin();
  	Serial.begin(115200);

	setupDisplay();
	setupWIFI();

	setupMQTT();

	// Bluetooth Setup:
  	BTstack.setup();

	// Now, setup based on the picoType:
	getInitialSensorType();
}


void loop(void)
{
	//Loop based on the picoType:
	currentSensorConfig->loop();
	if (configSubscription.hasMessage()) {
		handleConfigMessage(configSubscription.getMessage());
	}
}