from flask import Flask, request, jsonify, make_response
import mysql.connector
from mysql.connector import Error, pooling
from datetime import datetime, timedelta
import os
import requests
import time
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

# -------------------------------
# Database Connection Pool
# -------------------------------
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=32,
    pool_reset_session=True,
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')  # This should be "pico"
)

def get_db_connection():
    try:
        return connection_pool.get_connection()
    except Error as e:
        print(f"Error getting connection from pool: {e}")
        return None

# -------------------------------
# Session Validation
# -------------------------------
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
        return {"error": "Invalid cookie"}, 401
    return None

# -------------------------------
# Custom Type Lookup
# -------------------------------
def lookup_tracking_group(picoID):
    """
    Given a MAC address (picoID), look up its current tracking group from the bluetooth_tracker table.
    Returns the groupName in lowercase if found, otherwise "unknown".
    """
    conn = get_db_connection()
    if conn is None:
        return "unknown"
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT tg.groupName
            FROM bluetooth_tracker bt
            LEFT JOIN tracking_groups tg ON bt.trackingGroupID = tg.groupID
            WHERE bt.picoID = %s
        """, (picoID,))
        row = cursor.fetchone()
        if row is not None and row[0]:
            return row[0].lower()
        else:
            return "unknown"
    except Error as e:
        print("Error in lookup_tracking_group:", e)
        return "unknown"
    finally:
        cursor.close()
        conn.close()

# -------------------------------
# Helper Functions for Type Mapping
# -------------------------------
def get_tracker_type(picoID):
    """
    Returns the device type (singular) based on picoID.
    For Bluetooth trackers, since picoID is a MAC address, we look up the tracking group.
    Otherwise, fallback to prefix matching.
    """
    # If picoID is a MAC address (typical length 17), assume it's a bluetooth tracker.
    if len(picoID) == 17:
        return lookup_tracking_group(picoID)
    # Fallback to built-in prefix matching (if your IDs ever use the old format)
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
    Returns the type in plural form for summary aggregation.
    For built-in types, this converts singular to plural.
    For custom types (returned by lookup_tracking_group), we return as is.
    """
    t = get_tracker_type(picoID)
    if t == "user":
        return "users"
    elif t == "security":  # map "security" to "guard"
        return "guard"
    elif t in ["luggage", "staff", "guard"]:
        return t
    elif t != "unknown":
        return t  # For custom types, return as is
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

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT picoType, readablePicoID FROM pico_device WHERE picoID = %s", (PICO,))
        device = cursor.fetchone()
        if not device:
            return jsonify({"error": "Pico device not found"}), 404

        picoType = device['picoType']
        if picoType == 2:
            data_table = "bluetooth_tracker_data"
            device_label = get_tracker_type(PICO)
            # New contiguous block selection using 2-minute gap
            req_data = request.get_json(silent=True)
            provided_time = None
            if req_data and req_data.get("time"):
                provided_time = datetime.fromisoformat(req_data.get("time"))
            # Use provided_time as anchor if available; otherwise, use last log timestamp
            anchor = provided_time
            if anchor:
                day_start = anchor.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                cursor.execute(f"""
                    SELECT roomID, logged_at
                    FROM {data_table}
                    WHERE picoID = %s
                    ORDER BY logged_at DESC
                    LIMIT 1;
                """, (PICO,))
                last_log = cursor.fetchone()
                if not last_log:
                    return jsonify({"error": "No logs found for the specified Pico"}), 404
                anchor = last_log['logged_at']
                day_start = anchor.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            # Retrieve all logs for the day
            cursor.execute(f"""
                SELECT roomID, logged_at
                FROM {data_table}
                WHERE picoID = %s AND logged_at BETWEEN %s AND %s
                ORDER BY logged_at ASC;
            """, (PICO, day_start, day_end))
            logs = cursor.fetchall()
            if not logs:
                return jsonify({"error": "No logs found for the specified Pico"}), 404
            for row in logs:
                if not hasattr(row['logged_at'], 'isoformat'):
                    row['logged_at'] = datetime.strptime(row['logged_at'], "%Y-%m-%d %H:%M:%S")
            gap = timedelta(minutes=2)
            # Locate index where log time is >= anchor
            idx = next((i for i, row in enumerate(logs) if row['logged_at'] >= anchor), len(logs) - 1)
            # Expand backwards
            start_idx = idx
            while start_idx - 1 >= 0 and (logs[start_idx]['logged_at'] - logs[start_idx - 1]['logged_at']) <= gap:
                start_idx -= 1
            # Expand forwards
            end_idx = idx
            while end_idx + 1 < len(logs) and (logs[end_idx + 1]['logged_at'] - logs[end_idx]['logged_at']) <= gap:
                end_idx += 1
            contiguous_logs = logs[start_idx:end_idx + 1]
            movement = {row['logged_at'].isoformat(): row['roomID'] for row in contiguous_logs}
            return jsonify({"type": device_label, "movement": movement})
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

            for row in logs:
                if not hasattr(row['logged_at'], 'isoformat'):
                    row['logged_at'] = datetime.strptime(row['logged_at'], "%Y-%m-%d %H:%M:%S")
            
            gap = timedelta(seconds=90)
            idx = None
            for i, row in enumerate(logs):
                if row['logged_at'] >= provided_time:
                    idx = i
                    break
            if idx is None:
                idx = len(logs) - 1

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
        conn.close()

