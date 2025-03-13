import os
import mysql.connector
from mysql.connector import Error
import random
import hashlib
from datetime import datetime, timedelta
import bcrypt
import base64
import time

# -------------------------------
# Database connection helper
# -------------------------------
def get_connection():
    host = os.getenv("DB_HOST", "mysql")
    user = os.getenv("DB_USER", "dummy")
    password = os.getenv("DB_PASSWORD", "dummy")
    database = os.getenv("DB_NAME", "assets")  # default for account/preset creation
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            print("Connected to DB")
            return connection
    except Error as e:
        print("Error connecting to DB:", e)
        return None

def switch_database(conn, database_name):
    try:
        cursor = conn.cursor()
        cursor.execute(f"USE {database_name}")
        print(f"Switched to database: {database_name}")
        cursor.close()
    except Error as e:
        print(f"Error switching database: {e}")

# -------------------------------
# Helper functions for account/preset creation
# -------------------------------
def generate_password(string):
    import bcrypt
    return bcrypt.hashpw(string.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_account(conn, full_name, authority, raw_password, email):
    cursor = conn.cursor()
    pass_hash = generate_password(raw_password)
    sql = "INSERT INTO users (full_name, authority, pass_hash, email) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (full_name, authority, pass_hash, email))
    account_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    return account_id

def create_preset(conn, preset_name, owner_id=None, image_name=None, image_data=None):
    cursor = conn.cursor()
    sql = """INSERT INTO presets (preset_name, owner_id, image_name, image_data)
             VALUES (%s, %s, %s, %s)"""
    cursor.execute(sql, (preset_name, owner_id, image_name, image_data))
    preset_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    return preset_id

def create_map_block(conn, preset_id, roomID, top, left, width, height, colour, label=None):
    cursor = conn.cursor()
    sql = """INSERT INTO map_blocks (preset_id, roomID, label, `top`, `left`, `width`, `height`, colour)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql, (preset_id, roomID, label, top, left, width, height, colour))
    block_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    return block_id

# -------------------------------
# Helper to generate a random MAC address.
# -------------------------------
def generate_mac_address():
    mac = [random.randint(0x00, 0xFF) for _ in range(6)]
    return ':'.join(f"{x:02X}" for x in mac)

# -------------------------------
# Insert functions for pico_device and bluetooth_tracker.
# -------------------------------
def ensure_tracking_group_exists(conn, groupName):
    """
    Ensures a tracking group exists with the given groupName.
    Returns the groupID.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT groupID FROM tracking_groups WHERE groupName = %s", (groupName,))
    row = cursor.fetchone()
    if row:
        groupID = row[0]
    else:
        cursor.execute("INSERT INTO tracking_groups (groupName) VALUES (%s)", (groupName,))
        conn.commit()
        groupID = cursor.lastrowid
    cursor.close()
    return groupID

def insert_pico_device(conn, picoID, readablePicoID, bluetoothID, picoType):
    """
    Inserts or updates a device row into pico_device.
    For environment sensors, picoType = 1.
    For Bluetooth trackers, picoType = 2.
    We ensure 'readablePicoID' is unique by hashing or appending part of the picoID.
    """
    cursor = conn.cursor()
    sql = """INSERT INTO pico_device (picoID, readablePicoID, bluetoothID, picoType)
             VALUES (%s, %s, %s, %s)
             ON DUPLICATE KEY UPDATE
               readablePicoID = VALUES(readablePicoID),
               picoType = VALUES(picoType),
               bluetoothID = VALUES(bluetoothID)
    """
    try:
        cursor.execute(sql, (picoID, readablePicoID, bluetoothID, picoType))
        conn.commit()
    except mysql.connector.IntegrityError as e:
        print(f"Could not insert/update device {picoID}: {e}")
    finally:
        cursor.close()

def insert_or_update_bluetooth_tracker(conn, picoID, trackingGroupID):
    """
    Inserts or updates a row in bluetooth_tracker linking a device to a tracking group.
    If the device does not exist in pico_device, we create it with picoType=2 and a random readable ID.
    """
    # Ensure the device is in pico_device (with picoType=2).
    # If it's missing, create a fallback device entry:
    #   readablePicoID can be a short hash of picoID to ensure uniqueness.
    short_hash = hashlib.md5(picoID.encode()).hexdigest()[:6]
    fallback_readable = f"Tracker-{short_hash}"
    
    # Insert the device in pico_device if missing
    insert_pico_device(conn, picoID, fallback_readable, None, 2)

    # Now link it to the group
    cursor = conn.cursor()
    sql = """INSERT INTO bluetooth_tracker (picoID, trackingGroupID)
             VALUES (%s, %s)
             ON DUPLICATE KEY UPDATE trackingGroupID = VALUES(trackingGroupID)
    """
    try:
        cursor.execute(sql, (picoID, trackingGroupID))
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Could not link {picoID} to group {trackingGroupID}: {e}")
    finally:
        cursor.close()

def insert_bluetooth_tracker_data(conn, data):
    """
    Inserts multiple rows into bluetooth_tracker_data.
    Data is a list of (picoID, roomID, logged_at).
    If the picoID is not found in pico_device, we add it (picoType=2) then link it to 'unknown' group.
    """
    cursor = conn.cursor()
    # We'll do this row by row so we can handle missing devices gracefully
    # (i.e., create them or link them).
    inserted = 0
    for (picoID, roomID, logged_at) in data:
        try:
            # Attempt to insert
            sql = """INSERT INTO bluetooth_tracker_data (picoID, roomID, logged_at)
                     VALUES (%s, %s, %s)"""
            cursor.execute(sql, (picoID, roomID, logged_at))
            inserted += 1
        except mysql.connector.IntegrityError as e:
            # If the device doesn't exist in pico_device, we create it.
            if "foreign key constraint fails" in str(e).lower():
                print(f"dummy  | Adding missing pico_device for {picoID}")
                # Create or update the device
                short_hash = hashlib.md5(picoID.encode()).hexdigest()[:6]
                fallback_readable = f"Tracker-{short_hash}"
                insert_pico_device(conn, picoID, fallback_readable, None, 2)
                
                # Also link it to the "unknown" group or some default
                # If you have a real 'unknown' group, ensure it here:
                unknown_gid = ensure_tracking_group_exists(conn, "unknown")
                insert_or_update_bluetooth_tracker(conn, picoID, unknown_gid)
                
                # Retry the insert
                try:
                    cursor.execute(sql, (picoID, roomID, logged_at))
                    inserted += 1
                except mysql.connector.Error as e2:
                    print(f"dummy  | Still can't insert {picoID} => {e2}")
            else:
                print(f"dummy  | Skipping bluetooth_tracker_data row for {picoID}: {e}")
        except mysql.connector.Error as e:
            print(f"dummy  | Skipping bluetooth_tracker_data row for {picoID}: {e}")
    conn.commit()
    print(f"dummy  | Inserted {inserted} rows into bluetooth_tracker_data")
    cursor.close()

def insert_environment_sensor_data(conn, data):
    """
    Inserts multiple rows into environment_sensor_data.
    Data is a list of (picoID, logged_at, sound, light, temperature, IAQ, pressure, humidity).
    If the device doesn't exist, we create it with picoType=1.
    """
    cursor = conn.cursor()
    inserted = 0
    for row in data:
        (picoID, logged_at, sound, light, temperature, IAQ, pressure, humidity) = row
        try:
            sql = """INSERT INTO environment_sensor_data
                     (picoID, logged_at, sound, light, temperature, IAQ, pressure, humidity)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                  """
            cursor.execute(sql, row)
            inserted += 1
        except mysql.connector.IntegrityError as e:
            if "foreign key constraint fails" in str(e).lower():
                print(f"dummy  | Adding missing pico_device for env-sensor {picoID}")
                # Insert the environment device
                short_hash = hashlib.md5(picoID.encode()).hexdigest()[:6]
                fallback_readable = f"Env-{short_hash}"
                insert_pico_device(conn, picoID, fallback_readable, None, 1)
                
                # Retry
                try:
                    cursor.execute(sql, row)
                    inserted += 1
                except mysql.connector.Error as e2:
                    print(f"dummy  | Still can't insert environment row {picoID}: {e2}")
            else:
                print(f"dummy  | Skipping environment row for {picoID}: {e}")
        except mysql.connector.Error as e:
            print(f"dummy  | Skipping environment row for {picoID}: {e}")
    conn.commit()
    print(f"dummy  | Inserted {inserted} rows into environment_sensor_data")
    cursor.close()

# -------------------------------
# Dummy Data Generation Functions
# -------------------------------
def generate_dummy_environment_data():
    """
    Generate dummy environment sensor data for three rooms.
    Each room (using a placeholder string) gets 60 entries (one per minute).
    """
    data = []
    base_time = datetime.now().replace(second=0, microsecond=0)
    entries = 60
    for room in ['d83add67ed84', 'd83add41a997', 'd83add8af3cf']:
        for i in range(entries):
            logged_at = base_time - timedelta(minutes=(entries - 1 - i))
            picoID = room  
            sound = round(random.uniform(40, 70), 2)
            light = round(random.uniform(200, 800), 2)
            temperature = round(random.uniform(18, 26), 2)
            IAQ = round(random.uniform(50, 150), 2)
            pressure = round(random.uniform(1000, 1020), 2)
            humidity = round(random.uniform(30, 70), 2)
            data.append((picoID, logged_at.strftime("%Y-%m-%d %H:%M:%S"),
                         sound, light, temperature, IAQ, pressure, humidity))
    return data

def generate_dummy_tracking_data_for_devices(picoIDs, entries=60):
    """
    Generate dummy tracking data for each device in picoIDs.
    Each device gets 'entries' records (one per minute) with random room changes.
    """
    data = []
    base_time = datetime.now().replace(second=0, microsecond=0) - timedelta(minutes=(entries - 1))
    rooms = ['d83add67ed84', 'd83add41a997', 'd83add8af3cf']
    for dev in picoIDs:
        current_room = random.choice(rooms)
        for m in range(entries):
            ts = base_time + timedelta(minutes=m)
            if random.random() < 0.3:
                current_room = random.choice([r for r in rooms if r != current_room])
            data.append((dev, current_room, ts.strftime("%Y-%m-%d %H:%M:%S")))
    return data

def convert_image_to_base64(filepath):
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def set_default_preset(conn, preset_id):
    cursor = conn.cursor()
    sql = "UPDATE default_preset SET preset_id = %s WHERE id = 1"
    cursor.execute(sql, (preset_id,))
    conn.commit()
    cursor.close()

# -------------------------------
# Main Execution: Insert Dummy Data
# -------------------------------
if __name__ == '__main__':
    conn = get_connection()
    if not conn:
        print("Database connection failed, exiting.")
        exit(1)

    # Switch to the pico database.
    switch_database(conn, "pico")

    # 1) Insert environment sensor devices for each room.
    env_rooms = ['d83add67ed84', 'd83add41a997', 'd83add8af3cf']
    for room in env_rooms:
        # Use a short hash to ensure unique readable IDs
        import hashlib
        short_hash = hashlib.md5(room.encode()).hexdigest()[:6]
        env_readable = f"Env-{short_hash}"
        insert_pico_device(conn, room, env_readable, None, 1)

    # 2) Ensure tracking groups exist for built-in types + "unknown"
    tracking_groups = {}
    for grp in ["user", "luggage", "staff", "security", "unknown"]:
        tracking_groups[grp] = ensure_tracking_group_exists(conn, grp)

    # 3) Create Bluetooth tracker devices for each type.
    devices_by_type = {"User": [], "Luggage": [], "Staff": [], "Security": []}
    tracker_counts = {"User": 10, "Luggage": 10, "Staff": 5, "Security": 5}
    for tracker, cnt in tracker_counts.items():
        for i in range(cnt):
            mac = generate_mac_address()
            short_hash = hashlib.md5(mac.encode()).hexdigest()[:6]
            # e.g. "User-01-abc123"
            readable = f"{tracker}-{i+1:02d}-{short_hash}"
            insert_pico_device(conn, mac, readable, None, 2)
            grp_name = tracker.lower()  # "user", "luggage", etc.
            grp_id = tracking_groups[grp_name]
            insert_or_update_bluetooth_tracker(conn, mac, grp_id)
            devices_by_type[tracker].append(mac)

    # 4) Generate and insert dummy tracking data into bluetooth_tracker_data.
    bt_data = []
    for tracker, macs in devices_by_type.items():
        bt_data.extend(generate_dummy_tracking_data_for_devices(macs, 60))
    insert_bluetooth_tracker_data(conn, bt_data)

    # 5) Generate and insert dummy environment sensor data.
    env_data = generate_dummy_environment_data()
    insert_environment_sensor_data(conn, env_data)

    # 6) Switch to accounts and assets to create a dummy account and preset.
    try:
        switch_database(conn, "accounts")
        try:
            account_id = create_account(conn, "filler", "Super Admin", "filler", "filler@fakecompany.co.uk")
        except Error as e:
            # If it already exists, just find the existing one
            if "Duplicate entry" in str(e):
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE email=%s", ("filler@fakecompany.co.uk",))
                row = cursor.fetchone()
                if row:
                    account_id = row[0]
                else:
                    raise
            else:
                raise

        switch_database(conn, "assets")
        image_data = ""
        if os.path.exists("store.png"):
            image_data = convert_image_to_base64("store.png")

        preset_id = create_preset(conn, "Default", account_id, "store.png", image_data)
        create_map_block(conn, preset_id, env_rooms[0], 30, 20, 300, 300, "#ab28b2", "Reception")
        create_map_block(conn, preset_id, env_rooms[1], 330, 20, 300, 300, "#3a5fcd", "Security")
        create_map_block(conn, preset_id, env_rooms[2], 30, 320, 300, 300, "#e94d1b", "Lobby")
        set_default_preset(conn, preset_id)
    except Error as e:
        print("Error creating account or preset:", e)

    # 7) Live Simulation: Inserting live tracking and environment data every minute.
    switch_database(conn, "pico")
    ROOMS = env_rooms
    live_states = {
        "User": {mac: random.choice(ROOMS) for mac in devices_by_type["User"]},
        "Luggage": {mac: random.choice(ROOMS) for mac in devices_by_type["Luggage"]},
        "Staff": {mac: random.choice(ROOMS) for mac in devices_by_type["Staff"]},
        "Security": {mac: random.choice(ROOMS) for mac in devices_by_type["Security"]}
    }

    def simulate_minute(current_time, state):
        recs = []
        for picoID, cur_room in state.items():
            # decide if room changes
            if random.random() < 0.30:
                new_room = random.choice([r for r in ROOMS if r != cur_room])
                state[picoID] = new_room
            else:
                new_room = cur_room
            # add random seconds offset
            ts = current_time + timedelta(seconds=random.randint(0, 59))
            recs.append((picoID, new_room, ts.strftime("%Y-%m-%d %H:%M:%S")))
        return recs

    def simulate_environment(current_time):
        recs = []
        for rm in ROOMS:
            picoID = rm
            sound = round(random.uniform(40, 70), 2)
            light = round(random.uniform(200, 800), 2)
            temperature = round(random.uniform(18, 26), 2)
            IAQ = round(random.uniform(50, 150), 2)
            pressure = round(random.uniform(1000, 1020), 2)
            humidity = round(random.uniform(30, 70), 2)
            ts = current_time + timedelta(seconds=random.randint(0, 59))
            recs.append((picoID, ts.strftime("%Y-%m-%d %H:%M:%S"),
                         sound, light, temperature, IAQ, pressure, humidity))
        return recs

    print("Starting live simulation (press CTRL+C to stop)...")
    try:
        while True:
            current_time = datetime.now()
            print(f"\n--- Live Simulation: {current_time.strftime('%Y-%m-%d %H:%M:%S')} ---")

            # Insert tracking data
            for tracker, st in live_states.items():
                new_data = simulate_minute(current_time, st)
                insert_bluetooth_tracker_data(conn, new_data)

            # Insert environment data
            env_live = simulate_environment(current_time)
            insert_environment_sensor_data(conn, env_live)

            time.sleep(60)
    except KeyboardInterrupt:
        print("Live simulation interrupted by user.")
    except Exception as e:
        print("Error during live simulation:", e)
    finally:
        conn.close()
