import sqlite3

def list_users():
    # Connect to the SQLite database
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()

    # Query all users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # Print user details
    print("Registered users:")
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}")

    # Close the connection
    conn.close()

if __name__ == "__main__":
    list_users()
