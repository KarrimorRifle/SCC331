#include <BTstackLib.h>
#include <Arduino.h>

/*
 * Listen for BLE Broadcasts
 * Take details of first BLE Broadcast
 * Stop listening for BLE Broadcasts
 * Make BLE Broadcast with details received
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

void advertisementCallback(BLEAdvertisement *adv) {
  if (adv->isIBeacon()) {
    int majorID = adv->getIBeaconMajorID();

    // Stop scanning to prevent detecting other room sensors:
    BTstack.stopBLEScanning();
    isScanning = false;

    // TODO send majorID to the server (if needed):
    if (oldMajorID != majorID){
      oldMajorID = majorID;
      // TODO
    }
  }
}

void setup(void) {
  Serial.begin(115200);

  BTstack.setup();
  BTstack.setBLEAdvertisementCallback(advertisementCallback);

  Serial.println("Waiting to start scanning.")

  // TODO setup colour system
}

void loop(void) {
  unsigned long currentTime = millis();

  // Start scanning if not currently scanning and the wait period has elapsed:
  if (!isScanning && (currentTime - lastActionTime >= WAIT_DURATION)) {
    BTstack.startBLEScanning();

    isScanning = true;
    lastActionTime = currentTime; // Reset the timer
  }

  // Stop scanning after the scan duration:
  if (isScanning && (currentTime - lastActionTime >= SCAN_DURATION)) {
    BTstack.stopBLEScanning();

    isScanning = false;
    lastActionTime = currentTime; // Reset the timer
  }

  BTstack.loop();
}

