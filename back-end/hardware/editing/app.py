import json
from flask import Flask, request, jsonify, make_response
import mysql.connector
import paho.mqtt.client as mqtt
from flask_cors import CORS
from mysql.connector import Error
import os
import requests
import time

app = Flask(__name__)
CORS(app, supports_credentials=True)

db_connection = None

UNASSIGNED_PICO_TYPE = 0
ENVIRONMENT_PICO_TYPE = 1
BT_TRACKER_PICO_TYPE = 2

LOWEST_PICO_TYPE = UNASSIGNED_PICO_TYPE
HIGHEST_PICO_TYPE = BT_TRACKER_PICO_TYPE

MQTT_TOKEN = os.getenv("mqtt_token")


def get_db_connection(retries=5, delay=1):
    global db_connection
    for _ in range(retries):
        try:
            if db_connection != None and db_connection.is_connected():
                return db_connection
            db_connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            db_connection = None
            time.sleep(delay)
    
    print("Failed to establish database connection after retries")
    return None


def validate_session_cookie(request):
    VALIDATION_SITE = "http://account_login:5002/validate_cookie"
    cookie = request.cookies.get("session_id")

    if not cookie:
        print("No session_id cookie found.")
        return {"error": "Invalid cookie", "message": "Cookie missing"}, 401

    r = requests.get(VALIDATION_SITE, headers={"session-id": cookie})
    if r.status_code != 200:
        print("ERR: Invalid cookie detected")
        return {"error": "Invalid cookie"}, 401 #, "message": r.text
    
    data = r.json()
    if data.get("authority") not in ["Admin", "Super Admin"]:
        print("ERR: Non-admin cookie")
        return {"error": "Forbidden", "message": "User isn't a valid admin"}, 403
    
    return [data.get("uid")]


def send_individual_pico_message(pico_id, hardware_message):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    
    #set the token to authorise the client
    client.username_pw_set(MQTT_TOKEN, None)

    #connect
    client.connect("mqtt.flespi.io", 1883)
    client.loop_start()

    client.publish("hardware_config/server_message/" + pico_id, hardware_message, qos=2)

    client.loop_stop()
    client.disconnect()


def sync_tracking_grp_name_with_hardware(group_id, new_group_name = ""):
    connection = get_db_connection()
    if connection is None:
        return

    cursor = connection.cursor(dictionary=True)

    select_query = """SELECT picoID
                      FROM bluetooth_tracker
                      WHERE trackingGroupID = %s"""
    
    cursor.execute(select_query, (group_id, ))

    pico_data = cursor.fetchall()

    cursor.close() 

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    
    #set the token to authorise the client
    client.username_pw_set(MQTT_TOKEN, None)

    #connect
    client.connect("mqtt.flespi.io", 1883)
    client.loop_start()

    for pico in pico_data:
        pico_id = pico["picoID"]

        hardware_message = json.dumps({"TrackerGroup" : new_group_name})
        client.publish("hardware_config/server_message/" + pico_id, hardware_message, qos=2)
    
    client.loop_stop()
    client.disconnect()


