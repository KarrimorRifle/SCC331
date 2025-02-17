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
    
    data = r.get_json()
    if data.get("authority") != "Admin":
        return {"error": "Unauthorized access", "message": "you don't have sufficient permission to access this resource"}, 401

    # Return None if everything is valid (no error)
    return None


@app.route("/warnings", methods=["GET"])
def grab_warning():
    error = validate_session_cookie_edit(request)
    if error:
        return error
    data = request.get_json()
    authority = data.get("authority")
    print(f"Authority: {authority}")
    return jsonify({"authority": authority}), 200


if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5004)