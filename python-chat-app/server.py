import socket
import threading
import sqlite3
from datetime import datetime
import signal
import sys
import re

MAX_MESSAGE_LENGTH = 500

# Initialize Database
conn = sqlite3.connect('chat.db', check_same_thread=False)
cursor = conn.cursor()

# Create Tables
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT UNIQUE NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    sender_id INTEGER, 
                    receiver_id INTEGER, 
                    content TEXT, 
                    timestamp TEXT,
                    FOREIGN KEY (sender_id) REFERENCES users(id), 
                    FOREIGN KEY (receiver_id) REFERENCES users(id))''')

cursor.execute("DELETE FROM users")
cursor.execute("DELETE FROM messages")

conn.commit()

clients = {}

def validate_send_message(message):
    # Check if the /send message consists of a minimum of three elements, e.g. "/send maria hi"
    parts = message.split(' ', 2)
    if len(parts) < 3:
        return False
    to_return = parts[0] == '/send' and len(parts[1]) > 0 and len(parts[2]) > 0
    return to_return

def is_valid_message_content(content):
    # Reject messages that are empty or consist only of whitespace.
    return len(content.strip()) > 0

def is_safe_message(message):
    # Simple check to disallow potentially harmful characters or commands
    forbidden_characters = re.compile(r'[^\w\s,.!?]')
    return not forbidden_characters.search(message)

def is_message_length_valid(message):
    # Prevent excessively long messages
    return len(message) <= MAX_MESSAGE_LENGTH

def broadcast(sender, receiver, message):
    if receiver in clients:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{timestamp}] {sender}: {message}"
        clients[receiver].send(formatted_message.encode('utf-8'))
    else:
        print(f"User {receiver} is not online. Message will be stored.")
def handle_client(client_socket, username):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8').strip()
            
            if message:

                if message.startswith('/send') :
                    
                    try:
                        _, receiver_username, msg_content = message.split(' ', 2)
                    except Exception as e:
                        print(e)
                        if not validate_send_message(message) or not is_safe_message(msg_content) or not is_message_length_valid(msg_content) or not is_valid_message_content(msg_content):
                            client_socket.send(f"Wrong message format. Try again.".encode('utf-8'))
                    
                        client_socket.send(f"Enter a new message".encode('utf-8'))

                        continue
                   

                    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
                    sender_id = cursor.fetchone()[0]
                    cursor.execute("SELECT id FROM users WHERE username=?", (receiver_username,))
                    receiver = cursor.fetchone()

                    if receiver:
                        receiver_id = receiver[0]
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO messages (sender_id, receiver_id, content, timestamp) VALUES (?, ?, ?, ?)", 
                                       (sender_id, receiver_id, msg_content, timestamp))
                        conn.commit()

                        broadcast(username, receiver_username, msg_content)
                        client_socket.send(f"[{timestamp}] Message sent to {receiver_username}.".encode('utf-8'))
                    else:
                        client_socket.send(f"User {receiver_username} does not exist. Try again or use /send <username> <message>.".encode('utf-8'))
                        continue

                elif message.startswith('/history'):
                    _, receiver_username = message.split(' ', 1)
                    history = get_chat_history(username, receiver_username)
                    if history:
                        for msg in history:
                            client_socket.send(f"{msg}\n".encode('utf-8'))
                        client_socket.send("End of history.".encode('utf-8'))
                    else:
                        client_socket.send(f"No chat history found with {receiver_username}.".encode('utf-8'))

                # Prompt for new command
                client_socket.send("Enter a new command below.".encode('utf-8'))

            else:
                raise Exception("Client disconnected")
        except Exception as e:
            print(f"Error: {e}")
            clients.pop(username, None)
            client_socket.close()
            break

def client_registration(client_socket):
    client_socket.send("Enter your username: ".encode('utf-8'))
    username = client_socket.recv(1024).decode('utf-8')
    
    try:
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
    except sqlite3.IntegrityError:
        client_socket.send(f"Username {username} is already taken.".encode('utf-8'))
        client_socket.close()
        return
    
    clients[username] = client_socket
    client_socket.send(f"Welcome {username}!\nUse /send <username> <message> to send a message.\nUse /history to retrieve chat history.".encode('utf-8'))
    return username

def get_chat_history(sender_username, receiver_username):
    cursor.execute("SELECT id FROM users WHERE username=?", (sender_username,))
    sender_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM users WHERE username=?", (receiver_username,))
    receiver_id = cursor.fetchone()[0]

    cursor.execute("SELECT sender_id, content, timestamp FROM messages WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?) ORDER BY timestamp", 
                   (sender_id, receiver_id, receiver_id, sender_id))
    messages = cursor.fetchall()

    history = []
    for message in messages:
        sender_id, content, timestamp = message
        cursor.execute("SELECT username FROM users WHERE id=?", (sender_id,))
        sender_username = cursor.fetchone()[0]
        history.append(f"[{timestamp}] {sender_username}: {content}")

    return history


def shutdown_server(signal, frame):
    print("Shutting down server...")
    cursor.execute("DELETE FROM messages")  # Clear chat history
    cursor.execute("DELETE FROM users")     # Clear users
    conn.commit()
    conn.close()
    print("Database cleared. Server shutting down.")
    sys.exit(0)

# Register signal handler for graceful shutdown
signal.signal(signal.SIGINT, shutdown_server)

# Main Server Code
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9999))
server.listen()

print("Server started and listening for connections...")

while True:
    client_socket, addr = server.accept()
    print(f"Accepted connection from {addr}")
    
    username = client_registration(client_socket)
    if username:
        client_thread = threading.Thread(target=handle_client, args=(client_socket, username))
        client_thread.start()
