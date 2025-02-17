from flask import Flask, request, jsonify, make_response
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error
from datetime import datetime
import os
import requests
import time
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)
CORS(app)

# Establish a persistent connection to the database
db_connection = None

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


def validate_session_cookie_edit(request):
    VALIDATION_SITE = "http://account_login:5002/validate_cookie"
    cookie = request.cookies.get("session_id")

    if not cookie:
        print("No session_id cookie found.")
        return {"error": "Invalid cookie", "message": "Cookie missing"}, 401

    print(f"Cookie found: {cookie}")
    r = requests.get(VALIDATION_SITE, headers={"session-id": cookie})
    if r.status_code != 200:
        print("ERR: Invalid cookie detected")
        return {"error": "Invalid cookie"}, 401
    
    data = r.json()
    if data.get("authority") != "Admin":
        return {"error": "Unauthorized access", "message": "you don't have sufficient permission to access this resource"}, 401

    # Return user ID if everything is valid (no error)
    return None, data.get("uid")


@app.route("/warnings", methods=["GET"])
def get_warnings():
    error, status_code = validate_session_cookie_edit(request)
    if error:
        print(f"Validation error: {error}")
        return jsonify(error), status_code

    connection = get_db_connection()
    if connection is None:
        print("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM rule")
    warnings = cursor.fetchall()
    cursor.close()

    return jsonify(warnings), 200


@app.route("/warnings/<int:id>", methods=["GET"])
def get_warning(id):
    error, status_code = validate_session_cookie_edit(request)
    if error:
        print(f"Validation error: {error}")
        return jsonify(error), status_code

    connection = get_db_connection()
    if connection is None:
        print("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id, r.name, rc.roomID, rc.variable, rc.upper_bound, rc.lower_bound, rm.authority, rm.title, rm.location, rm.severity, rm.summary
        FROM rule r
        LEFT JOIN rule_conditions rc ON r.id = rc.rule_id
        LEFT JOIN rule_messages rm ON r.id = rm.rule_id
        WHERE r.id = %s
    """, (id,))
    warning_data = cursor.fetchall()
    cursor.close()

    if not warning_data:
        print("Warning not found")
        return jsonify({"error": "Warning not found"}), 404

    warning = {
        "id": warning_data[0]["id"],
        "name": warning_data[0]["name"],
        "conditions": [],
        "messages": []
    }

    conditions = {}
    for row in warning_data:
        roomID = row["roomID"]
        if roomID not in conditions:
            conditions[roomID] = {
                "roomID": roomID,
                "conditions": []
            }
        conditions[roomID]["conditions"].append({
            "variable": row["variable"],
            "lower_bound": row["lower_bound"],
            "upper_bound": row["upper_bound"]
        })

    warning["conditions"] = list(conditions.values())

    for row in warning_data:
        warning["messages"].append({
            "Authority": row["authority"],
            "Title": row["title"],
            "Location": row["location"],
            "Severity": row["severity"],
            "Summary": row["summary"]
        })

    return jsonify(warning), 200

@app.route("/warnings", methods=["POST"])
def make_warning():
    error, status_code = validate_session_cookie_edit(request)
    if error:
        print(f"Validation error: {error}")
        return jsonify(error), status_code
    
    connection = get_db_connection()
    if connection is None:
        print("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    data = request.get_json()

    name = data.get("name")
    if not name:
        print("Name is required")
        return jsonify({"error": "Name is required"}), 400

    try:
        cursor.execute("INSERT INTO rule (name, owner_id) VALUES (%s, %s)", (name, status_code))
        connection.commit()
        warning_id = cursor.lastrowid
    except Error as e:
        if "Duplicate entry" in str(e):
            print("Name already used")
            return jsonify({"error": "Name already used"}), 400
        print(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

    return jsonify({"message": "Successfully created rule", "id": warning_id}), 201

# Any admin can update it but only OWNER can delete
@app.route("/warnings/<int:id>", methods=["PATCH"])
def update_warning(id):
    error, status_code = validate_session_cookie_edit(request)
    if error:
        print(f"Validation error: {error}")
        return jsonify(error), status_code
    
    connection = get_db_connection()
    if connection is None:
        print("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    data = request.get_json()

    name = data.get("name")
    conditions = data.get("conditions")
    messages = data.get("messages")

    try:
        cursor.execute("UPDATE rule SET `name` = %s WHERE id = %s", (name, id))
        
        cursor.execute("DELETE FROM rule_conditions WHERE rule_id = %s", (id,))
        for condition in conditions:
            roomID = condition.get("roomID")
            for inner_condition in condition.get("conditions"):
                variable = inner_condition.get("variable")
                lower_bound = inner_condition.get("lower_bound")
                upper_bound = inner_condition.get("upper_bound")
                cursor.execute("""
                    INSERT INTO rule_conditions (rule_id, roomID, variable, lower_bound, upper_bound)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id, roomID, variable, lower_bound, upper_bound))
        
        cursor.execute("DELETE FROM rule_messages WHERE rule_id = %s", (id,))
        for message in messages:
            authority = message.get("Authority")
            title = message.get("Title")
            location = message.get("Location")
            severity = message.get("Severity")
            summary = message.get("Summary")
            cursor.execute("""
                INSERT INTO rule_messages (rule_id, authority, title, location, severity, summary)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id, authority, title, location, severity, summary))
        
        connection.commit()
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

    return jsonify({"message": "Successfully updated rule"}), 200

@app.route("/warnings/<int:id>", methods=["DELETE"])
def delete_warning(id):
    error, status_code = validate_session_cookie_edit(request)
    if error:
        print(f"Validation error: {error}")
        return jsonify(error), status_code
    
    connection = get_db_connection()
    if connection is None:
        print("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT `name` FROM rule WHERE id = %s", (id,))
    name = cursor.fetchone()["name"]

    try:
        cursor.execute("DELETE FROM rule WHERE id = %s", (id,))
        connection.commit()
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

    return jsonify({"message":"successfully deleted rule", "rule":name}), 200

@app.route("/warnings/test", methods=["POST"])
def queue_test():
    error, status_code = validate_session_cookie_edit(request)
    if error:
        print(f"Validation error: {error}")
        return jsonify(error), status_code
    
    data = request.get_json()
    mode = data.get("mode")
    id = data.get("id")
    
    if mode not in ["full", "messages"]:
        print("Invalid mode")
        return jsonify({"error": "Mode needs to be either 'full' or 'messages'"}), 400
    
    connection = get_db_connection()
    if connection is None:
        print("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id FROM rule WHERE id = %s", (id,))
    rule = cursor.fetchone()

    if rule is None:
        print("Invalid rule id")
        return jsonify({"error": "Invalid rule id"}), 400
    
    try:
        cursor.execute("INSERT INTO tests (rule_id, mode, requested_user) VALUES (%s, %s, %s)", (id, mode, status_code))
        connection.commit()
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

    return jsonify({"message": "Test queued successfully"}), 200

@app.route("/warnings/test/result/<int:id>", methods=["GET"])
def get_test_result(id):
    error, status_code = validate_session_cookie_edit(request)
    if error:
        print(f"Validation error: {error}")
        return jsonify(error), status_code
    
    connection = get_db_connection()
    if connection is None:
        print("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.id, t.rule_id, t.mode, t.result, t.completed_time, r.name AS rule_name, u.full_name AS requested_by
        FROM tests t
        JOIN rule r ON t.rule_id = r.id
        LEFT JOIN accounts.users u ON t.requested_user = u.user_id
        WHERE t.id = %s
    """, (id,))
    test_result = cursor.fetchone()
    cursor.close()

    if not test_result:
        print("Test result not found")
        return jsonify({"error": "Test result not found"}), 404

    return jsonify(test_result), 200