# -------------------------------
# /summary Endpoint
# -------------------------------
@app.route('/summary', methods=['GET'])
def summary():
    cookie_validation_error = validate_session_cookie(request)
    if cookie_validation_error:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]

    time_str = request.args.get("time")
    mode = request.args.get("mode", "all")
    if mode not in ("all", "picos", "environment"):
        return jsonify({"error": "Invalid mode parameter"}), 400

    now = datetime.utcnow()
    try:
        snapshot_time = datetime.fromisoformat(time_str.replace("Z", "")) if time_str else now
    except ValueError:
        return jsonify({"error": "Invalid time format"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500

    cursor = conn.cursor(dictionary=True)
    summary_data = {}
    # We'll keep track of all discovered tracker types in a set.
    discovered_types = set()

    try:
        # -----------------------------
        # 1) Occupancy Data (Bluetooth)
        # -----------------------------
        if mode in ("all", "picos"):
            occ_query = """
                SELECT t.roomID, t.picoID
                FROM bluetooth_tracker_data t
                JOIN (
                    SELECT picoID, MAX(logged_at) AS max_time
                    FROM bluetooth_tracker_data
                    WHERE logged_at <= %s AND logged_at >= (%s - INTERVAL 2 MINUTE)
                    GROUP BY picoID
                ) latest ON t.picoID = latest.picoID AND t.logged_at = latest.max_time
            """
            cursor.execute(occ_query, (snapshot_time, snapshot_time))
            occ_rows = cursor.fetchall()

            for row in occ_rows:
                room_id = str(row["roomID"])
                tracker_type = map_tracker_type(row["picoID"])  # e.g. "users", "staff", "guard", "vip", etc.
                if tracker_type == "unknown":
                    continue  # skip unrecognized trackers

                discovered_types.add(tracker_type)  # track that we have seen this type

                if room_id not in summary_data:
                    summary_data[room_id] = {}

                if tracker_type not in summary_data[room_id]:
                    summary_data[room_id][tracker_type] = {
                        "count": 0,
                        "id": []
                    }

                summary_data[room_id][tracker_type]["count"] += 1
                summary_data[room_id][tracker_type]["id"].append(row["picoID"])

        # -----------------------------
        # 2) Environment Data
        # -----------------------------
        if mode in ("all", "environment"):
            env_query = """
                SELECT e.picoID AS roomID,
                       e.temperature, e.sound, e.light, e.IAQ, e.pressure, e.humidity
                FROM environment_sensor_data e
                JOIN (
                    SELECT picoID, MAX(logged_at) AS latest_time
                    FROM environment_sensor_data
                    WHERE logged_at BETWEEN (%s - INTERVAL 2 MINUTE) AND %s
                    GROUP BY picoID
                ) latest ON e.picoID = latest.picoID AND e.logged_at = latest.latest_time
            """
            cursor.execute(env_query, (snapshot_time, snapshot_time))
            env_rows = cursor.fetchall()

            for row in env_rows:
                room_id = str(row["roomID"])
                if room_id not in summary_data:
                    summary_data[room_id] = {}
                summary_data[room_id]["environment"] = {
                    "temperature": row["temperature"],
                    "sound": row["sound"],
                    "light": row["light"],
                    "IAQ": row["IAQ"],
                    "pressure": row["pressure"],
                    "humidity": row["humidity"]
                }

        # --------------------------------------------------------
        # 3) Merge historical attributes from the past day
        # --------------------------------------------------------
        past_day_start = now - timedelta(days=1)
        # Historical occupancy: find distinct tracker types from the past day.
        historical_occ_query = """
            SELECT picoID
            FROM bluetooth_tracker_data
            WHERE logged_at BETWEEN %s AND %s
        """
        cursor.execute(historical_occ_query, (past_day_start, now))
        hist_occ_rows = cursor.fetchall()
        historical_tracker_types = set()
        for row in hist_occ_rows:
            t = map_tracker_type(row["picoID"])
            if t != "unknown":
                historical_tracker_types.add(t)
        
        # Historical environment: check which sensor columns were ever reported in the past day.
        historical_env_query = """
            SELECT 
                SUM(CASE WHEN temperature IS NOT NULL THEN 1 ELSE 0 END) as cnt_temperature,
                SUM(CASE WHEN sound IS NOT NULL THEN 1 ELSE 0 END) as cnt_sound,
                SUM(CASE WHEN light IS NOT NULL THEN 1 ELSE 0 END) as cnt_light,
                SUM(CASE WHEN IAQ IS NOT NULL THEN 1 ELSE 0 END) as cnt_IAQ,
                SUM(CASE WHEN pressure IS NOT NULL THEN 1 ELSE 0 END) as cnt_pressure,
                SUM(CASE WHEN humidity IS NOT NULL THEN 1 ELSE 0 END) as cnt_humidity
            FROM environment_sensor_data
            WHERE logged_at BETWEEN %s AND %s
        """
        cursor.execute(historical_env_query, (past_day_start, now))
        hist_env = cursor.fetchone()
        historical_env_attributes = set()
        if hist_env:
            if hist_env["cnt_temperature"] > 0:
                historical_env_attributes.add("temperature")
            if hist_env["cnt_sound"] > 0:
                historical_env_attributes.add("sound")
            if hist_env["cnt_light"] > 0:
                historical_env_attributes.add("light")
            if hist_env["cnt_IAQ"] > 0:
                historical_env_attributes.add("IAQ")
            if hist_env["cnt_pressure"] > 0:
                historical_env_attributes.add("pressure")
            if hist_env["cnt_humidity"] > 0:
                historical_env_attributes.add("humidity")
        
        # For each room, add missing occupancy and environment keys based on historical data.
        for room_id in summary_data:
            # Occupancy: merge historical tracker types.
            for t in historical_tracker_types:
                if t not in summary_data[room_id]:
                    summary_data[room_id][t] = {"count": 0, "id": []}
            # Environment: if environment key exists, add missing sensor attributes with null.
            if "environment" in summary_data[room_id]:
                for attr in historical_env_attributes:
                    if attr not in summary_data[room_id]["environment"]:
                        summary_data[room_id]["environment"][attr] = None
        return jsonify(summary_data)

    except Error as e:
        print(f"Error in /summary: {e}")
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# -------------------------------
# /summary/average Endpoint
# -------------------------------
def parse_period(period_str):
    period_str = period_str.strip().lower()
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
    cookie_validation_error = validate_session_cookie(request)
    if cookie_validation_error:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]

    req_data = request.get_json(silent=True) or {}
    now = datetime.utcnow()
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

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500
    cursor = conn.cursor(dictionary=True)
    average_summary = {}
    try:
        # 1) Environment: Aggregate by environment_sensor_data grouped by picoID (as roomID) and time bucket.
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

        # 2) Occupancy: Aggregate counts from bluetooth_tracker_data grouped by roomID, time bucket, and tracker type.
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

        # Ensure every bucket/room has all keys.
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
        print(f"Error in /summary/average: {e}")
        return jsonify({"error": "Error querying data", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# -------------------------------
# /movement Endpoint
# -------------------------------
@app.route('/movement', methods=['GET'])
def movement():
    cookie_validation_error = validate_session_cookie(request)
    if cookie_validation_error:
        return jsonify(cookie_validation_error[0]), cookie_validation_error[1]
    
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

    time_start = time_start.replace(second=0, microsecond=0)
    time_end = time_end.replace(second=0, microsecond=0)

    buckets = []
    current_bucket = time_start
    while current_bucket <= time_end:
        buckets.append(current_bucket)
        current_bucket += timedelta(minutes=1)

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "MySQL connection unavailable"}), 500
    cursor = conn.cursor(dictionary=True)
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
        print(f"Error in /movement: {e}")
        return jsonify({"error": "Error querying movement data", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    get_db_connection()  # Warm up connection
    app.run(host='0.0.0.0', port=5003)