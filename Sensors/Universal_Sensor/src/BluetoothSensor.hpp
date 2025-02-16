#pragma once

#include "Arduino.h"
#include <BTstackLib.h>
#include <SensorType.hpp>
#include <Adafruit_SSD1306.h>
#include <Adafruit_NeoPixel.h>
#include "MqttConnection.hpp"


#define BH1745NUC_DEVICE_ADDRESS_38 0x38 // Light
#define ENVIRONMENT_WAIT_DURATION 10000
#define SCAN_DURATION 9500
#define WAIT_DURATION 500
#define BUZZER 7

class BluetoothSensor : public SensorType {
    public:
        BluetoothSensor(Adafruit_SSD1306* Display, MqttConnection* Mqtt, Adafruit_NeoPixel* Leds);

        virtual void setup();
        virtual void loop();
        virtual void unsetup();
        virtual int getSensorType();
        void setSensorType(int PicoType);
        // Bluetooth Receiver Methods:
        static void advertisementCallback(BLEAdvertisement *adv);
        void ledSetup();
        void warningRecieved(String message);
        void warningAcknowledged();
        void warningOver();

    private:
        Adafruit_SSD1306* display;
        MqttConnection* mqtt;
        Adafruit_NeoPixel* leds;
        // BLE Scanning Variables:
        int strongestMajorID;
        static int strongestRSSI;
        unsigned long lastActionTime;
        bool isScanning;
        int picoType;
        int majorID; // The room the user / luggage is currently in, according to the majorID picked up
        uint8_t minorID;
        bool warningLive;
        String warningMessage;
        
        void sendToServer(String data);
};