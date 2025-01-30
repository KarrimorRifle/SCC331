# Uses paho-mqtt from pip, must include in the docker :)
import paho.mqtt.client as mqtt
import os
import json
import mysql.connector
from mysql.connector import Error

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

#on connection or reconnection, subscribe to all hardware data feed
# such that data from these feeds will be recieved by on_message
def on_connect(client, user_data, connect_flags, result_code, properties):
    print(f"Connected with result code {result_code}")

    #subscribe to all hardware data feeds
    client.subscribe("feeds/hardware-data/#")
    print("Subscribed to hardware feeds")

from pydantic import BaseModel, ValidationError
from typing import Union

class PicoData(BaseModel):
    PicoID: int
    RoomID: int
    PicoType: int
    Data: Union[str, int]

#whenever a message is recieved from a feed, print it and its details
def on_message(client, user_data, message):
    print(f'message from "{message.topic}":')
    # print(str(message.payload))

    # Decode message into utf-8
    payload_str = message.payload.decode("utf-8", errors="ignore")

    # Make sure it is a json
    try:
        data = PicoData.parse_raw(payload_str)
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

    # If it is a room sensor we do this
    if data.PicoType == 1:
        # Variables are split into Sound, Light, and Temperature
        env_data = data.Data.split(",")
        
        # Insert data into the database
        try:
            cursor.execute(
                "INSERT INTO environment (picoID, roomID, logged_at, sound, light, temperature, IAQ, pressure, humidity) "
                "VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s)",
                (data.PicoID, data.RoomID, env_data[0], env_data[1], env_data[2], env_data[3], env_data[4], env_data[5])
            )
            db_connection.commit()
        except Error as e:
            print(f"Error inserting data into MySQL: {e}")
        except:
            print("Incorrect format")

    else:
        # Otherwise just put the data in
        try:
            get_table_name = lambda pico_type: 'luggage' if pico_type == 2 else 'users' if pico_type == 3 else None
            table_name = get_table_name(data.PicoType)
            if table_name:
                query = f"INSERT INTO {table_name} (picoID, roomID, logged_at) VALUES (%s, %s, NOW())"
                cursor.execute(query, (data.PicoID, data.RoomID))
                db_connection.commit()
            else:
                print(f"Invalid PicoType {data.PicoType}")
        except Error as e:
            print(f"Error inserting data into MySQL: {e}")
        except e:
            print("unknown error", e)
    
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