#pragma once

#include <Arduino.h>

class MqttSubscription {
    public:
        MqttSubscription();
        MqttSubscription(String mqttSubscriptionRoute);
        void invoke(String message);
        String getSubscriptionRoute();
        bool hasMessage();
        String getMessage();

    private:
        String subscriptionRoute;
        bool messagePending;
        String lastMessage;
};