from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import bcrypt
import uuid
from datetime import datetime
import os
import time

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Establish a persistent connection to the database
db_connection = None

def get_db_connection():
	attempts = 5
	for attempt in range(attempts):
		try:
			db_connection = mysql.connector.connect(
				host=os.getenv('DB_HOST'),
				user=os.getenv('DB_USER'),
				password=os.getenv('DB_PASSWORD'),
				database=os.getenv('DB_NAME')
			)
			return db_connection
		except Error as e:
			print(f"Error connecting to MySQL (attempt {attempt + 1}/{attempts}): {e}")
			time.sleep(2)  # Wait for 2 seconds before retrying
	return None

def validate_session_cookie(request):
	VALIDATION_SITE = "http://account_login:5002/validate_cookie"
	cookie = request.cookies.get("session_id")

	if not cookie:
		print("No session_id cookie found.")
		return {"error": "Invalid cookie", "message": "Cookie missing"}, 401

	print(f"Cookie found: {cookie}")
	r = request.get(VALIDATION_SITE, headers={"session-id": cookie})
	if r.status_code != 200:
		print("ERR: Invalid cookie detected")
		return {"error": "Invalid cookie"}, 401 #, "message": r.text

	# Return None if everything is valid (no error)
	return None

# Get the users for the Admin page
@app.route('/get_users_admin', methods=['GET'])
def get_users():
	session_id = request.headers.get('session-id') or request.cookies.get('session_id')
	if not session_id:
		return jsonify({"error": "No session cookie or header provided"}), 400
	
	connection = get_db_connection()
	if connection is None:
		return jsonify({"error": "Database connection failed"}), 500
	
	cursor = connection.cursor(dictionary=True)
	cursor.execute("SELECT email, full_name as name, last_login, authority FROM users")
	users = cursor.fetchall()
	cursor.close()
	connection.close()

	return jsonify({"users": users}), 200


