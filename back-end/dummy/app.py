import os
import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime, timedelta
import bcrypt
import base64
import time

def get_connection():
    host = os.getenv("DB_HOST", "mysql")
    user = os.getenv("DB_USER", "dummy")
    password = os.getenv("DB_PASSWORD", "dummy")
    database = os.getenv("DB_NAME", "assets")
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

def generate_password(string):
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


def insert_pico_device(conn, picoID, readablePicoID, bluetoothID, picoType):
    """
    Inserts a dummy device into the pico_device table.
    picoType: 1 for environment sensor, 2 for bluetooth tracker.
    """
    cursor = conn.cursor()
    sql = """INSERT INTO pico_device (picoID, readablePicoID, bluetoothID, picoType)
             VALUES (%s, %s, %s, %s)
             ON DUPLICATE KEY UPDATE readablePicoID = VALUES(readablePicoID)"""
    cursor.execute(sql, (picoID, readablePicoID, bluetoothID, picoType))
    conn.commit()
    cursor.close()

def insert_bluetooth_tracker_data(conn, data):
    """
    Inserts tracking data into the bluetooth_tracker_data table.
    Expected columns: picoID, roomID, logged_at
    """
    cursor = conn.cursor()
    sql = "INSERT INTO bluetooth_tracker_data (picoID, roomID, logged_at) VALUES (%s, %s, %s)"
    cursor.executemany(sql, data)
    conn.commit()
    print(f"Inserted {cursor.rowcount} rows into bluetooth_tracker_data")
    cursor.close()

