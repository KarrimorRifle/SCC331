from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import bcrypt
import uuid
from datetime import datetime
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Establish a persistent connection to the database
db_connection = None

def get_db_connection():
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
    return db_connection

@app.route('/login', methods=['POST'])
def login():
    email = str(request.headers.get('email').lower())
    password = str(request.headers.get('password'))

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT user_id, pass_hash FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['pass_hash'].encode('utf-8')):
        # Generate a new cookie
        new_cookie = str(uuid.uuid4())
        # Update last_login and cookie in the database
        cursor.execute("UPDATE users SET last_login = %s, cookie = %s WHERE user_id = %s", 
                       (datetime.now(), new_cookie, user['user_id']))
        connection.commit()
        cursor.close()

        # Create response with the new cookie
        response = make_response(jsonify({"message": "Login successful"}), 200)
        response.set_cookie("session_id", new_cookie, max_age=1*60*60)
        return response
    else:
        cursor.close()
        return jsonify({"error": "Invalid email or password"}), 401

@app.route('/validate_cookie', methods=['GET'])
def validate_cookie():
    session_id = request.headers.get('session-id') or request.cookies.get('session_id') 
    if not session_id:
        return jsonify({"error": "No session cookie or header provided"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT user_id, email, authority FROM users WHERE cookie = %s", (session_id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return jsonify({"message": "Cookie is valid", "valid": True, "email": user['email'], "uid": user['user_id'], "authority": user["authority"]}), 200
    else:
        return jsonify({"error": "Invalid cookie", "valid": False}), 401


if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5002)