import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 9999))

def receive_messages():
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            if msg:
                print(msg)
            else:
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def request_chat_history():
    receiver = input("Enter the username of the chat history you want to retrieve: ")
    client.send(f"/history {receiver}".encode('utf-8'))

# Start a thread to listen for messages from the server
threading.Thread(target=receive_messages, daemon=True).start()

# Main loop for sending messages and requesting history
while True:
    message = input("Message: ")
    if message.startswith("/history"):
        request_chat_history()
    else:
        client.send(message.encode('utf-8'))
    if message.lower() == "quit":
        break
    #else:


