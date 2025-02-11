from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import bcrypt
import os
import time

app = Flask(__name__)

CORS(app, supports_credentials=True)

# Establish a persistent connection to the database
db_connection = None

def get_db_connection():
    global db_connection
    if db_connection is None or not db_connection.is_connected():
        while True:
            try:
                db_connection = mysql.connector.connect(
                    host=os.getenv('DB_HOST'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD'),
                    database=os.getenv('DB_NAME')
                )
                if db_connection.is_connected():
                    break
            except Error as e:
                print(f"Error connecting to MySQL: {e}")
                time.sleep(5)  # Wait for 5 seconds before retrying
    return db_connection

@app.route('/register', methods=['POST'])
def register():
    full_name = str(request.headers.get('name', ''))
    email = str(request.headers.get('email', '')).lower()
    password = str(request.headers.get('password', ''))
    bypass = str(request.headers.get('bypass', ''))

    if not full_name:
        return jsonify({"error": "Full name is required"}), 400

    if not email:
        return jsonify({"error": "Email is required"}), 400

    if not password:
        return jsonify({"error": "Password is required"}), 400

    if not email.endswith('@fakecompany.co.uk'):
        return jsonify({"error": "Email must end with '@fakecompany.co.uk'"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    authority = "Admin" if bypass == "yes" else "Reception"
    try:
        cursor.execute("INSERT INTO users (full_name, email, pass_hash, authority) VALUES (%s, %s, %s, %s)", 
                       (full_name, email, hashed_password, authority))
        connection.commit()
        cursor.close()
        return jsonify({"message": "User registered successfully"}), 201
    except Error as e:
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
# Should add a queue that needs admin approval to this

if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5001)