@app.route('/get/device/configs', methods=['GET'])
def get_configs():
    cookie_validation_error = validate_session_cookie(request)
    if len(cookie_validation_error) == 2:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500

    cursor = connection.cursor()
    try:
        query = """SELECT pico_device.picoID, pico_device.readablePicoID, pico_device.picoType, bluetooth_tracker.trackingGroupID
                   FROM pico_device
                   LEFT JOIN bluetooth_tracker
                   ON pico_device.picoID = bluetooth_tracker.picoID;
                """
       
        cursor.execute(query)

        data = cursor.fetchall()

        data_to_send = []

        for row in data:
            current_config = {"picoID" : row[0],
                              "readablePicoID" : row[1],
                              "picoType" : row[2],
                              "trackingGroupID" : row[3]}
           
            data_to_send.append(current_config)

        return jsonify({"configs" : data_to_send}), 200
    
    except Error as e:
        print(f"Error querying data: {e}")
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/patch/device/config/<pico_id>', methods=['PATCH'])
def patch_config(pico_id = None):
    cookie_validation_error = validate_session_cookie(request)
    if len(cookie_validation_error) == 2:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500

    if pico_id is None:
        return jsonify({"error": "PicoID must be supplied in route"}), 400

    data = request.json

    cursor = connection.cursor(dictionary=True)
    try:
        hardware_message = {}

        if "readablePicoID" in data:
            update_query = """UPDATE pico_device 
                              SET readablePicoID = %s
                              WHERE picoID = %s;"""

            cursor.execute(update_query, (data["readablePicoID"], pico_id))

            hardware_message.update({"ReadableID" : data["readablePicoID"]})

        if "picoType" in data:
            if (data["picoType"] < LOWEST_PICO_TYPE or data["picoType"] > HIGHEST_PICO_TYPE):
                print(f"Error querying data: Invalid picoType")
                connection.rollback()
                return jsonify({"error": "Error querying data", "message": "Invalid picoType"}), 400

            delete_query = """DELETE FROM bluetooth_tracker 
                                WHERE picoID = %s;"""
            
            cursor.execute(delete_query, (pico_id,))

            new_bt_id = 0
            
            if (data["picoType"] == UNASSIGNED_PICO_TYPE):
                update_query = """UPDATE pico_device
                                    SET picoType = %s, bluetoothID = NULL
                                    WHERE picoID = %s;"""
                
                cursor.execute(update_query, (UNASSIGNED_PICO_TYPE, pico_id))

            elif (data["picoType"] == ENVIRONMENT_PICO_TYPE):
                select_query = """SELECT MAX(bluetoothID) AS btMax
                                  FROM pico_device
                                  WHERE bluetoothID < 1000;"""

                cursor.execute(select_query)
                current_bt_max = cursor.fetchone()
                if current_bt_max["btMax"] is None:
                    new_bt_id = 1000
                elif current_bt_max["btMax"] == 999:
                    new_bt_id = None
                else:
                    new_bt_id = current_bt_max["btMax"] + 1

                update_query = """UPDATE pico_device
                                  SET picoType = %s, bluetoothID = %s
                                  WHERE picoID = %s;"""
                
                cursor.execute(update_query, (ENVIRONMENT_PICO_TYPE, new_bt_id, pico_id))

                if new_bt_id is None:
                    new_bt_id = 0

            elif (data["picoType"] == BT_TRACKER_PICO_TYPE):
                select_query = """SELECT MAX(bluetoothID) AS btMax
                                  FROM pico_device
                                  WHERE bluetoothID >= 1000;"""

                cursor.execute(select_query)
                current_bt_max = cursor.fetchone()
                if current_bt_max["btMax"] is None:
                    new_bt_id = 1000
                else:
                    new_bt_id = current_bt_max["btMax"] + 1

                update_query = """UPDATE pico_device
                                  SET picoType = %s, bluetoothID = %s
                                  WHERE picoID = %s;"""
                
                cursor.execute(update_query, (BT_TRACKER_PICO_TYPE, new_bt_id, pico_id))

            hardware_message.update({"BluetoothID" : new_bt_id})
            hardware_message.update({"PicoType" : data["picoType"]})


        if "trackingGroupID" in data:
            
            update_query = """INSERT INTO bluetooth_tracker (picoID, trackingGroupID)
                              VALUES(%s, %s) 
                              ON DUPLICATE KEY UPDATE trackingGroupID = %s;"""

            cursor.execute(update_query, (pico_id, data["trackingGroupID"], data["trackingGroupID"]))

                        #update hardware message
            select_query = """SELECT tracking_groups.groupName
                              FROM tracking_groups
                              INNER JOIN bluetooth_tracker ON tracking_groups.groupID = bluetooth_tracker.trackingGroupID
                              WHERE bluetooth_tracker.picoID = %s
                              LIMIT 1;"""

            cursor.execute(select_query, (pico_id,))

            tracking_group_data = cursor.fetchone()

            print(tracking_group_data)

            if (tracking_group_data == None):
                hardware_message.update({"TrackerGroup" : ""})
            else:
                hardware_message.update({"TrackerGroup" : tracking_group_data["groupName"]})

        send_individual_pico_message(pico_id, json.dumps(hardware_message))

        connection.commit()

        return jsonify({"message" : "success"}), 200
    
    except Error as e:
        print(f"Error querying data: {e}")
        connection.rollback()
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# MUST ONLY BE USED IN TESTING
@app.route("/delete/device/config/<pico_id>", methods=['POST'])
def delete_config(pico_id = None):
    cookie_validation_error = validate_session_cookie(request)
    if len(cookie_validation_error) == 2:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500

    if pico_id is None:
        return jsonify({"error": "PicoID must be supplied in route"}), 400

    cursor = connection.cursor(dictionary=True)
    try:
        delete_sql = """DELETE FROM pico_device WHERE picoID = %s"""

        cursor.execute(delete_sql, (pico_id,))
        cursor.fetchall()

        connection.commit()

        return jsonify({"message" : "success"}), 200
    
    except Error as e:
        print(f"Error querying data: {e}")
        connection.rollback()
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/get/tracking/groups', methods=['GET'])
def get_tracking_groups():
    cookie_validation_error = validate_session_cookie(request)
    if len(cookie_validation_error) == 2:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500

    cursor = connection.cursor(dictionary=True)

    try:
        query = """SELECT groupID, groupName 
                   FROM tracking_groups"""
       
        cursor.execute(query)

        return jsonify({"groups" : cursor.fetchall()}), 200

    except Error as e:
        print(f"Error querying data: {e}")
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/add/tracking/group', methods=['POST'])
def add_tracking_group():
    cookie_validation_error = validate_session_cookie(request)
    if len(cookie_validation_error) == 2:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500

    cursor = connection.cursor(dictionary=True)

    data = request.json

    try:
        if not("groupName" in data):
            print(f"Error querying data: No groupName supplied")
            connection.rollback()
            return jsonify({"error": "Error querying data", "message": "No groupName supplied"}), 400

        if (data["groupName"] == "everyone"):
            print(f"Error querying data: Disallowed group name supplied: 'everyone'")
            connection.rollback()
            return jsonify({"error": "Error querying data", "message": "Disallowed group name supplied: 'everyone'"}), 400
        
        if (data["groupName"] == ""):
            print(f"Error querying data: Disallowed group name supplied: ''")
            connection.rollback()
            return jsonify({"error": "Error querying data", "message": "Disallowed group name supplied: ''"}), 400

        insert_query = """INSERT INTO tracking_groups (groupName)
                            VALUES (%s)"""
       
        cursor.execute(insert_query, (data["groupName"],))

        select_query = """SELECT groupID
                          FROM tracking_groups
                          WHERE groupName = %s
                          LIMIT 1;"""

        cursor.execute(select_query, (data["groupName"],))

        new_id = cursor.fetchone()["groupID"]
        cursor.fetchall()

        connection.commit()

        return jsonify({"message" : "success", "groupID" : new_id}), 200
    
    except Error as e:
        print(f"Error querying data: {e}")
        connection.rollback()
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/patch/tracking/group/<int:group_id>', methods=['PATCH'])
def patch_tracking_group(group_id = None):
    cookie_validation_error = validate_session_cookie(request)
    if len(cookie_validation_error) == 2:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500

    if group_id is None:
        return jsonify({"error": "groupID must be supplied in route"}), 400

    data = request.json

    cursor = connection.cursor(dictionary=True)
    try:
        if not("groupName" in data):
            print(f"Error querying data: No groupName supplied")
            connection.rollback()
            return jsonify({"error": "Error querying data", "message": "No groupName supplied"}), 400
        
        if (data["groupName"] == "everyone"):
            print(f"Error querying data: Disallowed group name supplied: 'everyone'")
            connection.rollback()
            return jsonify({"error": "Error querying data", "message": "Disallowed group name supplied: 'everyone'"}), 400
        
        if (data["groupName"] == ""):
            print(f"Error querying data: Disallowed group name supplied: ''")
            connection.rollback()
            return jsonify({"error": "Error querying data", "message": "Disallowed group name supplied: ''"}), 400
        
        update_query = """UPDATE tracking_groups 
                          SET groupName = %s
                          WHERE groupID = %s;"""

        cursor.execute(update_query, (data["groupName"], group_id))

        connection.commit()

        sync_tracking_grp_name_with_hardware(group_id, data["groupName"])

        return jsonify({"message" : "success"}), 200
    
    except Error as e:
        print(f"Error querying data: {e}")
        connection.rollback()
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/delete/tracking/group/<int:group_id>', methods=['POST'])
def delete_tracking_group(group_id = None):
    cookie_validation_error = validate_session_cookie(request)
    if len(cookie_validation_error) == 2:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500

    if group_id is None:
        return jsonify({"error": "groupID must be supplied in route"}), 400

    cursor = connection.cursor(dictionary=True)
    try:
        sync_tracking_grp_name_with_hardware(group_id, "")

        delete_query = """DELETE FROM tracking_groups 
                          WHERE groupID = %s;"""

        cursor.execute(delete_query, (group_id,))
        cursor.fetchall()

        connection.commit()

        return jsonify({"message" : "success"}), 200
    
    except Error as e:
        print(f"Error querying data: {e}")
        connection.rollback()
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5006)