from umqtt.robust import MQTTClient
import env

#class that abstracts the MQTT client connection to the backend server
class BackendConnection():
    
    def __init__(self):
        self.client_uid = env.CLIENT_UID
        self.topic_to_publish = "feeds/hardware-data/" + self.client_uid
        
        self.client = MQTTClient(self.client_uid , env.MQTT_SERVER_IP, user = env.MQTT_USERNAME, password = env.MQTT_PASSWORD)
        self.client.connect()
        
    #publishes the message provided to this devices specific topic location
    def publishMessage(self, message):
        self.client.publish(self.topic_to_publish, message)
        