#include <BTstackLib.h>
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

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

// Colour definitions:
#define RED_PIN 2
#define GREEN_PIN 3
#define BLUE_PIN 4
// Change these per sensor:
#define RED_BRIGHTNESS 255
#define GREEN_BRIGHTNESS 0
#define BLUE_BRIGHTNESS 0

//-- defines OLED screen dimensions ---
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET    -1 // Reset pin # 
#define SCREEN_ADDRESS 0x3C // OLED I2C address

//creates OLED display object "display"
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define SCAN_DURATION 3000
#define WAIT_DURATION 20000

unsigned long lastActionTime = 0;
bool isScanning = false;

int oldMajorID = -1; // The room the user / luggage is currently in, according to the majorID picked up

int minorID = 1; // Unique integer identifier for this sensor; change for each sensor.
bool isLuggage = false; // Determines whether the sensor is luggage or a user.

int strongestMajorID = -1;
int strongestRSSI = -1;

void advertisementCallback(BLEAdvertisement *adv) {
  if (adv->isIBeacon()) {
    int majorID = adv->getIBeaconMajorID();
    int rssi = adv->getRssi();

    if (rssi > strongestRSSI) {
      strongestRSSI = rssi;
      strongestMajorID = majorID;
    }
  }
}

void setup(void) {
  Serial.begin(115200);

  BTstack.setup();
  BTstack.setBLEAdvertisementCallback(advertisementCallback);

  // Initialise the OLED display:
  if (!display.begin(SSD1306_I2C_ADDRESS, SCREEN_ADDRESS)) {
    Serial.println("SSD1306 allocation failed");
    for (;;);
  }
  // Update display:
  display.clearDisplay();
  display.setTextSize(1);     
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("Setup complete.");
  display.println("Waiting to start scanning..");
  display.println("Room ID: " + oldMajorID);
  display.display(); 

  // Colour System:
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  analogWrite(RED_PIN, RED_BRIGHTNESS);
  analogWrite(GREEN_PIN, GREEN_BRIGHTNESS);
  analogWrite(BLUE_PIN, BLUE_BRIGHTNESS);
}

void loop(void) {
  unsigned long currentTime = millis();

  // Start scanning if not currently scanning and the wait period has elapsed:
  if (!isScanning && (currentTime - lastActionTime >= WAIT_DURATION)) {
    Serial.println("Starting scan...");
    BTstack.startBLEScanning();

    // Reset the strongest signal tracking variables:
    strongestMajorID = -1;
    strongestRSSI = -1;

    isScanning = true;
    lastActionTime = currentTime;

    // Update display:
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Status: Scanning!");
    display.println("Scanning for BLE signal!");
    display.println("Room ID: " + oldMajorID);
    display.display(); 
  }

  // Stop scanning after the scan duration:
  if (isScanning && (currentTime - lastActionTime >= SCAN_DURATION)) {
    Serial.println("Stopping scan...");
    BTstack.stopBLEScanning();

    // After scanning, process the strongest signal:
    if (strongestMajorID != -1 && strongestRSSI != -1) {
      // Update MajorID:
      if (oldMajorID != strongestMajorID) {
        oldMajorID = strongestMajorID;
        // TODO: Send the new MajorID to the server (if needed)
      }
    }
    isScanning = false;
    lastActionTime = currentTime;

    // Update display:
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Status: Idle.");
    display.println("Waiting to scan..");
    display.println("Room ID: " + oldMajorID);
    display.display(); 
  }
  BTstack.loop();
}
