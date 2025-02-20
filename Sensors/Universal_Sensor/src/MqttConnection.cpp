#include "MqttConnection.hpp"
#include <AsyncMqttClient_Generic.hpp>
#include <AsyncMqttClient_Generic_Impl.h>
#include "env.cpp"

// MQTT Stuff:
#define MQTT_SERVER "mqtt.flespi.io"
#define MQTT_PORT 1883

#ifndef MQTT_TOKEN
#define MQTT_TOKEN ""
#endif


AsyncMqttClient MqttConnection::mqttClient;
bool MqttConnection::connectedToMQTT;
MqttSubscription* MqttConnection::subscriptions[5];
const int MqttConnection::maxSubscriptions = 5;
int MqttConnection::currentSubscriptionAmount;


MqttConnection::MqttConnection() {
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
    mqttClient.setCredentials(MQTT_TOKEN);

    mqttClient.onConnect(onMQTTConnect);
    mqttClient.onDisconnect(onMQTTDisconnect);
    mqttClient.onPublish(onMQTTPublish);
    mqttClient.onMessage(onMQTTMessage);
    mqttClient.setKeepAlive(65000);

    connectedToMQTT = false;
}


bool MqttConnection::connectToBroker() {
    mqttClient.connect();
    connectedToMQTT = mqttClient.connected();
    long startTime = millis();
    while(!connectedToMQTT && startTime + 10000 != millis())
        connectedToMQTT = mqttClient.connected();
    return connectedToMQTT;
}


bool MqttConnection::publishToMQTT(String data, String topic) {
    //WiFi.macAddress();
    Serial.printf("Publishing message in topic '%s': %s\n", topic.c_str(), data.c_str());

    if (!connectedToMQTT) {
        mqttClient.connect();
    }
    if (connectedToMQTT) {
        mqttClient.publish(topic.c_str(), 2, true, data.c_str());
        return true;
    }
    return false;
}


String MqttConnection::getHardwareIdentifier() {
    String macAddress = WiFi.macAddress();
    macAddress.replace(":", "");
    return macAddress;
}


bool MqttConnection::publishDataWithIdentifier(String data, String topic) {
    String id = getHardwareIdentifier();
    topic.concat(id);
    return publishToMQTT(data, topic);
}


bool MqttConnection::publishHardwareData(String data) {
    String topic = "feeds/hardware-data/";
    return publishDataWithIdentifier(data, topic);
}


bool MqttConnection::addSubscription(MqttSubscription* sub) {
    if (currentSubscriptionAmount == maxSubscriptions) {
        Serial.println("Max reached");
        return false;
    }

    if (sub->getSubscriptionRoute() == "") {
        Serial.println("No route");
        return false;
    }

    mqttClient.subscribe(sub->getSubscriptionRoute().c_str(), 2);

    subscriptions[currentSubscriptionAmount] = sub;
    currentSubscriptionAmount++;
    return true;


}


bool MqttConnection::removeSubscription(MqttSubscription* sub) {
    for (int i = 0; i < currentSubscriptionAmount; i++) {
        if (subscriptions[currentSubscriptionAmount]->getSubscriptionRoute().equals(sub->getSubscriptionRoute())) {
            for (int j = currentSubscriptionAmount; j > i; j--) {
                subscriptions[j-1] = subscriptions[j];
            }
            return true;
        }
    }

    return false;
}


// MQTT Methods:
void MqttConnection::onMQTTConnect(bool sessionPresent) {
    connectedToMQTT = true;
    Serial.println("Connected to MQTT.");
}


void MqttConnection::onMQTTDisconnect(AsyncMqttClientDisconnectReason reason) {
    connectedToMQTT = false;

    Serial.print("Disconnected from MQTT, reason:");
    String reasonText = "";
    switch ((uint8_t) reason)
    {
      case 0:   //TCP_DISCONNECTED:
        reasonText = "TCP_DISCONNECTED";
        break;
  
      case 1:   //MQTT_UNACCEPTABLE_PROTOCOL_VERSION:
        reasonText = "MQTT_UNACCEPTABLE_PROTOCOL_VERSION";
        break;
  
      case 2:   //MQTT_IDENTIFIER_REJECTED:
        reasonText = "MQTT_IDENTIFIER_REJECTED";
        break;
  
      case 3:   //MQTT_SERVER_UNAVAILABLE:
        reasonText = "MQTT_SERVER_UNAVAILABLE";
        break;
  
      case 4:   //MQTT_MALFORMED_CREDENTIALS:
        reasonText = "MQTT_MALFORMED_CREDENTIALS";
        break;
  
      case 5:   //MQTT_NOT_AUTHORIZED:
        reasonText = "MQTT_NOT_AUTHORIZED";
        break;
  
      case 6:   //ESP8266_NOT_ENOUGH_SPACE:
        reasonText = "ESP8266_NOT_ENOUGH_SPACE";
        break;
  
      case 7:   //TLS_BAD_FINGERPRINT:
        reasonText = "TLS_BAD_FINGERPRINT";
        break;
  
      default:
        break;
    }
    Serial.println(reasonText);

    // mqttClient.connect();
    // connectedToMQTT = mqttClient.connected();
    // long startTime = millis();
    // while(!connectedToMQTT && startTime + 10000 != millis()) {
    //     connectedToMQTT = mqttClient.connected();
    // }
}


void MqttConnection::onMQTTMessage(char* topic, char* payload, const AsyncMqttClientMessageProperties& properties, const size_t& len, const size_t& index, const size_t& total) {
    String message = String(payload, len);

    Serial.print("Message Recieved from: ");
    Serial.println(topic);
    Serial.println(message);

    for (int i = 0; i < currentSubscriptionAmount; i++) {
        String subscriptionRoute = subscriptions[i]->getSubscriptionRoute();
        String subscriptionRouteStripped = subscriptionRoute.substring(0, subscriptionRoute.length() - 1);

        if (String(topic).startsWith(subscriptionRouteStripped)) {
            subscriptions[i]->invoke(message);
            break;
        }
    }
}


void MqttConnection::onMQTTPublish(const uint16_t& packetId) {
    Serial.println("Publish acknowledged.");
    Serial.print("  packetId: ");
    Serial.println(packetId);
}


// void subscribeToWarnings() {
// 	switch (picoType)
// 	{
// 	case SECURITY_PICO:
// 		/* code */
// 		mqttClient.subscribe("feeds/warning/security/#", 2);
// 		break;

// 	case STAFF_PICO:
// 		mqttClient.subscribe("feeds/warning/staff/#", 2);
// 		break;

// 	case PASSENGER_PICO:
// 		mqttClient.subscribe("feeds/warning/user/#", 2);
// 		break;

// 	default:
// 		break;
// 	}
// }


// void unsubscribeToWarnings() {
// 	mqttClient.unsubscribe("feeds/warning/security/#");
// 	mqttClient.unsubscribe("feeds/warning/staff/#");
// 	mqttClient.unsubscribe("feeds/warning/user/#");
// }


// void subscribeToDeviceUpdates() {
// 	String macAddress = WiFi.macAddress();
//     macAddress.replace(":", "");
//     String topic = "feeds/device-updates/" + macAddress;
// 	mqttClient.subscribe(topic.c_str());
// }


// void unsubscribeToDeviceUpdates() {
// 	String macAddress = WiFi.macAddress();
//     macAddress.replace(":", "");
//     String topic = "feeds/device-updates/" + macAddress;
// 	mqttClient.unsubscribe(topic.c_str());
// }

