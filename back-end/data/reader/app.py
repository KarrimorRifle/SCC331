from flask import Flask, request, jsonify, make_response
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error
from datetime import datetime, timedelta
import os
import requests

app = Flask(__name__)
CORS(app, supports_credentials=True)

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

# make route for most recent pico session
@app.route('/pico/<string:PICO>', methods=['GET'])
def pico(PICO):
    cookie_validation_error = validate_session_cookie(request)
    if cookie_validation_error:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        # Check if a "time" attribute was passed in the JSON request body
        req_data = request.get_json(silent=True)
        provided_time = None
        if req_data and req_data.get("time"):
            provided_time = datetime.fromisoformat(req_data.get("time"))

        if provided_time:
            # Fetch all logs for PicoID in ascending order
            query = """
            SELECT roomID, logged_at, 'user' as pico_type FROM users WHERE PicoID = %s
            UNION ALL
            SELECT roomID, logged_at, 'luggage' as pico_type FROM luggage WHERE PicoID = %s
            UNION ALL
            SELECT roomID, logged_at, 'staff' as pico_type FROM staff WHERE PicoID = %s
            UNION ALL
            SELECT roomID, logged_at, 'guard' as pico_type FROM guard WHERE PicoID = %s
            ORDER BY logged_at ASC;
            """
            cursor.execute(query, (PICO, PICO, PICO, PICO))
            logs = cursor.fetchall()
            if not logs:
                return jsonify({"error": "No logs found for the specified Pico"}), 404

            # Convert logged_at to datetime objects if needed
            for row in logs:
                if not hasattr(row['logged_at'], 'isoformat'):
                    row['logged_at'] = datetime.strptime(row['logged_at'], "%Y-%m-%d %H:%M:%S")
            
            # Find the contiguous block containing the provided time.
            gap = timedelta(seconds=90)  # 1.5 minutes

            # Find the index where the provided_time fits
            idx = None
            for i, row in enumerate(logs):
                if row['logged_at'] >= provided_time:
                    idx = i
                    break
            if idx is None:
                idx = len(logs) - 1  # provided time later than all logs

            # Expand upward (later times)
            end_idx = idx
            while end_idx + 1 < len(logs):
                if logs[end_idx + 1]['logged_at'] - logs[end_idx]['logged_at'] <= gap:
                    end_idx += 1
                else:
                    break

            # Expand downward (earlier times)
            start_idx = idx
            while start_idx - 1 >= 0:
                if logs[start_idx]['logged_at'] - logs[start_idx - 1]['logged_at'] <= gap:
                    start_idx -= 1
                else:
                    break

            # Select contiguous block
            contiguous_logs = logs[start_idx:end_idx+1]
            movement = { row['logged_at'].isoformat(): row['roomID'] for row in contiguous_logs }
            pico_type = contiguous_logs[0]['pico_type'] if contiguous_logs else "unknown"
            print({"type": pico_type, "movement": movement})
            return jsonify({"type": pico_type, "movement": movement})
        else:
            # Fallback: use the old algorithm (using a 2-minute gap to pick session_start)
            query = """
            SELECT roomID, logged_at, pico_type FROM (
                SELECT roomID, logged_at, pico_type,
                       LAG(logged_at) OVER (ORDER BY logged_at) AS prev_log
                FROM (
                    SELECT roomID, logged_at, 'user' as pico_type FROM users WHERE PicoID = %s
                    UNION ALL
                    SELECT roomID, logged_at, 'luggage' FROM luggage WHERE PicoID = %s
                    UNION ALL
                    SELECT roomID, logged_at, 'staff' FROM staff WHERE PicoID = %s
                    UNION ALL
                    SELECT roomID, logged_at, 'guard' FROM guard WHERE PicoID = %s
                ) AS combined
                ORDER BY logged_at DESC
            ) AS ordered_logs
            WHERE TIMESTAMPDIFF(MINUTE, prev_log, logged_at) >= 2 OR prev_log IS NULL
            ORDER BY logged_at DESC
            LIMIT 1;
            """
            cursor.execute(query, (PICO, PICO, PICO, PICO))
            session_start = cursor.fetchone()
            if not session_start:
                return jsonify({"error": "No session found for the specified Pico"}), 404

            pico_type = session_start['pico_type']
            query = """
            SELECT roomID, logged_at FROM (
                SELECT roomID, logged_at, pico_type,
                       LAG(logged_at) OVER (ORDER BY logged_at) AS prev_log
                FROM (
                    SELECT roomID, logged_at, 'user' as pico_type FROM users WHERE PicoID = %s
                    UNION ALL
                    SELECT roomID, logged_at, 'luggage' FROM luggage WHERE PicoID = %s
                    UNION ALL
                    SELECT roomID, logged_at, 'staff' FROM staff WHERE PicoID = %s
                    UNION ALL
                    SELECT roomID, logged_at, 'guard' FROM guard WHERE PicoID = %s
                ) AS combined
                ORDER BY logged_at DESC
            ) AS ordered_logs
            WHERE logged_at >= %s
            ORDER BY logged_at;
            """
            cursor.execute(query, (PICO, PICO, PICO, PICO, session_start['logged_at']))
            session_logs = cursor.fetchall()
            for row in session_logs:
                if not hasattr(row['logged_at'], 'isoformat'):
                    row['logged_at'] = datetime.strptime(row['logged_at'], "%Y-%m-%d %H:%M:%S")
            movement = { row['logged_at'].isoformat(): row['roomID'] for row in session_logs }
            print({"type": pico_type, "movement": movement})
            return jsonify({"type": pico_type, "movement": movement})
    except Error as e:
        print(f"Error querying data: {e}")
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/summary', methods=['GET'])
def summary():
    cookie_validation_error = validate_session_cookie(request)
    if cookie_validation_error:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]

    connection = get_db_connection()
    
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500
    
    cursor = connection.cursor(dictionary=True)
    try:
        # Query for users
        query_users = """
        SELECT roomID, PicoID, logged_at as latest_log
        FROM users
        WHERE (PicoID, logged_at) IN (
            SELECT PicoID, MAX(logged_at)
            FROM users
            WHERE logged_at >= NOW() - INTERVAL 2 MINUTE
            GROUP BY PicoID
        );
        """
        cursor.execute(query_users)
        users_results = cursor.fetchall()

        # Query for luggage
        query_luggage = """
        SELECT roomID, PicoID, logged_at as latest_log
        FROM luggage
        WHERE (PicoID, logged_at) IN (
            SELECT PicoID, MAX(logged_at)
            FROM luggage
            WHERE logged_at >= NOW() - INTERVAL 2 MINUTE
            GROUP BY PicoID
        );
        """
        cursor.execute(query_luggage)
        luggage_results = cursor.fetchall()

        # Query for staff
        query_staff = """
        SELECT roomID, PicoID, logged_at as latest_log
        FROM staff
        WHERE (PicoID, logged_at) IN (
            SELECT PicoID, MAX(logged_at)
            FROM staff
            WHERE logged_at >= NOW() - INTERVAL 2 MINUTE
            GROUP BY PicoID
        );
        """
        cursor.execute(query_staff)
        staff_results = cursor.fetchall()

        # Query for guard
        query_guard = """
        SELECT roomID, PicoID, logged_at as latest_log
        FROM guard
        WHERE (PicoID, logged_at) IN (
            SELECT PicoID, MAX(logged_at)
            FROM guard
            WHERE logged_at >= NOW() - INTERVAL 2 MINUTE
            GROUP BY PicoID
        );
        """
        cursor.execute(query_guard)
        guard_results = cursor.fetchall()

        # Query for environment
        query_environment = """
        SELECT e.roomID, e.logged_at, e.temperature, e.sound, e.light, e.IAQ, e.pressure, e.humidity
        FROM environment e
        INNER JOIN (
            SELECT roomID, MAX(logged_at) as latest_log
            FROM environment
            WHERE logged_at >= NOW() - INTERVAL 2 MINUTE
            GROUP BY roomID
        ) latest ON e.roomID = latest.roomID AND e.logged_at = latest.latest_log;
        """
        cursor.execute(query_environment)
        environment_results = cursor.fetchall()

        # Combine results
        summary = {}
        for row in users_results:
            room_id = row['roomID']
            pico_id = row['PicoID']
            if room_id not in summary:
                summary[room_id] = {
                    "users": {"count": 0, "id": []},
                    "luggage": {"count": 0, "id": []},
                    "staff": {"count": 0, "id": []},
                    "guard": {"count": 0, "id": []},
                    "environment": {}
                }
            summary[room_id]['users']['count'] += 1
            summary[room_id]['users']['id'].append(pico_id)

        for row in luggage_results:
            room_id = row['roomID']
            pico_id = row['PicoID']
            if room_id not in summary:
                summary[room_id] = {
                    "users": {"count": 0, "id": []},
                    "luggage": {"count": 0, "id": []},
                    "staff": {"count": 0, "id": []},
                    "guard": {"count": 0, "id": []},
                    "environment": {}
                }
            summary[room_id]['luggage']['count'] += 1
            summary[room_id]['luggage']['id'].append(pico_id)

        for row in staff_results:
            room_id = row['roomID']
            pico_id = row['PicoID']
            if room_id not in summary:
                summary[room_id] = {
                    "users": {"count": 0, "id": []},
                    "luggage": {"count": 0, "id": []},
                    "staff": {"count": 0, "id": []},
                    "guard": {"count": 0, "id": []},
                    "environment": {}
                }
            summary[room_id]['staff']['count'] += 1
            summary[room_id]['staff']['id'].append(pico_id)

        for row in guard_results:
            room_id = row['roomID']
            pico_id = row['PicoID']
            if room_id not in summary:
                summary[room_id] = {
                    "users": {"count": 0, "id": []},
                    "luggage": {"count": 0, "id": []},
                    "staff": {"count": 0, "id": []},
                    "guard": {"count": 0, "id": []},
                    "environment": {}
                }
            summary[room_id]['guard']['count'] += 1
            summary[room_id]['guard']['id'].append(pico_id)

        for row in environment_results:
            room_id = row['roomID']
            if room_id not in summary:
                summary[room_id] = {
                    "users": {"count": 0, "id": []},
                    "luggage": {"count": 0, "id": []},
                    "staff": {"count": 0, "id": []},
                    "guard": {"count": 0, "id": []},
                    "environment": {}
                }
            summary[room_id]['environment'] = {
                "temperature": row['temperature'],
                "sound": row['sound'],
                "light": row['light'],
                "IAQ": row['IAQ'],
                "pressure": row['pressure'],
                "humidity": row['humidity']
            }

        return jsonify(summary)
    except Error as e:
        print(f"Error querying data: {e}")
        return jsonify({"error": "Error querying data", "message": f"{e}"}), 500
    finally:
        cursor.close()
        connection.close()



if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5003)