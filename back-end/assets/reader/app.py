from flask import Flask, request, jsonify, make_response
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error
from datetime import datetime
import os
import requests
import time

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Establish a persistent connection to the database
db_connection = None

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

    # Return the UID if no error
    return [r.json().get("uid")]

@app.route('/presets', methods=['GET'])
def list_presets():
    cookie_error = validate_session_cookie(request)
    if len(cookie_error) == 2:
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
    if len(cookie_error) == 2:
        return jsonify(cookie_error[0]), cookie_error[1]

    conn = get_db_connection()
    if not conn:
        print("ERR: No DB connection retrieving data")
        return jsonify({"error": "DB connection unavailable"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch preset details including image columns from presets
        cursor.execute("""
            SELECT preset_id AS id, preset_name AS name, image_name, image_data, owner_id
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
        trusted = [row['user_id'] for row in cursor.fetchall()]

        # Fetch boxes from map_blocks
        cursor.execute("""
            SELECT
              roomID,
              label,
              `top`,
              `left`,
              `width`,
              `height`,
              colour
            FROM map_blocks
            WHERE preset_id = %s
        """, (preset_id,))
        boxes = cursor.fetchall()

        # Build image object from presets columns if present
        image = {}
        if preset_row.get("image_name") and preset_row.get("image_data"):
            print(preset_row["image_data"])
            image = {
                "name": preset_row["image_name"],
                "data": preset_row["image_data"].decode('utf-8')
            }

        # Minimal representation of "permission"
        if cookie_error[0] in trusted:
            permission = "write"
        else:
            permission = "read"

        return jsonify({
            "id": preset_row["id"],
            "name": preset_row["name"],
            "owner_id": preset_row["owner_id"],
            "trusted": trusted,
            "boxes": boxes,
            "image": image,
            "permission": permission
        }), 200

    except Error as e:
        print(f"ERR: Error encountered retrieving preset data: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/home', methods=['GET'])
def get_front_page():
    cookie_error = validate_session_cookie(request)
    if len(cookie_error) == 2:
        return jsonify(cookie_error[0]), cookie_error[1]
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection unavailable"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT domain, loginText, hero_title, hero_subtitle, image_name, image_data FROM config WHERE id=1")
        config_row = cursor.fetchone()
        # Changed code: decode image_data if present
        image_data = config_row.get("image_data")
        if image_data and isinstance(image_data, bytes):
            image_data = image_data.decode('utf-8')
        config = {
            "domain": config_row.get("domain"),
            "loginText": config_row.get("loginText"),
            "hero": {
                "title": config_row.get("hero_title"),
                "subtitle": config_row.get("hero_subtitle"),
                "image": {
                    "name": config_row.get("image_name"),
                    "data": image_data
                }
            }
        }
        cursor.execute("SELECT title, description, icon FROM features")
        features = cursor.fetchall()
        cursor.execute("SELECT * FROM how_it_works")
        howItWorks = cursor.fetchall()
        cursor.execute("""
            SELECT primaryDarkBg, primaryDarkText, primarySecondaryBg, primarySecondaryText, 
                   primaryLightBg, primaryLightText, accent, accentHover 
            FROM theme_colours WHERE id=1
        """)
        theme = cursor.fetchone()
        
        front_page = {
            "config": config,
            "features": features,
            "howItWorks": howItWorks,
            "theme": theme
        }
        return jsonify(front_page), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5010)