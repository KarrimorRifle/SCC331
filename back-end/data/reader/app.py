from flask import Flask, request, jsonify, make_response
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error, pooling  # add this import
from datetime import datetime, timedelta
import os
import requests
import time
import re

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Create a connection pool at startup with an appropriate pool size; adjust parameters as needed.
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,  # set pool size based on load
    pool_reset_session=True,
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

def get_db_connection():
    try:
        return connection_pool.get_connection()
    except Error as e:
        print(f"Error getting connection from pool: {e}")
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

# -------------------------------
# Helper Functions for Type Mapping
# -------------------------------
def get_tracker_type(picoID):
    """
    Returns the old-style device type (singular) based on picoID.
    """
    if picoID.startswith("PICO-USER"):
        return "user"
    elif picoID.startswith("PICO-LUGGAGE"):
        return "luggage"
    elif picoID.startswith("PICO-STAFF"):
        return "staff"
    elif picoID.startswith("PICO-SECURITY"):
        return "guard"
    else:
        return "unknown"

def map_tracker_type(picoID):
    """
    Returns the old-style type in plural form for summary aggregation.
    """
    t = get_tracker_type(picoID)
    if t == "user":
        return "users"
    elif t == "luggage":
        return "luggage"
    elif t == "staff":
        return "staff"
    elif t == "guard":
        return "guard"
    else:
        return "unknown"

# -------------------------------
# Helper for /summary/average: Initialize a room structure.
# -------------------------------
def init_average_room():
    def occ_obj():
        return {"average": 0, "peak": 0, "trough": 0}
    return {
        "users": occ_obj(),
        "luggage": occ_obj(),
        "staff": occ_obj(),
        "guard": occ_obj(),
        "temperature": occ_obj(),
        "sound": occ_obj(),
        "light": occ_obj(),
        "IAQ": occ_obj(),
        "pressure": occ_obj(),
        "humidity": occ_obj()
    }

