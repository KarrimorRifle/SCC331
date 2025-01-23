#include <BTstackLib.h>
#include <Arduino.h>

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

  Serial.println("Waiting to start scanning...");

  // TODO setup colour system
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
  }
  BTstack.loop();
}
