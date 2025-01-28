# Uses paho-mqtt from pip, must include in the docker :)
import paho.mqtt.client as mqtt
import os


#on connection or reconnection, subscribe to all hardware data feed
# such that data from these feeds will be recieved by on_message
def on_connect(client, user_data, connect_flags, result_code, properties):
    print(f"Connected with result code {result_code}")

    #subscribe to all hardware data feeds
    client.subscribe("feeds/hardware-data/#")
    print("Subscribed to hardware feeds")


#whenever a message is recieved from a feed, print it and its details
def on_message(client, user_data, message):
    print(f'message from "{message.topic}":')
    print(str(message.payload))


#set up the client to recieve messages
def main():
    #get the mqtt access from a local env folder
    # if this fails exit main
    print("Getting access token")
    access_token = os.getenv("mqtt_token")
    print(f"Access token: {access_token}")

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
    print("hello")
    main()