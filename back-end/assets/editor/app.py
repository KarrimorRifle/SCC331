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
    
    data = r.json()
    if data.get("authority") != "Admin":
        print("ERR: Non-admin cookie")
        return {"error": "Forbidden", "message": "User isn't a valid admin"}, 403

    # Return None if everything is valid (no error)
    return None

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

if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5011)