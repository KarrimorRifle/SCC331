#include <Arduino.h>
#include <WiFi.h> 
#include <Adafruit_SSD1306.h>
#include <BTstackLib.h>
#include <Adafruit_NeoPixel.h>
#include "MqttConnection.hpp"
#include "RoomSensor.hpp"
#include "BluetoothSensor.hpp"


int picoType = LUGGAGE_PICO; // The Type of methods this Pico will be utilising 


// WiFi Stuff:
const char* ssid = "grp3"; // CHANGE THIS FOR DIFFERENT NETWORKS (FIND ON ROUTERS) 
const char* password = "eqdf2376"; // THIS TOO!
WiFiClient client;
MqttConnection mqtt = MqttConnection();


// Display Stuff:
Adafruit_NeoPixel led(3, 6, NEO_GRB + NEO_KHZ800); // LEDs
#define SCREEN_WIDTH 128 // Screen
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);


SensorType *currentSensorConfig;
RoomSensor roomSensorConfig = RoomSensor(&display, &mqtt);
BluetoothSensor bluetoothSensorConfig = BluetoothSensor(&display, &mqtt, &led);


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
	while (WiFi.status() != WL_CONNECTED) {
		delay(1000); // Not sure if this is needed to be honest...
	}
}


void setupMQTT() {
	// MQTT Setup:	
	display.clearDisplay();
	display.setCursor(0, 0);
	display.println("Connected.");
	display.println("Connecting to mqtt broker...");
	display.display(); 
  	mqtt.connectToBroker();
}


void getInitialSensorType() {
	// Update display:
	display.clearDisplay();
	display.setCursor(0, 0);
	display.println("Initial Setup complete.");
	display.println("Waiting for PicoType from Server");
	display.display(); 
	
	// TODO WAIT FOR REMOTE SETUP FROM SERVER
}


void setSensorType(bool initialSet = false) {
	if (!initialSet) {
		currentSensorConfig->unsetup();
	}

	switch (picoType)
	{
		case SERVER_PICO: // Server
			break;
		
		case ROOM_PICO: // Room
			currentSensorConfig = &roomSensorConfig;
			currentSensorConfig->setup();
			break;
			
		case LUGGAGE_PICO: // Luggage
			bluetoothSensorConfig.setSensorType(picoType);
			currentSensorConfig = &bluetoothSensorConfig;
			currentSensorConfig->setup();
			break;
			
		case PASSENGER_PICO: // Passenger
			bluetoothSensorConfig.setSensorType(picoType);
			currentSensorConfig = &bluetoothSensorConfig;
			currentSensorConfig->setup();
			break;
		
		case STAFF_PICO: // Staff
			bluetoothSensorConfig.setSensorType(picoType);
			currentSensorConfig = &bluetoothSensorConfig;
			currentSensorConfig->setup();
			break;
		
		case SECURITY_PICO: // Security Guard
			bluetoothSensorConfig.setSensorType(picoType);
			currentSensorConfig = &bluetoothSensorConfig;
			currentSensorConfig->setup();
			break;
		
		default:
			return;
			break;
	}
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
	setSensorType(true);
}


void loop(void)
{
	//Loop based on the picoType:
	currentSensorConfig->loop();
}