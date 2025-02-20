#pragma once

#include <AsyncMqttClient_Generic.hpp>
#include "MqttSubscription.hpp"

#pragma once
class MqttConnection {
    public:
        MqttConnection();
        bool connectToBroker();
        bool publishToMQTT(String data, String topic);
        String getHardwareIdentifier();
        bool publishDataWithIdentifier(String data, String topic);
        bool publishHardwareData(String data);
        bool addSubscription(MqttSubscription* sub);
        bool removeSubscription(MqttSubscription* sub);


    private:
        static AsyncMqttClient mqttClient;
        static bool connectedToMQTT;
        static MqttSubscription* subscriptions[5];
        static const int maxSubscriptions;
        static int currentSubscriptionAmount;


        // MQTT Methods:
        static void onMQTTConnect(bool sessionPresent);
        static void onMQTTDisconnect(AsyncMqttClientDisconnectReason reason);
        static void onMQTTMessage(char* topic, char* payload, const AsyncMqttClientMessageProperties& properties, const size_t& len, const size_t& index, const size_t& total);
        static void onMQTTPublish(const uint16_t& packetId);
};
