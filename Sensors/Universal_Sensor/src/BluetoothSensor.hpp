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
#define RED_BUTTON 13    
#define BLACK_BUTTON 12

class BluetoothSensor : public SensorType {
    public:
        BluetoothSensor(Adafruit_SSD1306* Display, MqttConnection* Mqtt, Adafruit_NeoPixel* Leds, uint16_t BluetoothID);

        virtual void setup();
        virtual void loop();
        virtual void unsetup();
        virtual int getSensorType();
        void setSensorType(int PicoType);
        // Bluetooth Receiver Methods:
        static void advertisementCallback(BLEAdvertisement *adv);

    private:
        Adafruit_SSD1306* display;
        MqttConnection* mqtt;
        Adafruit_NeoPixel* leds;
        // BLE Scanning Variables:
        static int strongestScanBluetoothID;
        static int strongestRSSI;
        unsigned long lastActionTime;
        bool isScanning;
        int picoType;
        uint16_t bluetoothID; // The room the user / luggage is currently in, according to the majorID picked up

        MqttSubscription globalWarningSubscription;
        MqttSubscription warningSubscription;

        bool warningLive;
        
        void sendToServer(String data);

        void setWarningSubscriptions();
        void unsetWarningSubscriptions();
        void handleWarning(String message, String source);
        void checkForAcknowledgement();
        void warningOver();

        void ledSetup();

        void SOSCall();
        void rainbowLEDs(uint8_t wait);
        uint32_t Wheel(byte WheelPos);
};