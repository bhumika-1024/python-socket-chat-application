import socket
import threading
from datetime import datetime

def get_time():
    return datetime.now().strftime("[%H:%M:%S]")

def receive_messages(client_socket):
    # Runs in a separate thread, continuously listens for incoming messages
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print("\n" + message)
        except Exception as e:
            # Socket closed or server disconnected
            print("Connection closed.")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 50000
    client_socket.connect((host, port))

    # Keep asking until server confirms username is available
    while True:
        username = input("Enter username: ")
        client_socket.sendall(username.encode('utf-8'))
        print("Waiting for server response...")
        response = client_socket.recv(1024).decode('utf-8')

        if response == "USERNAME_TAKEN":
            print("Username already exists. Try another.")
            continue

        print("Username accepted.")
        break

    # Daemon thread — auto-killed when main program exits
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()
    print("Enter message or type '/quit' to leave chat")
    
    while True:
        
        message = input()

        if message.lower() == '/quit':
            print("Leaving chat...")
            client_socket.close()
            break

        full_message = f"{username}: {message}"
        # Print locally with timestamp since server only stamps messages for other clients
        print(f"{get_time()} {full_message}")
        client_socket.sendall(full_message.encode("utf-8"))

if __name__ == "__main__":
    main()