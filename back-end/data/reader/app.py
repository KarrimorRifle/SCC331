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

import re

def parse_period(period_str):
    """
    Parse a period string (e.g., "5min", "1hr", "1hr5min") and return the total seconds.
    The minimum allowed period is 60 seconds and the maximum is 604800 seconds (1 week).
    """
    period_str = period_str.strip().lower()
    # Pattern: optional hours followed by optional minutes. At least one must be provided.
    pattern = re.compile(r"(?:(\d+)\s*hr)?\s*(?:(\d+)\s*min)?")
    m = pattern.fullmatch(period_str)
    if not m or (not m.group(1) and not m.group(2)):
        raise ValueError("Invalid period format")
    hours = int(m.group(1)) if m.group(1) else 0
    minutes = int(m.group(2)) if m.group(2) else 0
    total_seconds = hours * 3600 + minutes * 60
    if total_seconds < 60:
        raise ValueError("Minimum grouping period is 1 minute")
    if total_seconds > 604800:
        raise ValueError("Maximum grouping period is 1 week")
    return total_seconds

@app.route('/summary/average', methods=['GET'])
def summary_average():
    # Validate session cookie
    cookie_validation_error = validate_session_cookie(request)
    if cookie_validation_error:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]

    req_data = request.get_json(silent=True) or {}
    
    if req_data:
        if "start_time" in req_data and not req_data["start_time"].strip():
            return jsonify({"error": "Missing or invalid parameters: start_time is empty"}), 400
        if "rooms" in req_data and isinstance(req_data["rooms"], list) and len(req_data["rooms"]) == 0:
            return jsonify({"error": "Missing or invalid parameters: rooms list is empty"}), 400

    now = datetime.utcnow()
    start_time_str = req_data.get("start_time")
    end_time_str = req_data.get("end_time")
    period_str = req_data.get("time_periods", "1hr")
    rooms = req_data.get("rooms")

    try:
        period_seconds = parse_period(period_str)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    if not start_time_str:
        start_dt = now - timedelta(hours=24)
    else:
        try:
            start_dt = datetime.fromisoformat(start_time_str.replace("Z", ""))
        except ValueError:
            return jsonify({"error": "Invalid start_time format"}), 400

    if not end_time_str:
        end_dt = now
    else:
        try:
            end_dt = datetime.fromisoformat(end_time_str.replace("Z", ""))
        except ValueError:
            return jsonify({"error": "Invalid end_time format"}), 400

    if start_dt >= end_dt:
        return jsonify({"error": "Invalid request parameters: start_time must be before end_time"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        # Flexible grouping using period_seconds
        env_query = f"""
        SELECT 
            roomID,
            FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(logged_at)/%s)*%s) as bucket,
            AVG(temperature) as avg_temperature, MAX(temperature) as peak_temperature, MIN(temperature) as trough_temperature,
            AVG(sound) as avg_sound, MAX(sound) as peak_sound, MIN(sound) as trough_sound,
            AVG(light) as avg_light, MAX(light) as peak_light, MIN(light) as trough_light,
            AVG(IAQ) as avg_IAQ, MAX(IAQ) as peak_IAQ, MIN(IAQ) as trough_IAQ,
            AVG(pressure) as avg_pressure, MAX(pressure) as peak_pressure, MIN(pressure) as trough_pressure,
            AVG(humidity) as avg_humidity, MAX(humidity) as peak_humidity, MIN(humidity) as trough_humidity
        FROM environment
        WHERE logged_at BETWEEN %s AND %s
        """
        params = [period_seconds, period_seconds, start_dt, end_dt]
        if rooms:
            env_query += " AND roomID IN (" + ",".join(["%s"] * len(rooms)) + ")"
            params.extend(rooms)
        env_query += " GROUP BY roomID, bucket ORDER BY bucket ASC;"
        cursor.execute(env_query, params)
        env_results = cursor.fetchall()

        average_summary = {}
        for row in env_results:
            # Convert bucket to ISO string if it is a datetime
            bucket = row['bucket']
            if isinstance(bucket, datetime):
                bucket = bucket.isoformat() + "Z"
            else:
                bucket = str(bucket)
            room_id = str(row['roomID'])
            if bucket not in average_summary:
                average_summary[bucket] = {}
            average_summary[bucket][room_id] = {
                "temperature": {"average": row["avg_temperature"], "peak": row["peak_temperature"], "trough": row["trough_temperature"]},
                "sound": {"average": row["avg_sound"], "peak": row["peak_sound"], "trough": row["trough_sound"]},
                "light": {"average": row["avg_light"], "peak": row["peak_light"], "trough": row["trough_light"]},
                "IAQ": {"average": row["avg_IAQ"], "peak": row["peak_IAQ"], "trough": row["trough_IAQ"]},
                "pressure": {"average": row["avg_pressure"], "peak": row["peak_pressure"], "trough": row["trough_pressure"]},
                "humidity": {"average": row["avg_humidity"], "peak": row["peak_humidity"], "trough": row["trough_humidity"]}
            }

        occupancy_types = ["users", "luggage", "staff", "guard"]
        for occ in occupancy_types:
            occ_query = f"""
            SELECT 
                roomID,
                FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(logged_at)/%s)*%s) as bucket,
                COUNT(*) as occ_count
            FROM {occ}
            WHERE logged_at BETWEEN %s AND %s
            """
            occ_params = [period_seconds, period_seconds, start_dt, end_dt]
            if rooms:
                occ_query += " AND roomID IN (" + ",".join(["%s"] * len(rooms)) + ")"
                occ_params.extend(rooms)
            occ_query += " GROUP BY roomID, bucket ORDER BY bucket ASC;"
            cursor.execute(occ_query, occ_params)
            occ_results = cursor.fetchall()
            for row in occ_results:
                bucket = row['bucket']
                if isinstance(bucket, datetime):
                    bucket = bucket.isoformat() + "Z"
                else:
                    bucket = str(bucket)
                room_id = str(row['roomID'])
                if bucket not in average_summary:
                    average_summary[bucket] = {}
                if room_id not in average_summary[bucket]:
                    average_summary[bucket][room_id] = {}
                count = row["occ_count"]
                average_summary[bucket][room_id][occ] = {
                    "average": count,
                    "peak": count,
                    "trough": count
                }
        return jsonify(average_summary)
    except Error as e:
        print(f"Error querying data: {e}")
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5003)