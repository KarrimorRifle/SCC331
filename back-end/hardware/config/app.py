# Uses paho-mqtt from pip, must include in the docker :)
import paho.mqtt.client as mqtt
import os
import json
from pydantic import BaseModel, ValidationError
import mysql.connector
from mysql.connector import Error

UNASSIGNED_PICO_TYPE = 0
ENVIRONMENT_PICO_TYPE = 1
BT_TRACKER_PICO_TYPE = 2

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


#on connection or reconnection, subscribe to all hardware config message feeds
# such that data from these feeds will be recieved by on_message
def on_connect(client, user_data, connect_flags, result_code, properties):
    print(f"Connected with result code {result_code}")

    #subscribe to all hardware data feeds
    client.subscribe("hardware_config/hardware_message/#")
    client.subscribe("test/hardware_config/hardware_message/#")
    print("Subscribed to hardware feeds")


class ConfigRequest(BaseModel):
    PicoID: str


def handle_new_device(client, cursor, pico_id):
    print("Handling new device with picoid " + pico_id)
    print("")
    insert_statement = "INSERT INTO pico_device(picoID, readablePicoID) VALUES (%s, %s);"
    cursor.execute(insert_statement, (pico_id, pico_id));

    response = json.dumps({"ReadableID" : pico_id, "BluetoothID" : 0, "PicoType" : UNASSIGNED_PICO_TYPE, "TrackerGroup" : ""})
    publish_info = client.publish("hardware_config/server_message/" + pico_id, response, qos=2)
    publish_info.wait_for_publish()

    print("Published msg")
    print(response)
    print("")


def handle_known_device(client, cursor, pico_id, current_device_data):
    print("Handling known device with picoid " + pico_id)
    print("Device data: ", current_device_data)
    readable_id = current_device_data[0]
    bt_id = int(current_device_data[1])
    if bt_id == None:
        bt_id = 0
    pico_type = current_device_data[2]
    
    if (pico_type == UNASSIGNED_PICO_TYPE):
        response = json.dumps({"ReadableID" : readable_id, "BluetoothID" : bt_id, "PicoType" : UNASSIGNED_PICO_TYPE, "TrackerGroup" : ""})
        publish_info = client.publish("hardware_config/server_message/" + pico_id, response, qos=2)
        publish_info.wait_for_publish()

        print("Published msg")
        print(response)
        print("")

    elif (pico_type == BT_TRACKER_PICO_TYPE):
        bt_tracker_select_statement = """SELECT tracking_groups.groupName
                                            FROM tracking_groups
                                            INNER JOIN bluetooth_tracker ON tracking_groups.groupID = bluetooth_tracker.trackingGroupID
                                            WHERE bluetooth_tracker.picoID = %s;"""
        cursor.execute(bt_tracker_select_statement, (pico_id,))

        bt_tracker_data = cursor.fetchone()

        tracking_group = ""

        if bt_tracker_data != None:
            tracking_group = bt_tracker_data[0] 

        response = json.dumps({"ReadableID" : readable_id, "BluetoothID" : bt_id, "PicoType" : BT_TRACKER_PICO_TYPE, "TrackerGroup" : tracking_group})
        publish_info = client.publish("hardware_config/server_message/" + pico_id, response, qos=2)
        publish_info.wait_for_publish()

        
        print("Published msg")
        print(response)
        print("")

    elif(pico_type == ENVIRONMENT_PICO_TYPE):
        response = json.dumps({"ReadableID" : readable_id, "BluetoothID" : bt_id, "PicoType" : ENVIRONMENT_PICO_TYPE, "TrackerGroup" : ""})
        publish_info = client.publish("hardware_config/server_message/" + pico_id, response, qos=2)
        publish_info.wait_for_publish()
        
        print("Published msg")
        print(response)
        print("")


#whenever a message is recieved from a feed, print it and its details
def on_message(client, user_data, message):
    print(f'message from "{message.topic}":')
    # print(str(message.payload))

    # Decode message into utf-8
    payload_str = message.payload.decode("utf-8", errors="ignore")

    print(payload_str)

    # Make sure it is a json
    try:
        hardware_request_data = ConfigRequest.parse_raw(payload_str)
    except json.JSONDecodeError:
        print("ERR: invalid json")
        return
    except ValidationError as e:
        print("ERR: invalid structure", e)
        return
    except e:
        print("Unknown error", e)
        return

    # Make sure there is SQL connection
    db_connection = get_db_connection()
    if db_connection is None:
        print("ERR: No database connection, check the DB is up!")
        return
    cursor = db_connection.cursor()

    select_statement = "SELECT readablePicoID, bluetoothID, picoType FROM pico_device WHERE picoID = %s;"

    cursor.execute(select_statement, (hardware_request_data.PicoID,))

    current_device_data = cursor.fetchone()

    if current_device_data is None:
        handle_new_device(client, cursor, pico_id=hardware_request_data.PicoID)
    else:
        handle_known_device(client, cursor, hardware_request_data.PicoID, current_device_data)

    cursor.close()


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
