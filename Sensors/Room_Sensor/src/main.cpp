#include <BTstackLib.h>
#include <Arduino.h>

/*
 * BLE Broadcast periodically (Every 20 seconds)
 * Monitor Temperature
 * Send details to server if needed
*/

const char *ROOM_UUID = "12345678-1234-5678-1234-567812345678";
#define ROOM_MAJOR_ID 1

#define ADVERTISEMENT_DURATION 1000
#define SLEEP_DURATION 20000

unsigned long lastActionTime = 0;
bool isAdvertising = false;

void setup(void) {
  Serial.begin(115200);

  BTstack.setup();

  // Prepare iBeacon advertisement:
  BLEAdvertisement adv = BTstack.getBLEAdvertisement();
  adv.setIBeacon(ROOM_UUID, ROOM_MAJOR_ID, 0, -59); // UUID, MajorID, MinorID, Measured Power

  Serial.println("Setup complete. Waiting to broadcast.");
}

void loop(void) {
  unsigned long currentTime = millis();

  // If not advertising and it's time to start broadcasting:
  if (!isAdvertising && (currentTime - lastActionTime >= SLEEP_DURATION)) {
    BTstack.startBLEAdvertising();

    isAdvertising = true;
    lastActionTime = currentTime; // Reset the timer
  }

  // If advertising and it's time to stop:
  if (isAdvertising && (currentTime - lastActionTime >= ADVERTISEMENT_DURATION)) {
    BTstack.stopBLEAdvertising();

    isAdvertising = false;
    lastActionTime = currentTime; // Reset the timer
  }

  BTstack.loop();
}
