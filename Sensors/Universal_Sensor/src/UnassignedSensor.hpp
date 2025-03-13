#pragma once
#include "SensorType.hpp"

class UnassignedSensor : public SensorType {
    public:
        UnassignedSensor();

        virtual void setup();
        virtual void loop();
        virtual void unsetup();
        virtual int getSensorType();
};