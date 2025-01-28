#include <BTstackLib.h>
#include <stdio.h>
#include <SPI.h>
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h> 

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

#define ADVERTISEMENT_DURATION 30000
#define WAIT_DURATION 30000

unsigned long lastActionTime = 0;
bool isAdvertising = false;

// WiFi Stuff:
const char* ssid = "iPhone (204)"; // CHANGE THIS FOR DIFFERENT NETWORKS (FIND ON ROUTERS) 
const char* password = "dobberz68"; // THIS TOO!
const char* serverIP = "172.20.10.10"; 
const int serverPort = 4242;

WiFiClient client;

// Sensor Changeables: 
#define ROOM_MAJOR_ID 1
#define SENSOR_MINOR_ID 1
UUID ROOM_UUID = "12345678-1234-5678-1234-567812345678";

void setup(void) {
  Serial.begin(115200);

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
    delay(1000); // Not sure if this is needed to be honest...
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

void sendToServer(int temperature) {
    // Update display:
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Status: Communicating.");
    display.println("Sending to Server...");
    display.println("Temperature: " + String(temperature));
    display.display(); 

  if (client.connect(serverIP, serverPort)) {
    String message = "The temperature is: " + String(temperature);
    client.println(message);
    client.stop();
  }
}

void loop(void) {
  unsigned long currentTime = millis();

  // If not advertising and it's time to start broadcasting:
  if (!isAdvertising && (currentTime - lastActionTime >= WAIT_DURATION)) {
    BTstack.startAdvertising();

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
    BTstack.stopAdvertising();

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