@app.route("/warnings/logs", methods=["GET"])
def get_logs():
    error, status_code = validate_session_cookie_edit(request)
    if error:
        print(f"Validation error: {error}")
        return jsonify(error), status_code

    connection = get_db_connection()
    if connection is None:
        print("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500

    # Retrieve all logs and group their variables/messages
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT la.id AS log_id, la.rule_id, la.time, r.name AS rule_name
        FROM rule_logs_activation la
        JOIN rule r ON la.rule_id = r.id
        ORDER BY la.time DESC
    """)
    logs_raw = cursor.fetchall()

    # Gather logs in a dict keyed by log_id
    logs_dict = {}
    for row in logs_raw:
        logs_dict[row["log_id"]] = {
            "id": row["rule_id"],
            "name": row["rule_name"],
            "timestamp": row["time"].isoformat() if row["time"] else None,
            "variables": {},
            "messages": []
        }

    # Collect variables
    log_ids = [str(log["log_id"]) for log in logs_raw]
    if log_ids:
        cursor.execute(f"""
            SELECT log_id, variable, value, upper_bound, lower_bound
            FROM rule_logs_variables
            WHERE log_id IN ({",".join(log_ids)})
        """)
        vars_raw = cursor.fetchall()
        for var in vars_raw:
            logs_dict[var["log_id"]]["variables"][var["variable"]] = {
                "value": var["value"],
                "upper_bound": var["upper_bound"],
                "lower_bound": var["lower_bound"]
            }

    # Collect messages (join them by rule id)
    rule_ids = [str(log["id"]) for log in logs_dict.values()]
    if rule_ids:
        cursor.execute(f"""
            SELECT rm.rule_id, rm.authority AS Authority, rm.title AS Title,
                   rm.location AS Location, rm.severity AS Severity, rm.summary AS Summary
            FROM rule_messages rm
            WHERE rm.rule_id IN ({",".join(rule_ids)})
        """)
        msgs_raw = cursor.fetchall()
        # Append each message to all logs referencing that rule
        for msg in msgs_raw:
            for log_id, log_data in logs_dict.items():
                if log_data["id"] == msg["rule_id"]:
                    log_data["messages"].append(msg)

    cursor.close()

    return jsonify(list(logs_dict.values())), 200

@app.route("/warnings/<int:id>/acknowledge", methods=["POST"])
def acknowledge_warning(id):
    error, status_code = validate_session_cookie_edit(request)
    if error:
        print(f"Validation error: {error}")
        return jsonify(error), status_code

    data = request.get_json()
    response_value = data.get("response")
    if response_value not in ["acknowledged", "denied", "ignored"]:
        print("Invalid response")
        return jsonify({"error": "Invalid response"}), 400

    # Get user info
    connection = get_db_connection()
    if connection is None:
        print("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT full_name FROM accounts.users WHERE user_id = %s", (status_code,))
    user_record = cursor.fetchone()
    cursor.close()

    # Publish to MQTT
    mqtt_broker = "mqtt.flespi.io"
    mqtt_port = 1883
    mqtt_topic = f"response/{id}"
    mqtt_token = os.getenv("mqtt_token")  # Replace with your actual MQTT token

    client = mqtt.Client(protocol=mqtt.MQTTv5)
    client.username_pw_set(mqtt_token, None)
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_start()

    payload = json.dumps({
        "response": response_value,
        "name": user_record["full_name"],
        "medium": "Web"
    })
    client.publish(mqtt_topic, payload)
    time.sleep(1)  # Sleep to ensure the message is sent
    client.loop_stop()
    client.disconnect()

    return jsonify({"message": "Response sent"}), 200

if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5004)