from flask import Flask, request, jsonify, make_response
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error
import os
import requests
import time
import base64
import binascii

app = Flask(__name__)
CORS(app)

# Establish a persistent connection to the database
db_connection = None

def get_db_connection(retries=5, delay=1):
    global db_connection
    for _ in range(retries):
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
            time.sleep(delay)
    
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
    if data.get("authority") != "Admin":
        print("ERR: Non-admin cookie")
        return {"error": "Forbidden", "message": "User isn't a valid admin"}, 403
    
    return [data.get("uid")]

def validate_owner_cookie(request, owner):
    VALIDATION_SITE = "http://account_login:5002/validate_cookie"
    cookie = request.cookies.get("session_id")

    if not cookie:
        print("No session_id cookie found.")
        return {"error": "Invalid cookie", "message": "Cookie missing"}, 401

    print(f"Cookie found: {cookie}")
    r = requests.get(VALIDATION_SITE, headers={"session-id": cookie})
    if r.status_code != 200:
        print("ERR: Invalid cookie detected")
        return {"error": "Invalid cookie"}, 401 #, "message": r.text

    user_data = r.json()
    if user_data.get("uid") != owner:
        print("ERR: User isn't owner")
        return {"error":"Forbidden", "message":"Not the owner of this preset"}, 403

    # Return None if everything is valid (no error)
    return None

def validate_trusted_cookie(request, trustees):
    VALIDATION_SITE = "http://account_login:5002/validate_cookie"
    cookie = request.cookies.get("session_id")
    if not cookie:
        return {"error": "Invalid cookie", "message": "Cookie missing"}, 401

    r = requests.get(VALIDATION_SITE, headers={"session-id": cookie})
    if r.status_code != 200:
        return {"error": "Invalid cookie"}, 401

    user_data = r.json()
    if user_data.get("uid") not in trustees:
        return {"error": "Forbidden", "message": "You are not a trusted user"}, 403

    return None

@app.route('/presets', methods=['POST'])
def presets():
    cookie_res = validate_session_cookie(request)
    if len(cookie_res) == 2:
        return cookie_res[0], cookie_res[1]
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = connection.cursor(dictionary=True)
    data = request.get_json()

    try:
        # Insert the new preset
        cursor.execute("""
            INSERT INTO presets (preset_name, owner_id)
            VALUES (%s, %s)
            """, (data["name"], cookie_res[0]))
        
        preset_id = cursor.lastrowid

        # Add the trustees
        for user_id in data['trusted']:
            cursor.execute("""
                INSERT INTO preset_trusted (preset_id, user_id)
                VALUES (%s, %s)
            """, (preset_id, user_id))

        cursor.execute("""
                INSERT INTO preset_trusted (preset_id, user_id)
                VALUES (%s, %s)
            """, (preset_id, cookie_res[0]))

        connection.commit()
        return jsonify({"message": "Preset created", "preset_id": preset_id}), 201
    except Error as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/presets/default', methods=['PATCH'])
def set_default_preset():
    cookie_res = validate_session_cookie(request)
    if len(cookie_res) == 2:
        return cookie_res[0], cookie_res[1]
    
    connection = get_db_connection()
    if connection is None:
        print("ERR couldnt get a DB connection")
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = connection.cursor(dictionary=True)
    data = request.get_json()
    
    try:
        cursor.execute(
            "UPDATE default_preset SET preset_id = %s WHERE id = 1",
            (data["preset_id"],)
        )
        connection.commit()
        return jsonify({"message":"Preset updated successfully"}), 200
    except Error as e:
        print(f"ERR: Error encountered setting default preset: {str(e)}")
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/presets/<int:preset_id>/image', methods=['POST'])
def upload_preset_image(preset_id):
    cookie_res = validate_session_cookie(request)
    if len(cookie_res) == 2:
        return cookie_res[0], cookie_res[1]
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = connection.cursor(dictionary=True)
    data = request.get_json()

    # Validate base64 encoding
    try:
        base64.b64decode(data["data"], validate=True)
        print(data["data"])
    except (binascii.Error, KeyError):
        return jsonify({"error": "Image data is not valid base64"}), 400

    try:
        cursor.execute(
            "UPDATE presets SET image_name = %s, image_data = %s WHERE preset_id = %s",
            (data["name"], data["data"], preset_id)
        )
        connection.commit()
        return jsonify({"message": "Preset image updated"}), 200
    except Error as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/presets/<int:preset_id>/boxes', methods=['PATCH'])
def update_preset_boxes(preset_id):
    cookie_res = validate_session_cookie(request)
    if len(cookie_res) == 2:
        return cookie_res[0], cookie_res[1]
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = connection.cursor(dictionary=True)
    data = request.get_json()

    try:
        # Delete existing boxes (map_blocks) for this preset
        cursor.execute("DELETE FROM map_blocks WHERE preset_id = %s", (preset_id,))
        # Insert new boxes into map_blocks
        for box in data["boxes"]:
            cursor.execute("""
                INSERT INTO map_blocks 
                (preset_id, roomID, label, `top`, `left`, `width`, `heigth`, colour)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (preset_id, box["roomID"], box["label"], box["top"], box["left"], box["width"], box["height"], box["colour"]))
        connection.commit()
        return jsonify({"message": "Preset boxes updated"}), 200
    except Error as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/presets/<int:preset_id>', methods=['PATCH'])
def update_preset_name(preset_id):
    cookie_res = validate_session_cookie(request)
    if len(cookie_res) == 2:
        return cookie_res[0], cookie_res[1]
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = connection.cursor(dictionary=True)
    data = request.get_json()

    try:
        cursor.execute("UPDATE presets SET preset_name = %s WHERE preset_id = %s", (data["name"], preset_id))
        connection.commit()
        return jsonify({"message": "Preset name updated"}), 200
    except Error as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/presets/<int:preset_id>', methods=['DELETE'])
def delete_preset(preset_id):
    cookie_res = validate_session_cookie(request)
    if len(cookie_res) == 2:
        return cookie_res[0], cookie_res[1]
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT owner_id FROM presets WHERE preset_id = %s", (preset_id,))
    owner_id = cursor.fetchone()["owner_id"]
    if owner_id != cookie_res[0]:
        return jsonify({"error": "Forbidden", "message": "Not the owner of this preset"}), 403

    try:
        cursor.execute("DELETE FROM presets WHERE preset_id = %s", (preset_id,))
        cursor.execute("DELETE FROM preset_trusted WHERE preset_id = %s", (preset_id,))
        connection.commit()
        return jsonify({"message": "Preset deleted"}), 200
    except Error as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5011)