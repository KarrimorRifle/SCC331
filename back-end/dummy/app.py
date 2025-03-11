import os
import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime, timedelta

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

# Insert functions for pico tables (as defined in init.sql)
def insert_pico_users(conn, data):
    # Inserts data into pico.users (columns: picoID, roomID, logged_at)
    cursor = conn.cursor()
    sql = "INSERT INTO users (picoID, roomID, logged_at) VALUES (%s, %s, %s)"
    cursor.executemany(sql, data)
    conn.commit()
    print(f"Inserted {cursor.rowcount} rows into pico.users")
    cursor.close()

def insert_pico_luggage(conn, data):
    # Inserts data into pico.luggage (columns: picoID, roomID, logged_at)
    cursor = conn.cursor()
    sql = "INSERT INTO luggage (picoID, roomID, logged_at) VALUES (%s, %s, %s)"
    cursor.executemany(sql, data)
    conn.commit()
    print(f"Inserted {cursor.rowcount} rows into pico.luggage")
    cursor.close()

def insert_pico_staff(conn, data):
    # Inserts data into pico.staff (columns: picoID, roomID, logged_at)
    cursor = conn.cursor()
    sql = "INSERT INTO staff (picoID, roomID, logged_at) VALUES (%s, %s, %s)"
    cursor.executemany(sql, data)
    conn.commit()
    print(f"Inserted {cursor.rowcount} rows into pico.staff")
    cursor.close()

def insert_pico_guard(conn, data):
    # Inserts data into pico.guard (columns: picoID, roomID, logged_at)
    cursor = conn.cursor()
    sql = "INSERT INTO guard (picoID, roomID, logged_at) VALUES (%s, %s, %s)"
    cursor.executemany(sql, data)
    conn.commit()
    print(f"Inserted {cursor.rowcount} rows into pico.guard")
    cursor.close()

def insert_pico_environment(conn, data):
    # Inserts data into pico.environment 
    # (columns: picoID, roomID, logged_at, sound, light, temperature, IAQ, pressure, humidity)
    cursor = conn.cursor()
    sql = ("INSERT INTO environment (picoID, roomID, logged_at, sound, light, temperature, IAQ, pressure, humidity) "
           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    cursor.executemany(sql, data)
    conn.commit()
    print(f"Inserted {cursor.rowcount} rows into pico.environment")
    cursor.close()

def generate_dummy_environment_data():
    # Generate dummy environment data for rooms 1, 2, and 3; 30 entries per room leading up to now
    data = []
    base_time = datetime.now().replace(second=0, microsecond=0)
    entries = 30  # per room
    for room in ['1', '2', '3']:
        for i in range(entries):
            # Create timestamps from (now - 29 mins) up to now.
            logged_at = base_time - timedelta(minutes=(entries - 1 - i))
            picoID = f'PICO-{room}-{i+1}'
            # Generate realistic measurement values
            sound = round(random.uniform(40, 70), 2)          # dB
            light = round(random.uniform(200, 800), 2)         # lux
            temperature = round(random.uniform(18, 26), 2)     # Celsius
            IAQ = round(random.uniform(50, 150), 2)            # index
            pressure = round(random.uniform(1000, 1020), 2)    # hPa
            humidity = round(random.uniform(30, 70), 2)        # %
            data.append((picoID, room, logged_at.strftime("%Y-%m-%d %H:%M:%S"),
                         sound, light, temperature, IAQ, pressure, humidity))
    return data

def generate_dummy_users_data():
    # Generate tracking data for 10 users over the past 30 minutes (1 record per minute)
    data = []
    base_time = datetime.now().replace(second=0, microsecond=0) - timedelta(minutes=29)
    for d in range(1, 11):
        picoID = f"PICO-User-{d}"
        current_room = random.choice(['1', '2', '3'])
        for m in range(30):
            time_stamp = base_time + timedelta(minutes=m)
            # With 30% chance, change room (choose from the other two)
            if random.random() < 0.3:
                current_room = random.choice([r for r in ['1', '2', '3'] if r != current_room])
            data.append((picoID, current_room, time_stamp.strftime("%Y-%m-%d %H:%M:%S")))
    return data

def generate_dummy_device_data(device_count, device_type):
    data = []
    base_time = datetime.now().replace(second=0, microsecond=0)
    for d in range(1, device_count + 1):
        skip_next = False
        for m in range(30):
            current_time = base_time - timedelta(minutes=(29 - m))
            if skip_next:
                skip_next = False
                continue
            if random.random() < 0.3:  # chance to skip this and the next minute
                skip_next = True
                continue
            picoID = f"PICO-{device_type}-{d}"
            room = random.choice(['1', '2', '3'])
            data.append((picoID, room, current_time.strftime("%Y-%m-%d %H:%M:%S")))
    return data

if __name__ == '__main__':
    conn = get_connection()
    if conn:
      # Generate and insert dummy tracking data for pico users
      users_data = generate_dummy_users_data()  # 10 users tracked over 30 minutes
      insert_pico_users(conn, users_data)
      guard_data = generate_dummy_device_data(5, "Guard")    # 5 guards across 30 mins (with gaps)
      luggage_data = generate_dummy_device_data(10, "Luggage") # 10 luggage devices across 30 mins (with gaps)
      staff_data = generate_dummy_device_data(5, "Staff")      # 5 staff across 30 mins (with gaps)
      # Insert generated data
      insert_pico_guard(conn, guard_data)
      insert_pico_luggage(conn, luggage_data)
      insert_pico_staff(conn, staff_data)
      dummy_data = generate_dummy_environment_data()
      insert_pico_environment(conn, dummy_data)

      conn.close()
