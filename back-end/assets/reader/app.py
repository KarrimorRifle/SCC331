from flask import Flask, request, jsonify, make_response
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error
from datetime import datetime
import os
import requests
import time

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

    print(f"Cookie found: {cookie}")
    r = requests.get(VALIDATION_SITE, headers={"session-id": cookie})
    if r.status_code != 200:
        print("ERR: Invalid cookie detected")
        return {"error": "Invalid cookie"}, 401 #, "message": r.text

    # Return None if everything is valid (no error)
    return None

@app.route('/presets', methods=['GET'])
def list_presets():
    cookie_error = validate_session_cookie(request)
    if cookie_error:
        return jsonify(cookie_error[0]), cookie_error[1]

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection unavailable"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Get default preset
        cursor.execute("SELECT preset_id FROM default_preset WHERE id = 1;")
        row = cursor.fetchone()
        default_id = row['preset_id'] if row else None

        # Get all presets
        cursor.execute("SELECT preset_id AS id, preset_name AS name FROM presets;")
        presets = cursor.fetchall()

        return jsonify({
            "default": default_id,
            "presets": presets
        }), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/presets/<int:preset_id>', methods=['GET'])
def get_preset_details(preset_id):
    cookie_error = validate_session_cookie(request)
    if cookie_error:
        return jsonify(cookie_error[0]), cookie_error[1]

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection unavailable"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch preset details
        cursor.execute("""
            SELECT preset_id AS id, preset_name AS name, file_id
            FROM presets
            WHERE preset_id = %s
        """, (preset_id,))
        preset_row = cursor.fetchone()
        if not preset_row:
            return jsonify({"error": "Preset not found"}), 404

        # Fetch trusted users
        cursor.execute("""
            SELECT user_id
            FROM preset_trusted
            WHERE preset_id = %s
        """, (preset_id,))
        trusted_rows = cursor.fetchall()
        trusted = [row['user_id'] for row in trusted_rows]

        # Fetch boxes
        cursor.execute("""
            SELECT
              id AS box_id, roomID, label,
              location_top AS top,
              location_left AS left,
              location_width AS width,
              location_height AS height,
              colour
            FROM map_blocks
            WHERE preset_id = %s
        """, (preset_id,))
        boxes = cursor.fetchall()

        # Fetch image from files (if you store one)
        cursor.execute("""
            SELECT filename AS name
            FROM files
            WHERE filename = %s
        """, (preset_row["file_id"],))
        image_row = cursor.fetchone()

        # Minimal representation of "permission"
        # In real usage, you'd check whether user is in preset_trusted or an admin
        permission = "read"

        return jsonify({
            "id": preset_row["id"],
            "name": preset_row["name"],
            "trusted": trusted,
            "boxes": boxes,
            "image": image_row if image_row else {},
            "permission": permission
        }), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5010)