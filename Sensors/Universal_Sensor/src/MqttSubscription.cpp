#include <Arduino.h>
#include "MqttSubscription.hpp"


MqttSubscription::MqttSubscription() {
    subscriptionRoute = "";
    messagePending = false;
    lastMessage = "";
}


MqttSubscription::MqttSubscription(String mqttSubscriptionRoute) {
    subscriptionRoute = mqttSubscriptionRoute;
    messagePending = false;
    lastMessage = "";
}


void MqttSubscription::invoke(String message) {
    messagePending = true;
    lastMessage = message;
}


String MqttSubscription::getSubscriptionRoute() {
    return subscriptionRoute;
}


bool MqttSubscription::hasMessage() {
    return messagePending;
}


String MqttSubscription::getMessage() {
    messagePending = false;
    return lastMessage;
}