import paho.mqtt.client as mqtt
import json
import os
import mysql.connector
from mysql.connector import Error
import threading
import time
import random

# All rules are AND rules, so if one statement is false then we will be stopping
rules = []
roomData = {}

db_connection = None
rules_lock = threading.Lock()

firstTime = True
node_id = os.getenv('NODE_ID', '1')  # Set the node ID from environment variable or default to '1'
active = False
last_heartbeat = 0
last_message = 0
leader_timer = None

def get_db_connection():
    retry = 5
    global db_connection
    if db_connection and db_connection.is_connected():
        return db_connection
    for _ in range(retry):
        try:
            db_connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            if db_connection.is_connected():
                return db_connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            db_connection = None
    return db_connection

def grabRules():
    global firstTime
    global rules
    with rules_lock:
        connection = get_db_connection()
        if connection is None:
            print("Database connection failed")
            return

        cursor = connection.cursor(dictionary=True)
        
        # Check the updated flag
        cursor.execute("SELECT updated FROM updated WHERE id = 1")
        updated_flag = cursor.fetchone()["updated"]
        
        if not firstTime and not updated_flag:
            print("No updates to rules, skipping fetch")
            return
        
        cursor.execute("""
            SELECT r.id, r.name, rc.roomID, rc.variable, rc.upper_bound, rc.lower_bound, rm.authority, rm.title, rm.location, rm.severity, rm.summary
            FROM rule r
            LEFT JOIN rule_conditions rc ON r.id = rc.rule_id
            LEFT JOIN rule_messages rm ON r.id = rm.rule_id
        """)
        rules_data = cursor.fetchall()
        cursor.close()

        new_rules = []
        rules_dict = {}
        for row in rules_data:
            rule_id = row["id"]
            if rule_id not in rules_dict:
                rule_obj = {
                    "id": rule_id,
                    "name": row["name"],
                    "conditions": [],
                    "messages": []
                }
                rules_dict[rule_id] = rule_obj
                new_rules.append(rule_obj)

            roomID = row["roomID"]
            condition = next((c for c in rules_dict[rule_id]["conditions"] if c["roomID"] == roomID), None)
            if not condition:
                condition = {
                    "roomID": roomID,
                    "conditions": []
                }
                rules_dict[rule_id]["conditions"].append(condition)
            condition["conditions"].append({
                "variable": row["variable"],
                "lower_bound": row["lower_bound"],
                "upper_bound": row["upper_bound"]
            })

            rules_dict[rule_id]["messages"].append({
                "Authority": row["authority"],
                "Title": row["title"],
                "Location": row["location"],
                "Severity": row["severity"],
                "Summary": row["summary"]
            })

        rules = new_rules
        print("Rules updated")
        print(json.dumps(rules, indent=2))  # Print the rules variable for verification

        # Reset the updated flag
        cursor = connection.cursor()
        cursor.execute("UPDATE updated SET updated = 0 WHERE id = 1")
        connection.commit()
        cursor.close()

        firstTime = False

# Steal from the processor
from pydantic import BaseModel, ValidationError
from typing import Union

class PicoData(BaseModel):
    PicoID: Union[str, int]
    RoomID: Union[str, int]
    PicoType: int
    Data: Union[str, int]

# Dictionary to track the current RoomID and PicoType for each PicoID
pico_locations = {}
pico_types = {}
pico_last_seen = {}

# Dictionaries to count the number of Pico devices in each RoomID for each PicoType
room_counts = {
    "luggage": {},
    "users": {},
    "staff": {},
    "guard": {}
}

def update_room_counts(pico_id, old_pico_type, new_pico_type, old_room_id, new_room_id):
    pico_type_keys = {
        2: "luggage",
        3: "users",
        4: "staff",
        5: "guard"
    }

    old_pico_type_key = pico_type_keys.get(old_pico_type)
    new_pico_type_key = pico_type_keys.get(new_pico_type)

    if old_pico_type_key:
        # Remove from old room
        if old_room_id in room_counts[old_pico_type_key]:
            room_counts[old_pico_type_key][old_room_id] -= 1
            if room_counts[old_pico_type_key][old_room_id] == 0:
                del room_counts[old_pico_type_key][old_room_id]

    if new_pico_type_key:
        # Add to new room
        if new_room_id not in room_counts[new_pico_type_key]:
            room_counts[new_pico_type_key][new_room_id] = 0
        room_counts[new_pico_type_key][new_room_id] += 1

def grabRoomCount(room_id, pico_type):
    pico_type_keys = {
        "luggage": 2,
        "users": 3,
        "staff": 4,
        "guard": 5
    }

    pico_type_key = pico_type_keys.get(pico_type)
    if pico_type_key is None:
        print(f"Invalid pico type: {pico_type}")
        return 0

    return room_counts.get(pico_type, {}).get(room_id, 0)

