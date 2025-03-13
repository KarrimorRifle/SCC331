#include "RoomSensor.hpp"
#include <Arduino.h>
#include <PDM.h>
#include <ArduinoJson.h>
extern "C" void flash_get_unique_id(uint8_t *p);

short RoomSensor::sampleBuffer[512]; // Sound
volatile int RoomSensor::samplesRead = 0;


RoomSensor::RoomSensor(Adafruit_SSD1306* Display, MqttConnection* Mqtt, uint16_t BluetoothID, String* ReadableID) {
    display = Display;
    mqtt = Mqtt;
    readableID = ReadableID;
    lastActionTime = millis();
    bluetoothID = BluetoothID;
    currentlyActive = false;
    hasBeenActive = false;
}


void RoomSensor::setup() {
  if (!hasBeenActive) {
    // Initialise Climate Sensors:
    iaqSensor.begin(BME68X_I2C_ADDR_LOW, Wire);
    bsec_virtual_sensor_t sensorList[13] = {
      BSEC_OUTPUT_IAQ,
      BSEC_OUTPUT_STATIC_IAQ,
      BSEC_OUTPUT_CO2_EQUIVALENT,
      BSEC_OUTPUT_BREATH_VOC_EQUIVALENT,
      BSEC_OUTPUT_RAW_TEMPERATURE,
      BSEC_OUTPUT_RAW_PRESSURE,
      BSEC_OUTPUT_RAW_HUMIDITY,
      BSEC_OUTPUT_RAW_GAS,
      BSEC_OUTPUT_STABILIZATION_STATUS,
      BSEC_OUTPUT_RUN_IN_STATUS,
      BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_TEMPERATURE,
      BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_HUMIDITY,
      BSEC_OUTPUT_GAS_PERCENTAGE
    };

    iaqSensor.updateSubscription(sensorList, 13, BSEC_SAMPLE_RATE_LP);

    // Light: 
    bh1745nuc.begin(BH1745NUC_DEVICE_ADDRESS_38);
    bh1745nuc.startMeasurement();
  }

  // Noise:
  PDM.onReceive(this->onPDMdata);
  PDM.setCLK(3);
  PDM.setDIN(2);
  if(!PDM.begin(1, 16000)){
    Serial.println("failed to start PDM");
    while(1);
  }
  
  // Initialise Bluetooth Stuff:
  BTstack.iBeaconConfigure(&ROOM_UUID, bluetoothID, 0);
  BTstack.startAdvertising();

  currentlyActive = true;
}


void RoomSensor::loop() {
  unsigned long currentTime = millis();
  display->clearDisplay();
  display->println("Environment Sensor");
  display->print("Device Name: ");
  display->println((*readableID));
  display->println("BTid: " + String(bluetoothID));
  display->setCursor(0, 0);
  display->display();

  if (currentTime - lastActionTime >= ENVIRONMENT_WAIT_DURATION) {
    lastActionTime = currentTime;
    environmentalData();

    // Update display:
    display->clearDisplay();
    display->setCursor(0, 0);
    display->println("Broadcasting...");
    display->display(); 
  }

  BTstack.loop();
}


void RoomSensor::unsetup() {
  BTstack.stopAdvertising();
  PDM.end();
}


void RoomSensor::setBluetoothID(uint16_t newBluetoothID) {
  if (newBluetoothID != bluetoothID) {
    bluetoothID = newBluetoothID;

    if (currentlyActive) {
      BTstack.stopAdvertising();
      BTstack.iBeaconConfigure(&ROOM_UUID, bluetoothID, 0);
      BTstack.startAdvertising();
    }
  }
}


int RoomSensor::getSensorType() {
    return ROOM_PICO;
}


//private methods
void RoomSensor::environmentalData() {
  // Get the data:
  iaqSensor.run();
  bh1745nuc.read();  

  // Process the data:
  float sound = readSoundSamples();
  String temperature =  String(iaqSensor.temperature - 4.49);
  String light = String(bh1745nuc.clear);
  String airQuality = String(iaqSensor.iaq);
  String pressure = String(iaqSensor.pressure / 100);
  String humidity = String(iaqSensor.humidity);


  // Send data to server via helpermethod:
  String dataLine = String(light) + "," + String(sound) + "," + String(temperature) + "," + String(airQuality) + "," + String(pressure) + "," + String(humidity);
  sendToServer(dataLine);    
   
}


float RoomSensor::readSoundSamples() {
  if (samplesRead > 0) {
    float decibels = calculateDecibels();
    samplesRead = 0; // Reset the sample count after processing
    return decibels;
  }
  return -1; 
}


float RoomSensor::calculateDecibels() {
  float sum = 0;
  for (int i = 0; i < samplesRead; i++) {
    sum += abs(sampleBuffer[i]);
  }
  float average = sum / samplesRead;
  return -20.0f * log10(average / 32767.0f); // Convert average value to decibels
}


void RoomSensor::onPDMdata() {
  int bytesAvailable = PDM.available();
  PDM.read(sampleBuffer, bytesAvailable);
  // 16-bit, 2 bytes per sample
  samplesRead = bytesAvailable / 2;
}


void RoomSensor::sendToServer(String data) {
  // Create JSON document to send to server:
  StaticJsonDocument<256> json;

  json["PicoID"] = mqtt->getHardwareIdentifier();;
  json["RoomID"] = bluetoothID;
  json["PicoType"] = ROOM_PICO;
  json["Data"] = data;

  String jsonString;
  serializeJson(json, jsonString);

  mqtt->publishDataWithIdentifier(jsonString, "feeds/hardware-data/");
}