@app.route('/get_users_messages_page', methods=['GET'])
def get_users_messsages():
    session_id = request.headers.get('session-id') or request.cookies.get('session_id')
    if not session_id:
        return jsonify({"error": "No session cookie or header provided"}), 400
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = connection.cursor(dictionary=True)

    # Retrieve the logged-in user's user_id based on session ID
    cursor.execute("SELECT user_id FROM users WHERE cookie = %s", (session_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.close()
        connection.close()
        return jsonify({"error": "User not found!"}), 404

    user_id = user["user_id"]

    # Exclude the logged-in user from the list of users
    cursor.execute("""
        SELECT email, full_name AS name, last_login, authority
        FROM users
        WHERE user_id != %s
    """, (user_id,))
    
    users = cursor.fetchall()
    cursor.close()
    connection.close()

    return jsonify({"users": users}), 200

	
@app.route('/send_message', methods=['POST'])
def send_message():
	session_id = request.headers.get('session-id') or request.cookies.get('session_id')
	if not session_id:
		return jsonify({"error": "No session cookie or header provided"}), 400

	connection = get_db_connection()
	if connection is None:
		return jsonify({"error": "Database connection failed"}), 500

	cursor = connection.cursor(dictionary=True)

	# Get sender user_id from session
	cursor.execute("SELECT user_id FROM users WHERE cookie = %s", (session_id,))
	user = cursor.fetchone()
	
	if user is None:
		cursor.close()
		connection.close()
		return jsonify({"error": "User not found!"}), 402

	sender_id = user['user_id']
	
	data = request.get_json()
	if not data or 'receiver_email' not in data or 'message' not in data:
		cursor.close()
		connection.close()
		return jsonify({"error": "Receiver email and message are required."}), 403
	
	receiver_email = data['receiver_email']
	message = data['message']

	# Get receiver_id using email
	cursor.execute("SELECT user_id FROM users WHERE email = %s", (receiver_email,))
	receiver = cursor.fetchone()
	
	if receiver is None:
		cursor.close()
		connection.close()
		return jsonify({"error": "Receiver not found!"}), 404

	receiver_id = receiver['user_id']

	try:
		cursor.execute("""
			INSERT INTO messages (receiver_id, sender_id, left_message)
			VALUES (%s, %s, %s)
		""", (receiver_id, sender_id, message))
		connection.commit()
		cursor.close()
		connection.close()
		return jsonify({"message": "Message sent successfully."}), 200
	except Error as e:
		cursor.close()
		connection.close()
		return jsonify({"error": f"Failed to send message: {e}"}), 500
		
		
# Delete users using the delete button next to each user
@app.route('/delete_user', methods=['POST'])
def delete_user():
	session_id = request.headers.get('session-id') or request.cookies.get('session_id')
	if not session_id:
		return jsonify({"error": "No session cookie or header provided"}), 400

	connection = get_db_connection()
	if connection is None:
		return jsonify({"error": "Database connection failed"}), 500

	data = request.get_json()
	if not data or "email" not in data:
		return jsonify({"error": "Email is required for deletion"}), 400
		
	cursor = connection.cursor(dictionary=True)
	
	try:
		cursor.execute("DELETE FROM users WHERE email = %s", (data["email"],))
		connection.commit()
		cursor.close()
		connection.close()
		return jsonify({"message": "User deleted successfully"}), 200
	except Error as e:
		cursor.close()
		connection.close()
		return jsonify({"error": f"Failed to delete user: {e}"}), 500


import bcrypt
# Reset password functionality
@app.route('/reset_password', methods=['POST'])
def reset_password():
	session_id = request.headers.get('session-id') or request.cookies.get('session_id')
	if not session_id:
		return jsonify({"error": "No session cookie or header provided"}), 400

	connection = get_db_connection()
	if connection is None:
		return jsonify({"error": "Database connection failed"}), 500

	cursor = connection.cursor(dictionary=True)

	data = request.get_json()
	if not data or "email" not in data or "new_password" not in data:
		return jsonify({"error": "Email and new password are required"}), 400

	hashed_password = bcrypt.hashpw(data["new_password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

	try:
		cursor.execute("UPDATE users SET pass_hash = %s WHERE email = %s", (hashed_password, data["email"]))
		connection.commit()
		cursor.close()
		connection.close()
		return jsonify({"message": "Password reset successfully"}), 200
	except Error as e:
		cursor.close()
		connection.close()
		return jsonify({"error": f"Failed to reset password: {e}"}), 500


# Adding a new user to the database:
@app.route('/add_user', methods=['POST'])
def add_user():
	session_id = request.headers.get('session-id') or request.cookies.get('session_id')
	if not session_id:
		return jsonify({"error": "No session cookie or header provided"}), 400

	connection = get_db_connection()
	if connection is None:
		return jsonify({"error": "Database connection failed"}), 500

	data = request.get_json()
	if not data or 'full_name' not in data or 'email' not in data or 'is_admin' not in data:
		return jsonify({"error": "Missing required fields"}), 400

	full_name = data['full_name']
	email = data['email']
	is_admin = data['is_admin']
	authority = "Admin" if is_admin else "Reception"
	
	# Generate a default password and hash it
	default_password = "password123"  # Consider sending an email to reset this
	hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

	cursor = connection.cursor()
	try:
		cursor.execute("""
			INSERT INTO users (full_name, email, authority, pass_hash)
			VALUES (%s, %s, %s, %s)
		""", (full_name, email, authority, hashed_password))
		connection.commit()
		cursor.close()
		connection.close()
		return jsonify({"message": "User added successfully"}), 201
	except Error as e:
		cursor.close()
		connection.close()
		return jsonify({"error": f"Failed to add user: {e}"}), 500

@app.route('/check_admin', methods=['GET'])
def check_admin():
	session_id = request.headers.get('session-id') or request.cookies.get('session_id')
	if not session_id:
		return jsonify({"error": "No session cookie or header provided"}), 400

	connection = get_db_connection()
	if connection is None:
		return jsonify({"error": "Database connection failed"}), 500

	cursor = connection.cursor(dictionary=True)

	# Get user role from session
	cursor.execute("SELECT authority FROM users WHERE cookie = %s", (session_id,))
	user = cursor.fetchone()
	
	cursor.close()
	connection.close()

	if user is None:
		return jsonify({"error": "User not found!"}), 404

	if user["authority"] != "Admin":
		return jsonify({"error": "Not authorized"}), 403

	return jsonify({"message": "Authorized"}), 200

@app.route('/get_messages', methods=['GET'])
def get_messages():
    session_id = request.headers.get('session-id') or request.cookies.get('session_id')
    if not session_id:
        return jsonify({"error": "No session cookie or header provided"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)

    # Retrieve the logged-in user's user_id based on session ID
    cursor.execute("SELECT user_id FROM users WHERE cookie = %s", (session_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.close()
        connection.close()
        return jsonify({"error": "User not found!"}), 404

    user_id = user["user_id"]

    # Retrieve messages and determine who the other participant in the conversation is
    cursor.execute("""
        SELECT m.message_id,
               u.email AS sender_email,
               CASE 
                   WHEN m.receiver_id = %s THEN u.email  -- logged-in user is the receiver, show sender_email
                   WHEN m.sender_id = %s THEN u.email  -- logged-in user is the sender, show receiver_email
               END AS other_user_email,
               m.left_message, m.time_sent
        FROM messages m
        JOIN users u ON (m.sender_id = u.user_id OR m.receiver_id = u.user_id)
        WHERE ((m.receiver_id = %s AND m.sender_id != %s)  -- Only get messages where receiver is not the logged-in user
                OR (m.sender_id = %s AND m.receiver_id != %s))  -- Only get messages where sender is not the logged-in user
        ORDER BY m.time_sent DESC
    """, (user_id, user_id, user_id, user_id, user_id, user_id))

    messages = cursor.fetchall()

    # Now, let's get the count of unread messages for each user that has messaged the logged-in user
    cursor.execute("""
        SELECT m.sender_id, COUNT(*) AS unread_count
        FROM messages m
        WHERE m.receiver_id = %s AND m.is_read = 0
        GROUP BY m.sender_id
    """, (user_id,))

    unread_counts = cursor.fetchall()

    # Convert unread_counts into a dictionary for easy access
    unread_counts_dict = {str(unread_count["sender_id"]): unread_count["unread_count"] for unread_count in unread_counts}

    # Add the unread count to each user's message thread
    for message in messages:
        sender_user_email = message["other_user_email"]

        # Adding the unread count from the unread_counts_dict
        if sender_user_email in unread_counts_dict:
            message["unread_count"] = unread_counts_dict[sender_user_email]
        else:
            message["unread_count"] = 0

    cursor.close()
    connection.close()

    return jsonify({"messages": messages, "unreadCounts": unread_counts_dict}), 200

@app.route('/unread_messages_count', methods=['GET'])
def unread_messages_count():
    session_id = request.headers.get('session-id') or request.cookies.get('session_id')
    if not session_id:
        return jsonify({"error": "No session cookie or header provided"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT user_id FROM users WHERE cookie = %s", (session_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.close()
        connection.close()
        return jsonify({"error": "User not found!"}), 404

    user_id = user["user_id"]

    # Get the count of unread messages for the logged-in user
    cursor.execute("""
        SELECT COUNT(*) AS unread_count
        FROM messages
        WHERE receiver_id = %s AND is_read = 0
    """, (user_id,))

    unread_count = cursor.fetchone()["unread_count"]

    cursor.close()
    connection.close()

    return jsonify({"unread_messages_count": unread_count}), 200

@app.route('/get_chat_messages', methods=['GET'])
def get_chat_messages():
    session_id = request.headers.get('session-id')
    user_email = request.args.get('user_email')  # The person we're chatting with

    if not session_id or not user_email:
        return jsonify({'error': 'Invalid request'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get logged-in user's ID and email from session ID
    cursor.execute("SELECT user_id, email FROM users WHERE cookie = %s", (session_id,))
    logged_in_user = cursor.fetchone()

    if not logged_in_user:
        conn.close()
        return jsonify({'error': 'Invalid session'}), 401

    logged_in_id = logged_in_user['user_id']

    # Get the recipient's user_id using email
    cursor.execute("SELECT user_id FROM users WHERE email = %s", (user_email,))
    recipient = cursor.fetchone()

    if not recipient:
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    recipient_id = recipient['user_id']

    # Mark all messages as read where the logged-in user is the receiver
    cursor.execute("""
        UPDATE messages
        SET is_read = 1
        WHERE receiver_id = %s AND sender_id = %s AND is_read = 0
    """, (logged_in_id, recipient_id))

    # Fetch both sent & received messages between the two users
    cursor.execute("""
        SELECT 
            m.message_id, 
            m.sender_id, 
            m.receiver_id, 
            m.left_message, 
            m.time_sent,
            u1.email AS sender_email,
            u2.email AS receiver_email
        FROM messages m
        JOIN users u1 ON m.sender_id = u1.user_id
        JOIN users u2 ON m.receiver_id = u2.user_id
        WHERE 
            (m.sender_id = %s AND m.receiver_id = %s) 
            OR 
            (m.sender_id = %s AND m.receiver_id = %s)
        ORDER BY m.time_sent ASC
    """, (logged_in_id, recipient_id, recipient_id, logged_in_id))

    messages = cursor.fetchall()

    conn.commit()  # Commit the update to the messages

    conn.close()

    return jsonify({'messages': messages})


@app.route('/get_user_email', methods=['GET'])
def get_user_email():
    session_id = request.headers.get('session-id') or request.cookies.get('session_id')
    if not session_id:
        return jsonify({"error": "No session cookie or header provided"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)

    # Retrieve the logged-in user's email based on session ID
    cursor.execute("SELECT email FROM users WHERE cookie = %s", (session_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.close()
        connection.close()
        return jsonify({"error": "User not found!"}), 404

    cursor.close()
    connection.close()

    # Return the email of the logged-in user
    return jsonify({"email": user["email"]}), 200

@app.route('/check_password', methods=['POST'])
def check_password():
    session_id = request.headers.get('session-id') or request.cookies.get('session_id')
    if not session_id:
        return jsonify({"error": "No session cookie or header provided"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)

    data = request.get_json()
    if not data or "password" not in data:
        cursor.close()
        connection.close()
        return jsonify({"error": "Password is required"}), 400

    # Retrieve the user's password hash from the database based on the session ID
    cursor.execute("SELECT pass_hash FROM users WHERE cookie = %s", (session_id,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user and bcrypt.checkpw(data["password"].encode('utf-8'), user['pass_hash'].encode('utf-8')):
        return jsonify({"message": "Password is correct"}), 200
    else:
        return jsonify({"error": "Incorrect password"}), 401


if __name__ == '__main__':
	get_db_connection()  # Ensure the connection is established at startup
	app.run(host='0.0.0.0', port=5007)