def check_pico_status():
    while True:
        current_time = time.time()
        to_remove = []
        for pico_id, last_seen in pico_last_seen.items():
            if current_time - last_seen > 120:  # 2 minutes
                old_room_id = pico_locations.get(pico_id)
                old_pico_type = pico_types.get(pico_id)
                update_room_counts(pico_id, old_pico_type, None, old_room_id, None)
                to_remove.append(pico_id)

        for pico_id in to_remove:
            del pico_locations[pico_id]
            del pico_types[pico_id]
            del pico_last_seen[pico_id]
            del roomData[pico_id]

        time.sleep(60)  # Check every minute

def start_leader_timer(client):
    global leader_timer

    def become_leader():
        global active
        active = True
        client.publish(f"checkingwarnings/{node_id}", str(time.time()))
        print("Node is now active")

    delay = random.uniform(1, 5)  # Random delay between 1 and 5 seconds
    leader_timer = threading.Timer(delay, become_leader)
    leader_timer.start()

#whenever a message is recieved from a feed, print it and its details
def on_message(client, user_data, message):
    global active, last_heartbeat, leader_timer

    # Ignore own heartbeat messages
    if message.topic == f"checkingwarnings/{node_id}":
        return
    
    if message.topic.startswith("checkingwarnings/"):
        last_heartbeat = time.time()
        if leader_timer:
            leader_timer.cancel()
            leader_timer = None
        return
    
    last_message = time.time()

    if active:
        grabRules()
        client.publish(f"checkingwarnings/{node_id}", str(time.time()))

    # Process the message
    print(f'message from "{message.topic}":')

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
    except Exception as e:
        print("Unknown error", e)
        return
    
    pico_id = data.PicoID
    pico_last_seen[pico_id] = time.time()

    if data.PicoType == 1:  # Room data
        try:
            env_data = list(map(float, data.Data.split(',')))
            if len(env_data) != 6:
                print("ERR: invalid environment data length")
                return
        except ValueError:
            print("ERR: invalid environment data format")
            return

        key = str(data.RoomID)
        roomData[key] = {
            "sound": env_data[0],
            "light": env_data[1],
            "temperature": env_data[2],
            "IAQ": env_data[3],
            "pressure": env_data[4],
            "humidity": env_data[5]
        }

    if data.PicoType in [2, 3, 4, 5]:  # Luggage, Users, Staff, Guard
        new_room_id = str(data.RoomID)
        old_room_id = pico_locations.get(pico_id)
        old_pico_type = pico_types.get(pico_id)

        if old_room_id != new_room_id or old_pico_type != data.PicoType:
            update_room_counts(pico_id, old_pico_type, data.PicoType, old_room_id, new_room_id)
            pico_locations[pico_id] = new_room_id
            pico_types[pico_id] = data.PicoType

    # Check if the node should become active
    if not active:
        if last_heartbeat < last_message - 0.2:  # No heartbeat received for 60 seconds
            start_leader_timer(client)
        return
    
    # Process the rule data
    for rule in rules:
        sendMessage = True 
        for condition in rule["conditions"]:
            roomID = condition["roomID"]
            for variable in condition["conditions"]:
                if variable["variable"] in ["users", "guard", "luggage", "staff"]:
                    count = grabRoomCount(roomID, variable["variable"])
                    if count < variable["lower_bound"] or count > variable["upper_bound"]:
                        sendMessage = False
                        break
                else:
                    value = roomData.get(roomID,{}).get(variable["variable"], None)
                    if value is None:
                        broken_sensor_message = {
                            "Title": f"Broken room sensor: {roomID}",
                            "Location": "SENSOR",
                            "Severity": "warning",
                            "Summary": f"sensor with roomID {roomID} has no valid data, please give it a checkup"
                        }
                        client.publish("warning/admin/-1", json.dumps(broken_sensor_message))
                        sendMessage = False
                        break
                    if value < variable["lower_bound"] or value > variable["upper_bound"]:
                        sendMessage = False
                        break
            if not sendMessage:
                break
        
        # If we dont need to send a message go onto the next rule
        if not sendMessage:
            continue

        # then we continue on to send the messages
        for message in rule["messages"]:
            authority = message.pop("Authority")
            client.publish(f"warning/{authority}/{rule['id']}", json.dumps(message))


def on_connect(client, user_data, connect_flags, result_code, properties):
    print(f"Connected with result code {result_code}")

    #subscribe to all hardware data feeds
    client.subscribe("feeds/hardware-data/#")
    client.subscribe("checkingwarnings/#")
    print("Subscribed to hardware feeds")

#set up the client to recieve messages
def main():
    global last_heartbeat
    
    # Start background thread to check Pico status
    threading.Thread(target=check_pico_status, daemon=True).start()
    
    # MQTT connection
    print("Getting access token")
    access_token = os.getenv("mqtt_token")
    print("Access token found")

    if not access_token:
        print("Error: Token not found")
        return

    #set up the mqtt client
    print("Starting mqtt client")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(access_token, None)
    client.connect("mqtt.flespi.io", 1883)
    client.loop_forever()

if __name__ == "__main__":
    main()