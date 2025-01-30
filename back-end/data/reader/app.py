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

# Make route for finding the picos in each room currently

# make route for most recent pico session
@app.route('/pico/<int:PICO>', methods=['GET'])
def pico(PICO):
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
        # Query to get the most recent session for the specified PicoID
        query = """
        SELECT roomID, logged_at
        FROM (
            SELECT roomID, logged_at,
                    LAG(logged_at) OVER (ORDER BY logged_at) AS prev_log
            FROM (
                SELECT roomID, logged_at
                FROM (
                    SELECT roomID, logged_at FROM users WHERE PicoID = %s
                    UNION ALL
                    SELECT roomID, logged_at FROM luggage WHERE PicoID = %s
                ) AS combined
                ORDER BY logged_at DESC
            ) AS ordered_logs
        ) AS session_logs
        WHERE TIMESTAMPDIFF(MINUTE, prev_log, logged_at) >= 2 OR prev_log IS NULL
        ORDER BY logged_at DESC
        LIMIT 1;
        """
        cursor.execute(query, (PICO, PICO))
        session_start = cursor.fetchone()

        if not session_start:
            return jsonify({"error": "No session found for the specified PicoID"}), 404

        # Query to get all logs for the most recent session
        query = """
        SELECT roomID, logged_at
        FROM (
            SELECT roomID, logged_at,
                    LAG(logged_at) OVER (ORDER BY logged_at) AS prev_log
            FROM (
                SELECT roomID, logged_at
                FROM (
                    SELECT roomID, logged_at FROM users WHERE PicoID = %s
                    UNION ALL
                    SELECT roomID, logged_at FROM luggage WHERE PicoID = %s
                ) AS combined
                ORDER BY logged_at DESC
            ) AS ordered_logs
        ) AS session_logs
        WHERE logged_at >= %s
        ORDER BY logged_at;
        """
        cursor.execute(query, (PICO, PICO, session_start['logged_at']))
        session_logs = cursor.fetchall()

        return jsonify(session_logs)
    except Error as e:
        print(f"Error querying data: {e}")
        return jsonify({"error": "Error querying data"}), 500
    finally:
        cursor.close()
        connection.close()


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
        # Query for users
        query_users = """
        SELECT roomID, PicoID, MAX(logged_at) as latest_log
        FROM users
        WHERE logged_at >= NOW() - INTERVAL 2 MINUTE
        GROUP BY roomID, PicoID;
        """
        cursor.execute(query_users)
        users_results = cursor.fetchall()

        # Query for luggage
        query_luggage = """
        SELECT roomID, PicoID, MAX(logged_at) as latest_log
        FROM luggage
        WHERE logged_at >= NOW() - INTERVAL 2 MINUTE
        GROUP BY roomID, PicoID;
        """
        cursor.execute(query_luggage)
        luggage_results = cursor.fetchall()

        # Query for environment
        query_environment = """
        SELECT roomID, MAX(logged_at) as latest_log, temperature, sound, light
        FROM environment
        WHERE logged_at >= NOW() - INTERVAL 2 MINUTE
        GROUP BY roomID;
        """
        cursor.execute(query_environment)
        environment_results = cursor.fetchall()

        # Combine results
        summary = {}
        for row in users_results:
            room_id = row['roomID']
            pico_id = row['PicoID']
            if room_id not in summary:
                summary[room_id] = {"users": {"count": 0, "id": []}, "luggage": {"count": 0, "id": []}, "environment": {}}
            summary[room_id]['users']['count'] += 1
            summary[room_id]['users']['id'].append(pico_id)

        for row in luggage_results:
            room_id = row['roomID']
            pico_id = row['PicoID']
            if room_id not in summary:
                summary[room_id] = {"users": {"count": 0, "id": []}, "luggage": {"count": 0, "id": []}, "environment": {}}
            summary[room_id]['luggage']['count'] += 1
            summary[room_id]['luggage']['id'].append(pico_id)

        for row in environment_results:
            room_id = row['roomID']
            if room_id not in summary:
                summary[room_id] = {"users": {"count": 0, "id": []}, "luggage": {"count": 0, "id": []}, "environment": {}}
            summary[room_id]['environment'] = {
                "temperature": row['temperature'],
                "sound": row['sound'],
                "light": row['light']
            }

        return jsonify(summary)
    except Error as e:
        print(f"Error querying data: {e}")
        return jsonify({"error": "Error querying data"}), 500
    finally:
        cursor.close()
        connection.close()



if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5003)