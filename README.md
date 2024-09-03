# Messaging Application

## Description
This is a simple messaging application built in Python. It allows users to register, send messages to other users, and retrieve chat history. The backend is implemented using Python's socket library and stores data in an SQLite database.

## How to Run

### Start the Server
Open a terminal and run `server.py` to start the server. The server will listen for incoming connections from clients.

    python server.py
    
### Start the Client
Open another terminal and run `client.py` to start a client instance.

    python client.py

### Register Users
When `client.py` starts, you will be prompted to enter a username. Register a user with a unique name. To register additional users, open a new terminal and run another instance of `client.py`.


### Interact with the Application

#### Send Messages
To send a message from one user to another, use the `/send` command followed by the recipient's username and the message. For example:

    /send <recipient_username> hi

#### Retrieve Chat History
To view the chat history with another user, use the `/history` command and provide the desired username when prompted:

    /history <other_username>
    
#### Quit Chat Option

    quit
    
You can open as many client terminals as needed and perform similar operations with different users.

## Accessing the Database

The repository includes a script named `access_db.py` that you can run separately to interact with the SQLite database. This script connects to the `chat.db` database and allows you to fetch and print the tables' contents. It is useful for inspecting the data directly.

**Note:** Every time `server.py` is started, the database is refreshed, and all existing data is deleted.

## Libraries Used
- `socket` for networking
- `threading` for concurrent client handling
- `sqlite3` for database management
- `re` for basic message validation
- `datetime` for timestamping messages
- `signal` and `sys` for graceful shutdown of the server

## Features
- **User Registration:** Users can register with a unique username.
- **Send Messages:** Users can send messages to other registered users.
- **Retrieve Chat History:** Users can request chat history with another user.

## Validation and Error Handling
- Messages are validated for format, content, safety, and length.
- Error handling for invalid message formats and disconnected clients.

## Future Improvements and Known Issues
- Handle more edge-cases.
- Implement more complex features such as:
  - Group chat
  - Chatting from different devices
  - Include a frontend interface
- Only basic validation is implemented. More comprehensive checks and features may be required.
- The application does not handle concurrent modifications to the database.
