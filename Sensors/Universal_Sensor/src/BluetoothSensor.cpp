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
  // specificWarningSubscription = MqttSubscription();
  // globalWarningSubscription = MqttSubscription();
  flash_get_unique_id(&minorID);
}


void BluetoothSensor::setWarningSubscriptions() {
  String specificWarningRoute;
  switch (picoType) {
    case SECURITY_PICO:
      specificWarningRoute = "warning/security/#";
      break;

    case STAFF_PICO:
      specificWarningRoute = "warning/staff/#";
      break;

    case PASSENGER_PICO:
      specificWarningRoute = "warning/users/#";
      break;

    default:
      specificWarningRoute = "";
  }


  warningSubscription = MqttSubscription(specificWarningRoute);
  globalWarningSubscription = MqttSubscription("warning/everyone/#");


  mqtt->addSubscription(&warningSubscription);
  mqtt->addSubscription(&globalWarningSubscription);
}


void BluetoothSensor::unsetWarningSubscriptions() {
  mqtt->removeSubscription(&warningSubscription);
  mqtt->removeSubscription(&globalWarningSubscription);
}


void BluetoothSensor::ledSetup() {
  // Colour System:
  leds->begin(); // initializes WS2812B strip object (REQUIRED)
  leds->setPixelColor(1, leds->Color(100, 100, 100));
  leds->setBrightness(100);     //just to make the brightness more bearable, feel free to adjust
  leds->show();
}


void BluetoothSensor::setup() {
  BTstack.setBLEAdvertisementCallback(this->advertisementCallback);

  this->ledSetup();

  this->setWarningSubscriptions();

  pinMode(BUZZER, OUTPUT);
  pinMode(BLACK_BUTTON, INPUT);
  pinMode(RED_BUTTON, INPUT);
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
  }

  // Stop scanning after the scan duration:
  if (isScanning && (currentTime - lastActionTime >= SCAN_DURATION)) {
    BTstack.bleStopScanning();

    isScanning = false;
    lastActionTime = currentTime;


    // After scanning, process the strongest signal:
    if (strongestMajorID != -1 && strongestRSSI != -1) {
      // Update MajorID:
      majorID = strongestMajorID;

      // Send the new MajorID to the server:
      sendToServer(String(strongestMajorID));
    }
  }

  if (globalWarningSubscription.hasMessage()) {
    handleWarning(globalWarningSubscription.getMessage(), "GLOBAL");
  }

  if (warningSubscription.hasMessage()) {
    String source;
    switch (picoType) {
      case SECURITY_PICO:
        source = "SECURITY";
        break;
  
      case STAFF_PICO:
        source = "STAFF";
        break;
  
      case PASSENGER_PICO:
        source = "PASSENGER";
        break;
  
      default:
        source = "";
    }

    handleWarning(warningSubscription.getMessage(), source);
  }

  if(warningLive){
    this->checkForAcknowledgement();
  }
  
  BTstack.loop();
}


void BluetoothSensor::unsetup() {
	BTstack.bleStopScanning();
  this->unsetWarningSubscriptions();
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


void BluetoothSensor::handleWarning(String message, String source) {
  warningLive = true;

  source.toUpperCase();
  String warningMessage = "";

  StaticJsonDocument<1000> doc;

  DeserializationError error = deserializeJson(doc, message);

  if (error) {
    Serial.print("Json Error in BluetoothSensor::handleWarning: ");
    Serial.println(error.c_str());
    warningLive = false;
    return;
  }


  String severity;
  if (doc.containsKey("Severity")) {
    severity = doc["Severity"].as<String>();
    severity.toUpperCase();
    warningMessage.concat((source + " " + severity).substring(0, 20) +  + " \n");
  }
  else {
    severity = "";
    warningMessage.concat(source + " WARNING \n");
  }

  if (doc.containsKey("Title")) {
    String title = doc["Title"];
    title = title.substring(0, 20);
    warningMessage.concat(title + " \n");
  }

  warningMessage.concat("\n");

  if (doc.containsKey("Location")) {
    String location = doc["Location"];
    location = location.substring(0, 20);
    warningMessage.concat("Area: " + location + " \n");
  }

  if (doc.containsKey("Summary")) {
    warningMessage.concat(String(doc["Summary"]) + " ");
  }
  
  Serial.println("------------------");
  Serial.println(warningMessage);
  Serial.println("------------------");


  display->clearDisplay();
  display->setCursor(0, 0);
  display->startscrollleft(0x00, 0x0F);
  display->println(warningMessage);
  display->display(); 

  if (severity.startsWith("DANGER")) {
    tone(BUZZER, 6000);
    leds->setPixelColor(2, leds->Color(255, 0, 0));
    leds->show();
  }
  else if (severity.startsWith("WARNING")) {
    tone(BUZZER, 4000, 3000);
    leds->setPixelColor(2, leds->Color(255, 64, 0));
    leds->show();
  }
  else {
    tone(BUZZER, 2000, 1000);
    leds->setPixelColor(2, leds->Color(0, 255, 0));
    leds->show();
  }
}


//for reply - staff/security??
  //buttons used to acknowledge y/n
void BluetoothSensor::checkForAcknowledgement() {
  if (digitalRead(RED_BUTTON) == HIGH) {
    warningLive = false;
    leds->clear();
    leds->setPixelColor(1, leds->Color(255, 255, 255));
    leds->show();
    
    noTone(BUZZER);

    display->clearDisplay();
    display->stopscroll();
    display->setCursor(0, 0);
    display->println("Acknowledgement:");
    display->println("Understood");
    display->display();

    delay(2000);

    display->clearDisplay();
    display->setCursor(0, 0);
    display->display();
  }
}


//for ends the warning - users
void BluetoothSensor::warningOver() {
  warningLive = false;
  leds->clear();
  leds->setPixelColor(1, 4294967295);
  leds->show();
  
  noTone(BUZZER);

  display->clearDisplay();
  display->setCursor(0, 0);
  display->println("Thank you for your attention, the situation has been resolved");
  display->display(); 

  delay(1500);

  display->clearDisplay();
  display->setCursor(0, 0);
  display->display(); 
}


void BluetoothSensor::sendToServer(String data) {
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
