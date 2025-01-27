#include <BTstackLib.h>
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_NeoPixel.h>
#include <WiFi.h> 
 

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


// For LED Stuff:
Adafruit_NeoPixel WS2812B(3, 6, NEO_GRB + NEO_KHZ800);

//-- defines OLED screen dimensions ---
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET    -1 // Reset pin #
#define SCREEN_ADDRESS 0x3C // OLED I2C address
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define SCAN_DURATION 15000
#define WAIT_DURATION 30000

unsigned long lastActionTime = 0;
bool isScanning = false;

int oldMajorID = -1; // The room the user / luggage is currently in, according to the majorID picked up

bool isLuggage = false; // Determines whether the sensor is luggage or a user.

int strongestMajorID = -1;
int strongestRSSI = -10000;

// WiFi Stuff:
const char* ssid = "iPhone (204)"; // CHANGE THIS FOR DIFFERENT NETWORKS (FIND ON ROUTERS) 
const char* password = "dobberz68"; // THIS TOO!
const char* serverIP = "172.20.10.10"; 
const int serverPort = 4242;

WiFiClient client;

// Sensor Changeables:
#define SENSOR_MINOR_ID 2
uint32_t colour = WS2812B.Color(255, 0, 0); // Colour of our sensor (change for each luggage sensor pair)

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

void setup(void) {
  Serial.begin(115200);

  // Initialize Bluetooth
  BTstack.setup();
  BTstack.setBLEAdvertisementCallback(advertisementCallback);

  // Initialise the OLED display:
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("SSD1306 allocation failed");
    for (;;);
  }

  // Colour System:
  WS2812B.begin(); // initializes WS2812B strip object (REQUIRED)
  WS2812B.setPixelColor(1, colour);
  WS2812B.show();

  // Connect to Wi-Fi:
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000); // Not sure if this is needed to be honest...
  }

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
    display.println("Room ID: " + String(oldMajorID));
    display.display(); 

  if (client.connect(serverIP, serverPort)) {
    String message = "The room ID is: " + String(majorID);
    client.println(message);
    client.stop();
  }
}

void loop(void) {
  unsigned long currentTime = millis();
  Serial.println("Reached loop");

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
      if (oldMajorID != strongestMajorID) {
        oldMajorID = strongestMajorID;

        // Send the new MajorID to the server:
        sendToServer(strongestMajorID);
      }
    }
  }
  BTstack.loop();
}
