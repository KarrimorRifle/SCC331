from flask import Flask, request, jsonify, make_response
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
import requests

app = Flask(__name__)

# Establish a persistent connection to the database
db_connection = None

def get_db_connection():
    global db_connection
    if db_connection is None or not db_connection.is_connected():
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

# Make A path per data type, and make sure the cookie is valid beither getting summary data

@app.route('/summary', methods=['GET'])
def summary():
    VALIDATION_SITE = "http://account_login:5002/validate_cookie"
    # Make sure the cookie is valid by sending a cookie auth check to accounts_login container at /authenticate_cookie
    r = requests.get(VALIDATION_SITE, headers={
        "session-id":request.cookies.get('session_id') 
    })
    if r.status_code != 200:
        print("ERR: Invalid cookie detected")
        return jsonify({"error": "Invalid cookie"}), 401

    connection = get_db_connection()
    
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500
    
    cursor = connection.cursor(dictionary=True)
    try:
        # Grab the latest from both luggage and user within two minutes
        query = """
        SELECT roomID, COUNT(*) as count
        FROM (
            SELECT picoID, roomID, logged_at FROM luggage
            WHERE logged_at >= NOW() - INTERVAL 2 MINUTE
            UNION ALL
            SELECT picoID, roomID, logged_at FROM users
            WHERE logged_at >= NOW() - INTERVAL 2 MINUTE
        ) AS combined
        GROUP BY roomID;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results)
    except Error as e:
        print(f"Error querying data: {e}")
        return jsonify({"error": "Error querying data"}), 500
    finally:
        cursor.close()
        connection.close()



if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5003)