def insert_environment_sensor_data(conn, data):
    cursor = conn.cursor()
    sql = ("INSERT INTO environment_sensor_data (picoID, logged_at, sound, light, temperature, IAQ, pressure, humidity) "
           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    cursor.executemany(sql, data)
    conn.commit()
    print(f"Inserted {cursor.rowcount} rows into environment_sensor_data")
    cursor.close()


# ------------------------------------------------------------------
# Dummy Data Generation Functions (updated for tracker types)
# ------------------------------------------------------------------

def generate_dummy_environment_data():
    """
    Generate dummy environment sensor data for three devices (one per room).
    Each device gets 60 entries (one per minute) leading up to the current time.
    The picoID indicates an environment sensor.
    """
    data = []
    base_time = datetime.now().replace(second=0, microsecond=0)
    entries = 60  # per device
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
            # Removed room from the tuple as it's not a column in the table.
            data.append((picoID, logged_at.strftime("%Y-%m-%d %H:%M:%S"),
                         sound, light, temperature, IAQ, pressure, humidity))
    return data


def generate_dummy_tracking_data(tracker_prefix, device_count, entries=60):
    """
    Generate dummy tracking data for a given tracker type.
    tracker_prefix: string, e.g. "User", "Luggage", "Staff", "Security"
    Each device gets 'entries' records (one per minute).
    """
    data = []
    base_time = datetime.now().replace(second=0, microsecond=0) - timedelta(minutes=(entries - 1))
    for d in range(1, device_count + 1):
        picoID = f"PICO-{tracker_prefix.upper()}-{d}"
        current_room = random.choice(['d83add67ed84', 'd83add41a997', 'd83add8af3cf'])
        for m in range(entries):
            time_stamp = base_time + timedelta(minutes=m)
            # With 30% chance, change room (choose from the other rooms)
            if random.random() < 0.3:
                current_room = random.choice([r for r in ['d83add67ed84', 'd83add41a997', 'd83add8af3cf'] if r != current_room])
            data.append((picoID, current_room, time_stamp.strftime("%Y-%m-%d %H:%M:%S")))
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

# ------------------------------------------------------------------
# Main execution: Insert dummy data
# ------------------------------------------------------------------
if __name__ == '__main__':
    conn = get_connection()
    if conn:
        # Switch to the pico database for tracking data and devices.
        switch_database(conn, "pico")
        
        # Insert dummy devices for each tracker type (bluetooth trackers have picoType=2)
        tracker_types = {
            "User": 10,
            "Luggage": 10,
            "Staff": 5,
            "Security": 5  # replacing the previous "Guard" type
        }
        for tracker, count in tracker_types.items():
            for i in range(1, count + 1):
                picoID = f"PICO-{tracker.upper()}-{i}"
                readablePicoID = f"{tracker}-{i:02d}"
                bluetoothID = None  # or assign an integer if needed
                insert_pico_device(conn, picoID, readablePicoID, bluetoothID, 2)
        
        # Generate and insert dummy tracking data into bluetooth_tracker_data.
        user_data = generate_dummy_tracking_data("User", 10)
        luggage_data = generate_dummy_tracking_data("Luggage", 10)
        staff_data = generate_dummy_tracking_data("Staff", 5)
        security_data = generate_dummy_tracking_data("Security", 5)
        
        insert_bluetooth_tracker_data(conn, user_data)
        insert_bluetooth_tracker_data(conn, luggage_data)
        insert_bluetooth_tracker_data(conn, staff_data)
        insert_bluetooth_tracker_data(conn, security_data)
        
        # Insert dummy environment sensor data.
        env_data = generate_dummy_environment_data()
        insert_environment_sensor_data(conn, env_data)
        
        # Switch to accounts and assets to create an account and preset.
        try:
            switch_database(conn, "accounts")
            accountID = create_account(conn, "filler", "Super Admin", "filler", "filler@fakecompany.co.uk")
            
            switch_database(conn, "assets")
            image_data = convert_image_to_base64("store.png")
            presetID = create_preset(conn, "Default", accountID, "store.png", image_data)
            create_map_block(conn, presetID, 'd83add67ed84', 30, 20, 300, 300, "#ab28b2", "Reception")
            create_map_block(conn, presetID, 'd83add41a997', 330, 20, 300, 300, "#3a5fcd", "Security")
            create_map_block(conn, presetID, 'd83add8af3cf', 30, 320, 300, 300, "#e94d1b", "Lobby")
            set_default_preset(conn, presetID)
        except Exception as e:
            print("Error creating account or preset:", e)
        
        # ------------------------------------------------------------------
        # Live simulation: Inserting live tracking and environment data every minute.
        # ------------------------------------------------------------------
        switch_database(conn, "pico")
        ROOMS = ['d83add67ed84', 'd83add41a997', 'd83add8af3cf']
        
        live_states = {
            "User": {f"PICO-USER-{d}": random.choice(ROOMS) for d in range(1, 11)},
            "Luggage": {f"PICO-LUGGAGE-{d}": random.choice(ROOMS) for d in range(1, 11)},
            "Staff": {f"PICO-STAFF-{d}": random.choice(ROOMS) for d in range(1, 6)},
            "Security": {f"PICO-SECURITY-{d}": random.choice(ROOMS) for d in range(1, 6)}
        }
        
        def simulate_minute(current_time, state):
            records = []
            for picoID, current_room in state.items():
                # Skip updating sometimes.
                if random.random() < 0.20:
                    continue
                if random.random() < 0.30:
                    new_room = random.choice([r for r in ROOMS if r != current_room])
                    state[picoID] = new_room
                else:
                    new_room = current_room
                records.append((picoID, new_room, current_time.strftime("%Y-%m-%d %H:%M:%S")))
            return records
        
        def simulate_environment(current_time):
            records = []
            for room in ROOMS:
                picoID = room
                sound = round(random.uniform(40, 70), 2)
                light = round(random.uniform(200, 800), 2)
                temperature = round(random.uniform(18, 26), 2)
                IAQ = round(random.uniform(50, 150), 2)
                pressure = round(random.uniform(1000, 1020), 2)
                humidity = round(random.uniform(30, 70), 2)
                # Removed room from the tuple.
                records.append((picoID, current_time.strftime("%Y-%m-%d %H:%M:%S"),
                                sound, light, temperature, IAQ, pressure, humidity))
            return records

                
        print("Starting live simulation (press CTRL+C to stop)...")
        try:
            while True:
                current_time = datetime.now()
                print(f"\n--- Live Simulation: {current_time.strftime('%Y-%m-%d %H:%M:%S')} ---")
                for tracker, state in live_states.items():
                    records = simulate_minute(current_time, state)
                    if records:
                        insert_bluetooth_tracker_data(conn, records)
                env_records = simulate_environment(current_time)
                if env_records:
                    insert_environment_sensor_data(conn, env_records)
                time.sleep(60)
        except KeyboardInterrupt:
            print("Live simulation interrupted by user.")
        except Exception as e:
            print("Error during live simulation:", e)
        finally:
            conn.close()
