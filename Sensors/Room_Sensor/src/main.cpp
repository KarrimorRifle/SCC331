#include <BTstackLib.h>
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

/*
 * BLE Broadcast periodically (Every 20 seconds)
 * Monitor Temperature
 * Send details to server if needed
*/

//-- defines OLED screen dimensions ---
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET    -1 // Reset pin # 
#define SCREEN_ADDRESS 0x3C // OLED I2C address

//creates OLED display object "display"
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

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
  display.println("Waiting to broadcast...");
  display.display(); 
}

void loop(void) {
  unsigned long currentTime = millis();

  // If not advertising and it's time to start broadcasting:
  if (!isAdvertising && (currentTime - lastActionTime >= SLEEP_DURATION)) {
    BTstack.startBLEAdvertising();

    isAdvertising = true;
    lastActionTime = currentTime; // Reset the timer

    // Update display:
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Status: Broadcasting!");
    display.println("Advertising BLE signal!");
    display.display(); 
  }

  // If advertising and it's time to stop:
  if (isAdvertising && (currentTime - lastActionTime >= ADVERTISEMENT_DURATION)) {
    BTstack.stopBLEAdvertising();

    isAdvertising = false;
    lastActionTime = currentTime; // Reset the timer

    // Update display:
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Status: Idle.");
    display.println("Waiting to broadcast..");
    display.display();
  }

  BTstack.loop();
}
