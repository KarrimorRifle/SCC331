#include "BluetoothSensor.hpp"
#include <Arduino.h>
#include <PDM.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
extern "C" void flash_get_unique_id(uint8_t *p);


int BluetoothSensor::strongestRSSI = -10000;


BluetoothSensor::BluetoothSensor(Adafruit_SSD1306* Display, MqttConnection* Mqtt, Adafruit_NeoPixel* Leds) {
    display = Display;
    mqtt = Mqtt;
    leds = Leds;
    strongestMajorID = -1;
    strongestRSSI = -10000;
    lastActionTime = 0;
    isScanning = false;
    majorID = -1;
    picoType = 2;
    flash_get_unique_id(&minorID);
}


void BluetoothSensor::ledSetup() {
    // Colour System:
    leds->begin(); // initializes WS2812B strip object (REQUIRED)
    leds->setPixelColor(1, 4294967295);
    leds->setBrightness(200);     //just to make the brightness more bearable, feel free to adjust
    leds->show();
}


void BluetoothSensor::setup() {
    BTstack.setBLEAdvertisementCallback(this->advertisementCallback);
    pinMode(BUZZER, OUTPUT);
    this->ledSetup();
}


void BluetoothSensor::loop() {
  unsigned long currentTime = millis();

  // Start scanning if not currently scanning and the wait period has elapsed:
  if (!isScanning && (currentTime - lastActionTime >= WAIT_DURATION)) {
	BTstack.bleStartScanning();

	// Reset the strongest signal tracking variables:
	strongestRSSI = -10000;

	isScanning = true;
	lastActionTime = currentTime;

	// Update display:
	display->clearDisplay();
	display->setCursor(0, 0);
	display->println("Status: Scanning!");
	display->println("Scanning for BLE signal!");
	display->println("Room ID: " + String(majorID));
	display->display(); 
  }

  // Stop scanning after the scan duration:
  if (isScanning && (currentTime - lastActionTime >= SCAN_DURATION)) {
	Serial.println("Stopping scan...");
	BTstack.bleStopScanning();

	isScanning = false;
	lastActionTime = currentTime;

	// Update display:
	display->clearDisplay();
	display->setCursor(0, 0);
	display->println("Status: Idle.");
	display->println("Waiting to scan..");
	display->println("Room ID: " + String(majorID));
	display->display(); 

	// After scanning, process the strongest signal:
	if (strongestMajorID != -1 && strongestRSSI != -1) {
	  // Update MajorID:
	  majorID = strongestMajorID;

	  // Send the new MajorID to the server:
	  sendToServer(String(strongestMajorID));
	}
  }
  BTstack.loop();

  if(warningLive){
    warningRecieved(warningMessage);
  }
}


void BluetoothSensor::unsetup() {
    Serial.println("Stopping scan...");
	BTstack.bleStopScanning();
}


int BluetoothSensor::getSensorType() {
    return picoType;
}


void BluetoothSensor::setSensorType(int PicoType) {
    picoType = PicoType;
}


// Bluetooth Receiver Methods:
void BluetoothSensor::advertisementCallback(BLEAdvertisement *adv) {
  if (adv->isIBeacon()) {
	int majorID = adv->getIBeaconMajorID();
	int rssi = adv->getRssi();

	if (rssi > strongestRSSI) {
	  strongestRSSI = rssi;
	  majorID = majorID;
	}
  }
}


void BluetoothSensor::warningRecieved(String message) {
  warningLive = true;
  warningMessage = message;
  //standard
  leds->setPixelColor(2, leds->Color(255, 15, 15));
  leds->setPixelColor(3, leds->Color(255, 15, 15));
  leds->show();

  tone(BUZZER, 5000, 1500);

  display->clearDisplay();
  display->setCursor(0, 0);
  display->println("WARNING:");
  display->println(message);
  display->display(); 

  delay(2500);

  /*
  //Danger
  leds->setPixelColor(2, leds->Color(255, 15, 15));
  leds->setPixelColor(3, leds->Color(255, 15, 15));
  leds->show();

  tone(BUZZER, 5500, 1500);

  display->clearDisplay();
  display->setCursor(0, 0);
  display->println("DANGER:");
  display->println(message);
  display->display(); 

  delay(2500);

  //Doomed
  leds->setPixelColor(2, leds->Color(255, 15, 15));
  leds->setPixelColor(3, leds->Color(255, 15, 15));
  leds->show();

  tone(BUZZER, 6000, 1500);

  display->clearDisplay();
  display->setCursor(0, 0);
  display->println("DOOMED:");
  display->println(message);
  display->display(); 

  delay(2500);

  //Notification
  leds->setPixelColor(2, leds->Color(255, 15, 15));
  leds->setPixelColor(3, leds->Color(255, 15, 15));
  leds->show();

  tone(BUZZER, 5000, 1500);

  display->clearDisplay();
  display->setCursor(0, 0);
  display->println("NOTIFICATION:");
  display->println(message);
  display->display(); 

  delay(2500);
  */
}

//for reply - staff/security??
void BluetoothSensor::warningAcknowledged() {

}

void BluetoothSensor::warningOver() {
  warningLive = false;
  warningMessage = "";
  leds->clear();
  leds->setPixelColor(1, 4294967295);
  leds->show();
  
  noTone(BUZZER);

  display->clearDisplay();
  display->setCursor(0, 0);
  display->println("Thank you for your attention, the situation has been resolved");
  display->display(); 

  delay(1500);
}


void BluetoothSensor::sendToServer(String data) {
    	// Update display:
    display->clearDisplay();
    display->setCursor(0, 0);
    display->println("Status: Communicating.");
    display->println("Sending to Server...");
    display->println("Room ID: " + String(majorID));
    display->display(); 

    // Create JSON document to send to server:
    StaticJsonDocument<256> json;

    json["PicoID"] = mqtt->getHardwareIdentifier();
    json["RoomID"] = majorID;
    json["PicoType"] = picoType;
    json["Data"] = data;

    String jsonString;
    serializeJson(json, jsonString);

	mqtt->publishDataWithIdentifier(jsonString, "feeds/hardware-data/");
}
