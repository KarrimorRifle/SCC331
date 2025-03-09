#include "BluetoothSensor.hpp"
#include <Arduino.h>
#include <PDM.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
extern "C" void flash_get_unique_id(uint8_t *p);

int BluetoothSensor::strongestScanBluetoothID = -1;
int BluetoothSensor::strongestRSSI = -10000;


BluetoothSensor::BluetoothSensor(Adafruit_SSD1306* Display, MqttConnection* Mqtt, Adafruit_NeoPixel* Leds, uint16_t BluetoothID ) {
  display = Display;
  mqtt = Mqtt;
  leds = Leds;
  strongestScanBluetoothID = -1;
  strongestRSSI = -10000;
  lastActionTime = 0;
  isScanning = false;
  bluetoothID = BluetoothID;
  picoType = 2;
  warningSubscription = MqttSubscription();
  globalWarningSubscription = MqttSubscription();
}


void BluetoothSensor::setWarningSubscriptions() {
  String specificWarningRoute;
  switch (picoType) {
    case SECURITY_PICO:
      specificWarningRoute = "warnings/security/#";
      break;

    case STAFF_PICO:
      specificWarningRoute = "warnings/staff/#";
      break;

    case PASSENGER_PICO:
      specificWarningRoute = "warnings/users/#";
      break;

    default:
      specificWarningRoute = "";
  }


  warningSubscription = MqttSubscription(specificWarningRoute);
  globalWarningSubscription = MqttSubscription("warnings/everyone/#");


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
    if (strongestScanBluetoothID != -1 && strongestRSSI != -1) {
      // Send the new MajorID to the server:
      sendToServer(String(strongestScanBluetoothID));
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
  if (adv->isIBeacon()) 
  {
    int majorID = adv->getIBeaconMajorID();
    int rssi = adv->getRssi();

    if (rssi > strongestRSSI) {
      strongestRSSI = rssi;
      strongestScanBluetoothID = majorID;
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
  if (digitalRead(RED_BUTTON) == HIGH && warningLive) { //added the use of warningLive boolean to free up red button, will remove if buggy
    warningLive = false;
    leds->clear();
    leds->setPixelColor(1, leds->Color(255, 255, 255));
    leds->show();
    
    noTone(BUZZER);

    display->clearDisplay();
    display->setCursor(0, 0);
    display->println("Acknowledgement:");
    display->println("Understood");
    display->display();

    StaticJsonDocument<256> json;
    json["PicoID"] = mqtt->getHardwareIdentifier();
    json["RoomID"] = String(strongestScanBluetoothID);
    json["PicoType"] = picoType;
    json["Response"] = "I acknowledge and will take the appropriate actions";

    String jsonString;
    serializeJson(json, jsonString);

    mqtt->publishDataWithIdentifier(jsonString, "warnings/admin");

    delay(2000);

    display->clearDisplay();
    display->setCursor(0, 0);
    display->display();
  }
  else if (digitalRead(BLACK_BUTTON) == HIGH && warningLive) { //added the use of warningLive boolean to free up red button, will remove if buggy
    warningLive = false;
    leds->clear();
    leds->setPixelColor(1, leds->Color(255, 255, 255));
    leds->show();
    
    noTone(BUZZER);

    display->clearDisplay();
    display->setCursor(0, 0);
    display->println("Acknowledgement:");
    display->println("Ignored");
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


void BluetoothSensor::SOSCall(){
  //black button to confirm
  //piggy back off warning system channels
    //Hard code message
    //Send in json (base off of sendToServer)
    //display message (on their way, stay in the room)
      //could light up an LED to a colour to match customer and staff??? (would have to add method to recieve message and decipher LED config)
      //OR just shine on customer a known colour

  //both buttons to suggest
  if(digitalRead(BLACK_BUTTON) == HIGH && digitalRead(RED_BUTTON)){//loop waiting for response??
    //display message
    display->clearDisplay();
    display->setCursor(0, 0);
    display->println("Would you like some assisstance?");
    display->println("Black - Confirm\tRed - Cancel");
    display->display(); 
    if(digitalRead(BLACK_BUTTON) == HIGH){
      //confirm
        //display message (sending)
        //gather room id and sensor id 
        //set LEDs
        //send json
        //display message
      display->clearDisplay();
      display->setCursor(0, 0);
      display->println("Sending request");
      display->display(); 

      
      //loop below until...?
      int pixelInterval = 50;                   //  Delay time (ms)
      int pixelQueue = 0;
      int pixelCycle = 0;
      for(int i = 0; i < 3; i += 3) {
        leds.setPixelColor(i + pixelQueue, Wheel((i + pixelCycle) % 255)); //  Update delay time  
      }

      leds.show();
      
      for(int i = 0; i < 3; i += 3) {
        leds.setPixelColor(i + pixelQueue, leds.Color(0, 0, 0)); //  Update delay time  
      }

      pixelQueue++;                           //  Advance current queue  
      pixelCycle++;                           //  Advance current cycle
      
      if(pixelQueue >= 3){
        pixelQueue = 0;                       //  Loop
      }if(pixelCycle >= 256){
        pixelCycle = 0;                       //  Loop
      }

      //json file
      StaticJsonDocument<256> json;
      json["PicoID"] = mqtt->getHardwareIdentifier();
      json["RoomID"] = String(strongestScanBluetoothID);
      json["PicoType"] = picoType;
      json["Request"] = "Request for assistance in Room " + String(strongestScanBluetoothID) + ", person with bright device";

      String jsonString;
      serializeJson(json, jsonString);

      mqtt->publishDataWithIdentifier(jsonString, "warnings/staff");

      display->clearDisplay();
      display->setCursor(0, 0);
      display->println("Request sent");
      display->println("An assistant is on their way");
      display->display(); 
    }else if(digitalRead(RED_BUTTON) == HIGH){
      //cancel
        //display message
      display->clearDisplay();
      display->setCursor(0, 0);
      display->println("Cancelled");
      display->println("Press both buttons simultaneously to try again");
      display->display(); 
    }
  }
}

uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if(WheelPos < 85) {
    return leds.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if(WheelPos < 170) {
    WheelPos -= 85;
    return leds.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return leds.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}


void BluetoothSensor::sendToServer(String data) {
    // Create JSON document to send to server:
    StaticJsonDocument<256> json;

    json["PicoID"] = mqtt->getHardwareIdentifier();
    json["RoomID"] = String(strongestScanBluetoothID);
    json["PicoType"] = picoType;
    json["Data"] = data;

    String jsonString;
    serializeJson(json, jsonString);

	mqtt->publishDataWithIdentifier(jsonString, "feeds/hardware-data/");
}
