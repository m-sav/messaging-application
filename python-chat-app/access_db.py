import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('chat.db')
cursor = conn.cursor()

# Example: Fetch all users
print("Fetching all users:")
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
for user in users:
    print(user)

# Example: Fetch all messages
print("\nFetching all messages:")
cursor.execute("SELECT * FROM messages")
messages = cursor.fetchall()
for message in messages:
    print(message)

# Close the connection
conn.close()