# -------------------------------
# /pico Endpoint
# -------------------------------
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
        # Lookup device info
        cursor.execute("SELECT picoType, readablePicoID FROM pico_device WHERE picoID = %s", (PICO,))
        device = cursor.fetchone()
        if not device:
            return jsonify({"error": "Pico device not found"}), 404

        picoType = device['picoType']
        if picoType == 2:
            data_table = "bluetooth_tracker_data"
            device_label = get_tracker_type(PICO)
        elif picoType == 1:
            data_table = "environment_sensor_data"
            device_label = "environment"
        else:
            return jsonify({"error": "Pico device not activated or unknown type"}), 400

        req_data = request.get_json(silent=True)
        provided_time = None
        if req_data and req_data.get("time"):
            provided_time = datetime.fromisoformat(req_data.get("time"))

        if provided_time:
            query = f"""
                SELECT roomID, logged_at
                FROM {data_table}
                WHERE picoID = %s AND logged_at >= %s
                ORDER BY logged_at ASC;
            """
            cursor.execute(query, (PICO, provided_time))
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
            while end_idx + 1 < len(logs) and logs[end_idx + 1]['logged_at'] - logs[end_idx]['logged_at'] <= gap:
                end_idx += 1
            start_idx = idx
            while start_idx - 1 >= 0 and logs[start_idx]['logged_at'] - logs[start_idx - 1]['logged_at'] <= gap:
                start_idx -= 1

            contiguous_logs = logs[start_idx:end_idx+1]
            movement = { row['logged_at'].isoformat(): row['roomID'] for row in contiguous_logs }
            return jsonify({"type": device_label, "movement": movement})
        else:
            # Fallback: return latest session block
            query = f"""
                SELECT roomID, logged_at
                FROM {data_table}
                WHERE picoID = %s
                ORDER BY logged_at DESC
                LIMIT 1;
            """
            cursor.execute(query, (PICO,))
            last_log = cursor.fetchone()
            if not last_log:
                return jsonify({"error": "No logs found for the specified Pico"}), 404
            
            session_start = last_log['logged_at']
            query = f"""
                SELECT roomID, logged_at
                FROM {data_table}
                WHERE picoID = %s AND logged_at >= %s
                ORDER BY logged_at ASC;
            """
            cursor.execute(query, (PICO, session_start))
            session_logs = cursor.fetchall()
            for row in session_logs:
                if not hasattr(row['logged_at'], 'isoformat'):
                    row['logged_at'] = datetime.strptime(row['logged_at'], "%Y-%m-%d %H:%M:%S")
            movement = { row['logged_at'].isoformat(): row['roomID'] for row in session_logs }
            return jsonify({"type": device_label, "movement": movement})
    except Error as e:
        print(f"Error in /pico: {e}")
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
    try:
        snapshot_time = datetime.fromisoformat(time_str.replace("Z", "")) if time_str else now
    except ValueError:
        return jsonify({"error": "Invalid time format"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500
    cursor = connection.cursor(dictionary=True)
    summary = {}
    try:
        # Occupancy Data: only if mode is "all" or "picos"
        if mode in ("all", "picos"):
            occ_query = """
                SELECT t.roomID, t.picoID
                FROM bluetooth_tracker_data t
                JOIN (
                    SELECT picoID, MAX(logged_at) AS max_time
                    FROM bluetooth_tracker_data
                    WHERE logged_at <= %s AND logged_at >= (%s - INTERVAL 1 MINUTE)
                    GROUP BY picoID
                ) latest ON t.picoID = latest.picoID AND t.logged_at = latest.max_time
            """
            cursor.execute(occ_query, (snapshot_time, snapshot_time))
            occ_rows = cursor.fetchall()
            for row in occ_rows:
                room_id = str(row["roomID"])
                tracker_type = map_tracker_type(row["picoID"])
                if tracker_type == "unknown":
                    continue
                if room_id not in summary:
                    summary[room_id] = {
                        "users": {"count": 0, "id": []},
                        "luggage": {"count": 0, "id": []},
                        "staff": {"count": 0, "id": []},
                        "guard": {"count": 0, "id": []},
                        "environment": {}
                    }
                summary[room_id][tracker_type]["count"] += 1
                summary[room_id][tracker_type]["id"].append(row["picoID"])

        # Environment Data from environment_sensor_data: latest record per sensor (treat picoID as roomID)
        if mode in ("all", "environment"):
            env_query = """
                SELECT e.picoID as roomID, e.temperature, e.sound, e.light, e.IAQ, e.pressure, e.humidity
                FROM environment_sensor_data e
                JOIN (
                    SELECT picoID, MAX(logged_at) AS latest_time
                    FROM environment_sensor_data
                    WHERE logged_at BETWEEN (%s - INTERVAL 1 MINUTE) AND %s
                    GROUP BY picoID
                ) latest ON e.picoID = latest.picoID AND e.logged_at = latest.latest_time
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
    now = datetime.utcnow()
    # Updated: check start_time and end_time from JSON first, then from query parameters.
    start_time_str = req_data.get("start_time") or request.args.get("start_time")
    end_time_str = req_data.get("end_time") or request.args.get("end_time")
    period_str = req_data.get("time_periods") or request.args.get("time_periods", "1hr")
    rooms = req_data.get("rooms") or request.args.getlist("rooms")

    try:
        period_seconds = parse_period(period_str)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    try:
        start_dt = datetime.fromisoformat(start_time_str.replace("Z", "")) if start_time_str else now - timedelta(hours=24)
    except ValueError:
        return jsonify({"error": "Invalid start_time format"}), 400

    try:
        end_dt = datetime.fromisoformat(end_time_str.replace("Z", "")) if end_time_str else now
    except ValueError:
        return jsonify({"error": "Invalid end_time format"}), 400

    if start_dt >= end_dt:
        return jsonify({"error": "start_time must be before end_time"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500
    cursor = connection.cursor(dictionary=True)
    average_summary = {}
    try:
        # 1) Environment: Aggregate by environment_sensor_data grouped by picoID (as roomID) and bucket.
        env_query = """
        SELECT 
            e.picoID as roomID,
            FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(logged_at)/%s)*%s) as bucket,
            AVG(temperature) as avg_temperature, MAX(temperature) as peak_temperature, MIN(temperature) as trough_temperature,
            AVG(sound) as avg_sound, MAX(sound) as peak_sound, MIN(sound) as trough_sound,
            AVG(light) as avg_light, MAX(light) as peak_light, MIN(light) as trough_light,
            AVG(IAQ) as avg_IAQ, MAX(IAQ) as peak_IAQ, MIN(IAQ) as trough_IAQ,
            AVG(pressure) as avg_pressure, MAX(pressure) as peak_pressure, MIN(pressure) as trough_pressure,
            AVG(humidity) as avg_humidity, MAX(humidity) as peak_humidity, MIN(humidity) as trough_humidity
        FROM environment_sensor_data e
        WHERE logged_at BETWEEN %s AND %s
        """
        env_params = [period_seconds, period_seconds, start_dt, end_dt]
        if rooms:
            env_query += " AND e.picoID IN (" + ",".join(["%s"] * len(rooms)) + ")"
            env_params.extend(rooms)
        env_query += " GROUP BY e.picoID, bucket ORDER BY bucket ASC;"
        cursor.execute(env_query, env_params)
        env_results = cursor.fetchall()
        for row in env_results:
            bucket = row["bucket"]
            bucket = bucket.isoformat() + "Z" if isinstance(bucket, datetime) else str(bucket)
            room_id = str(row["roomID"])
            if bucket not in average_summary:
                average_summary[bucket] = {}
            if room_id not in average_summary[bucket]:
                average_summary[bucket][room_id] = init_average_room()
            average_summary[bucket][room_id]["temperature"] = {
                "average": row["avg_temperature"],
                "peak": row["peak_temperature"],
                "trough": row["trough_temperature"]
            }
            average_summary[bucket][room_id]["sound"] = {
                "average": row["avg_sound"],
                "peak": row["peak_sound"],
                "trough": row["trough_sound"]
            }
            average_summary[bucket][room_id]["light"] = {
                "average": row["avg_light"],
                "peak": row["peak_light"],
                "trough": row["trough_light"]
            }
            average_summary[bucket][room_id]["IAQ"] = {
                "average": row["avg_IAQ"],
                "peak": row["peak_IAQ"],
                "trough": row["trough_IAQ"]
            }
            average_summary[bucket][room_id]["pressure"] = {
                "average": row["avg_pressure"],
                "peak": row["peak_pressure"],
                "trough": row["trough_pressure"]
            }
            average_summary[bucket][room_id]["humidity"] = {
                "average": row["avg_humidity"],
                "peak": row["peak_humidity"],
                "trough": row["trough_humidity"]
            }

        # 2) Occupancy: Aggregate counts from bluetooth_tracker_data grouped by room and bucket.
        occ_query = """
            SELECT 
                roomID,
                picoID,
                FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(logged_at)/%s)*%s) as bucket
            FROM bluetooth_tracker_data
            WHERE logged_at BETWEEN %s AND %s
        """
        occ_params = [period_seconds, period_seconds, start_dt, end_dt]
        if rooms:
            occ_query += " AND roomID IN (" + ",".join(["%s"] * len(rooms)) + ")"
            occ_params.extend(rooms)
        occ_query += " ORDER BY logged_at ASC;"
        cursor.execute(occ_query, occ_params)
        occ_rows = cursor.fetchall()
        occupant_counts = {}
        for row in occ_rows:
            bucket = row["bucket"]
            bucket = bucket.isoformat() + "Z" if isinstance(bucket, datetime) else str(bucket)
            room_id = str(row["roomID"])
            tracker = map_tracker_type(row["picoID"])
            if tracker == "unknown":
                continue
            key = (bucket, room_id, tracker)
            occupant_counts[key] = occupant_counts.get(key, 0) + 1

        for (bucket, room_id, tracker), count in occupant_counts.items():
            if bucket not in average_summary:
                average_summary[bucket] = {}
            if room_id not in average_summary[bucket]:
                average_summary[bucket][room_id] = init_average_room()
            average_summary[bucket][room_id][tracker] = {
                "average": count,
                "peak": count,
                "trough": count
            }

        # Ensure every bucket/room has all keys to avoid KeyErrors.
        for bucket_key, rooms_dict in average_summary.items():
            for room_key, data_dict in rooms_dict.items():
                for t in ["users", "luggage", "staff", "guard"]:
                    if t not in data_dict:
                        data_dict[t] = {"average": 0, "peak": 0, "trough": 0}
                for env_var in ["temperature", "sound", "light", "IAQ", "pressure", "humidity"]:
                    if env_var not in data_dict:
                        data_dict[env_var] = {"average": 0, "peak": 0, "trough": 0}
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
    try:
        time_start = datetime.fromisoformat(time_start_str.replace("Z", "")) if time_start_str else now - timedelta(hours=24)
    except ValueError:
        return jsonify({"error": "Invalid time_start format"}), 400
    try:
        time_end = datetime.fromisoformat(time_end_str.replace("Z", "")) if time_end_str else now
    except ValueError:
        return jsonify({"error": "Invalid time_end format"}), 400

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
        for bucket in buckets:
            bucket_end = bucket + timedelta(minutes=1)
            query = """
            SELECT roomID, picoID, logged_at as latest_log,
                   DATE_FORMAT(logged_at, '%%Y-%%m-%%dT%%H:%%i:00Z') as bucket
            FROM bluetooth_tracker_data
            WHERE logged_at >= %s AND logged_at < %s
            ORDER BY logged_at DESC;
            """
            cursor.execute(query, (bucket, bucket_end))
            results = cursor.fetchall()
            if results:
                bucket_data = {}
                for row in results:
                    room_id = str(row['roomID'])
                    tracker = map_tracker_type(row['picoID'])
                    if room_id not in bucket_data:
                        bucket_data[room_id] = {}
                    bucket_data[room_id][row['picoID']] = tracker
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