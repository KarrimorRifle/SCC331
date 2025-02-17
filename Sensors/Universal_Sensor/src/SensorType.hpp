#pragma once

// Pico Configurables:
#define SERVER_PICO 0
#define ROOM_PICO 1
#define LUGGAGE_PICO 2
#define PASSENGER_PICO 3
#define STAFF_PICO 4
#define SECURITY_PICO 5

class SensorType {
    public:
        virtual void setup();
        virtual void loop();
        virtual void unsetup();
        virtual int getSensorType();

    private:

};