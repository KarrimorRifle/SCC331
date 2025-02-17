import paho.mqtt.client as mqtt
import json
import os
import mysql.connector
from mysql.connector import Error

MQTT_BROKER = "mqtt.flespi.io"
MQTT_PORT = 1883
MQTT_TOKEN = os.getenv("MQTT_TOKEN")
TOPIC = "warning/admin/#"

db_connection = None

def get_db_connection():
    global db_connection
    if db_connection is None or not db_connection.is_connected():
        try:
            db_connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            db_connection = None
        except e:
            print("Unknown error", e)
    return db_connection

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print("Active Warning Received:", json.dumps(payload, indent=2))

        if payload.get("Severity") in ["doomed", "danger"]:
            ack_topic = f"response/{payload.get('id', 'unknown')}"
            ack_payload = json.dumps({
                "response": "acknowledged",
                "name": "ActiveReader",
                "medium": "Automated"
            })
            client.publish(ack_topic, ack_payload)
            print("Acknowledgment sent to topic:", ack_topic)
    except Exception as e:
        print("Error processing active warning:", e)

def on_connect(client, user_data, connect_flags, result_code, properties):
    print(f"Connected with result code {result_code}")

    #subscribe to all hardware data feeds
    client.subscribe("feeds/hardware-data/#")
    print("Subscribed to hardware feeds")

#set up the client to recieve messages
def main():
    #get the mqtt access from a local env folder
    # if this fails exit main
    print("Getting access token")
    access_token = os.getenv("mqtt_token")
    print(f"Access token: {access_token}")
    get_db_connection()

    if not access_token:
        print("Error: Token not found")
        return

    #set up the mqtt client
    print("Starting mqtt client")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    
    #set the mqtt client to handle connections and messages
    client.on_connect = on_connect
    client.on_message = on_message

    #set the token to authorise the client
    client.username_pw_set(access_token, None)

    #connect
    client.connect("mqtt.flespi.io", 1883)

    client.loop_forever()

if __name__ == "__main__":
    main()