#pragma once

#include "Arduino.h"
#include <BTstackLib.h>
#include <SensorType.hpp>
#include <Adafruit_SSD1306.h>
#include <bsec.h>
#include <BH1745NUC.h>
#include "MqttConnection.hpp"


#define BH1745NUC_DEVICE_ADDRESS_38 0x38 // Light
#define ENVIRONMENT_WAIT_DURATION 10000

class RoomSensor : public SensorType {
    public:
        RoomSensor(Adafruit_SSD1306* Display, MqttConnection* Mqtt, uint16_t BluetoothID);

        virtual void setup();
        virtual void loop();
        virtual void unsetup();
        virtual int getSensorType();

    private:
        Adafruit_SSD1306* display;
        MqttConnection* mqtt;
        Bsec iaqSensor; // Climate
        static short sampleBuffer[512]; // Sound
        static volatile int samplesRead;
        BH1745NUC bh1745nuc = BH1745NUC();
        UUID ROOM_UUID;		  // The unique Room UUID, for Room Sensors only
        unsigned long lastActionTime;
        uint16_t bluetoothID;     // The RoomID, defaulted to -1 for People Sensors

        void environmentalData();
        float readSoundSamples();
        float calculateDecibels();
        static void onPDMdata();
        void sendToServer(String data);
};