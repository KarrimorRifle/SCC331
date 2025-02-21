from flask import Flask, request, jsonify, make_response
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error
from datetime import datetime, timedelta
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
    
    print("Failed to establish database connection after retries")
    return None

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
    # Validate session cookie.
    cookie_validation_error = validate_session_cookie(request)
    if cookie_validation_error:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]

    # Read query parameters from URL.
    # Using request.args since these are GET parameters.
    time_str = request.args.get("time")
    mode = request.args.get("mode", "all")
    if mode not in ("all", "picos", "environment"):
        return jsonify({"error": "Invalid mode parameter"}), 400

    # Set snapshot_time: use provided time if valid, otherwise current UTC time.
    now = datetime.utcnow()
    if time_str:
        try:
            snapshot_time = datetime.fromisoformat(time_str.replace("Z", ""))
        except ValueError:
            return jsonify({"error": "Invalid time format"}), 400
    else:
        snapshot_time = now

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500

    cursor = connection.cursor(dictionary=True)
    summary = {}
    try:
        # Occupancy Data: only if mode is "all" or "picos"
        if mode in ("all", "picos"):
            # Define occupancy types in priority order.
            occupancy_types = ["users", "luggage", "staff", "guard"]
            # Global set to track PicoIDs already added (across all occupancy types)
            tracked_picos = set()
            for occ in occupancy_types:
                occ_query = f"""
                SELECT t.roomID, t.PicoID
                FROM {occ} t
                JOIN (
                    SELECT PicoID, MAX(logged_at) AS max_time
                    FROM {occ}
                    WHERE logged_at <= %s AND logged_at >= (%s - INTERVAL 1 MINUTE)
                    GROUP BY PicoID
                ) latest ON t.PicoID = latest.PicoID AND t.logged_at = latest.max_time;
                """
                cursor.execute(occ_query, (snapshot_time, snapshot_time))
                results = cursor.fetchall()
                for row in results:
                    pico_id = str(row["PicoID"])
                    # Only add this PicoID if it hasn't been seen already.
                    if pico_id in tracked_picos:
                        continue
                    room_id = str(row["roomID"])
                    if room_id not in summary:
                        summary[room_id] = {
                            "users": {"count": 0, "id": []},
                            "luggage": {"count": 0, "id": []},
                            "staff": {"count": 0, "id": []},
                            "guard": {"count": 0, "id": []},
                            "environment": {}
                        }
                    summary[room_id][occ]["id"].append(pico_id)
                    summary[room_id][occ]["count"] += 1
                    tracked_picos.add(pico_id)

        # Environment Data: only if mode is "all" or "environment"
        if mode in ("all", "environment"):
            # Query only records with logged_at in the last minute relative to snapshot_time.
            env_query = """
            SELECT e.roomID, e.temperature, e.sound, e.light, e.IAQ, e.pressure, e.humidity
            FROM environment e
            JOIN (
                SELECT roomID, MAX(logged_at) AS max_time
                FROM environment
                WHERE logged_at BETWEEN (%s - INTERVAL 1 MINUTE) AND %s
                GROUP BY roomID
            ) latest ON e.roomID = latest.roomID AND e.logged_at = latest.max_time;
            """
            cursor.execute(env_query, (snapshot_time, snapshot_time))
            env_results = cursor.fetchall()
            for row in env_results:
                room_id = str(row["roomID"])
                if room_id not in summary:
                    summary[room_id] = {
                        "users": {"count": 0, "id": []},
                        "luggage": {"count": 0, "id": []},
                        "staff": {"count": 0, "id": []},
                        "guard": {"count": 0, "id": []},
                        "environment": {}
                    }
                summary[room_id]["environment"] = {
                    "temperature": row["temperature"],
                    "sound": row["sound"],
                    "light": row["light"],
                    "IAQ": row["IAQ"],
                    "pressure": row["pressure"],
                    "humidity": row["humidity"]
                }
        return jsonify(summary)
    except Error as e:
        print(f"Error querying data: {e}")
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
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
    rooms = req_data.get("rooms")  # Optional room filter

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
        average_summary = {}

        # Updated Environment Query:
        # Map roomID '694904231' to '3' (adjust or extend this mapping as needed).
        env_query = f"""
        SELECT 
            CASE WHEN roomID = '694904231' THEN '3' ELSE roomID END as roomID,
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

        # Process environment results.
        for row in env_results:
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
            average_summary[bucket][room_id]["temperature"] = {
                "average": row["avg_temperature"], "peak": row["peak_temperature"], "trough": row["trough_temperature"]
            }
            average_summary[bucket][room_id]["sound"] = {
                "average": row["avg_sound"], "peak": row["peak_sound"], "trough": row["trough_sound"]
            }
            average_summary[bucket][room_id]["light"] = {
                "average": row["avg_light"], "peak": row["peak_light"], "trough": row["trough_light"]
            }
            average_summary[bucket][room_id]["IAQ"] = {
                "average": row["avg_IAQ"], "peak": row["peak_IAQ"], "trough": row["trough_IAQ"]
            }
            average_summary[bucket][room_id]["pressure"] = {
                "average": row["avg_pressure"], "peak": row["peak_pressure"], "trough": row["trough_pressure"]
            }
            average_summary[bucket][room_id]["humidity"] = {
                "average": row["avg_humidity"], "peak": row["peak_humidity"], "trough": row["trough_humidity"]
            }

        # Query occupancy data.
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
                count = row["occ_count"]
                if bucket not in average_summary:
                    average_summary[bucket] = {}
                if room_id not in average_summary[bucket]:
                    # Initialize environment metrics to zeros.
                    average_summary[bucket][room_id] = {
                        "temperature": {"average": 0, "peak": 0, "trough": 0},
                        "sound": {"average": 0, "peak": 0, "trough": 0},
                        "light": {"average": 0, "peak": 0, "trough": 0},
                        "IAQ": {"average": 0, "peak": 0, "trough": 0},
                        "pressure": {"average": 0, "peak": 0, "trough": 0},
                        "humidity": {"average": 0, "peak": 0, "trough": 0}
                    }
                average_summary[bucket][room_id][occ] = {
                    "average": count,
                    "peak": count,
                    "trough": count
                }
        
        # Ensure that for each bucket and each room, every occupancy type and environment metric is present.
        default_occ = {"average": 0, "peak": 0, "trough": 0}
        default_env = {"average": 0, "peak": 0, "trough": 0}
        env_keys = ["temperature", "sound", "light", "IAQ", "pressure", "humidity"]
        for bucket in average_summary:
            for room in average_summary[bucket]:
                for occ in occupancy_types:
                    if occ not in average_summary[bucket][room]:
                        average_summary[bucket][room][occ] = default_occ.copy()
                for key in env_keys:
                    if key not in average_summary[bucket][room]:
                        average_summary[bucket][room][key] = default_env.copy()
        
        return jsonify(average_summary)
    except Error as e:
        print(f"Error querying data: {e}")
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/movement', methods=['GET'])
def movement():
    # Validate session cookie.
    cookie_validation_error = validate_session_cookie(request)
    if cookie_validation_error:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]
    
    # Get time_start and time_end from query parameters; default to past 24 hours.
    time_start_str = request.args.get("time_start")
    time_end_str = request.args.get("time_end")
    now = datetime.utcnow()
    if time_start_str:
        try:
            time_start = datetime.fromisoformat(time_start_str.replace("Z", ""))
        except ValueError:
            return jsonify({"error": "Invalid time_start format"}), 400
    else:
        time_start = now - timedelta(hours=24)
    if time_end_str:
        try:
            time_end = datetime.fromisoformat(time_end_str.replace("Z", ""))
        except ValueError:
            return jsonify({"error": "Invalid time_end format"}), 400
    else:
        time_end = now

    if time_start >= time_end:
        return jsonify({"error": "time_start must be before time_end"}), 400

    # Round start and end off to the minute.
    time_start = time_start.replace(second=0, microsecond=0)
    time_end = time_end.replace(second=0, microsecond=0)

    # Build a list of minute buckets (inclusive).
    buckets = []
    current_bucket = time_start
    while current_bucket <= time_end:
        buckets.append(current_bucket)
        current_bucket += timedelta(minutes=1)

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500

    cursor = connection.cursor(dictionary=True)
    movement_summary = {}
    try:
        # For each minute bucket, query the occupancy data.
        for bucket in buckets:
            bucket_end = bucket + timedelta(minutes=1)
            # Use a JOIN to select only the latest record per PicoID in this bucket.
            query = """
            SELECT c.roomID, c.PicoID, c.type, c.logged_at as latest_log,
                   DATE_FORMAT(c.logged_at, '%%Y-%%m-%%dT%%H:%%i:00Z') as bucket
            FROM (
                SELECT roomID, logged_at, PicoID, 'User' as type
                FROM users
                WHERE logged_at >= %s AND logged_at < %s
                UNION ALL
                SELECT roomID, logged_at, PicoID, 'Luggage' as type
                FROM luggage
                WHERE logged_at >= %s AND logged_at < %s
                UNION ALL
                SELECT roomID, logged_at, PicoID, 'Staff' as type
                FROM staff
                WHERE logged_at >= %s AND logged_at < %s
                UNION ALL
                SELECT roomID, logged_at, PicoID, 'Guard' as type
                FROM guard
                WHERE logged_at >= %s AND logged_at < %s
            ) AS c
            JOIN (
                SELECT PicoID, MAX(logged_at) as max_time
                FROM (
                    SELECT PicoID, logged_at FROM users WHERE logged_at >= %s AND logged_at < %s
                    UNION ALL
                    SELECT PicoID, logged_at FROM luggage WHERE logged_at >= %s AND logged_at < %s
                    UNION ALL
                    SELECT PicoID, logged_at FROM staff WHERE logged_at >= %s AND logged_at < %s
                    UNION ALL
                    SELECT PicoID, logged_at FROM guard WHERE logged_at >= %s AND logged_at < %s
                ) AS all_logs
                GROUP BY PicoID
            ) AS sub ON c.PicoID = sub.PicoID AND c.logged_at = sub.max_time
            ORDER BY c.logged_at DESC;
            """
            # We need to pass bucket and bucket_end for each occurrence.
            params = [bucket, bucket_end, bucket, bucket_end, bucket, bucket_end, bucket, bucket_end,
                      bucket, bucket_end, bucket, bucket_end, bucket, bucket_end, bucket, bucket_end]
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            if results:
                # Group results by room.
                bucket_data = {}
                for row in results:
                    room_id = str(row['roomID'])
                    pico_id = str(row['PicoID'])
                    pico_type = row['type']
                    if room_id not in bucket_data:
                        bucket_data[room_id] = {}
                    bucket_data[room_id][pico_id] = pico_type
                bucket_key = bucket.isoformat() + "Z"
                movement_summary[bucket_key] = bucket_data

        return jsonify(movement_summary)
    except Error as e:
        print(f"Error querying movement data: {e}")
        return jsonify({"error": "Error querying movement data", "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    get_db_connection()  # Ensure the connection is established at startup
    app.run(host='0.0.0.0', port=5003)