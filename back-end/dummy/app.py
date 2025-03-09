import os
import mysql.connector
from mysql.connector import Error

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

if __name__ == '__main__':
    conn = get_connection()
    if conn:
      # Inset
      conn.close()
