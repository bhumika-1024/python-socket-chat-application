import socket
import threading
from datetime import datetime

# Stores all currently connected client sockets
clients = []

# Maps client socket -> username
usernames = {}

def get_time():
    return datetime.now().strftime("[%H:%M:%S]")

def broadcast(message, sender_socket):
    # Send message to every client except the sender
    for client in clients:
        if client != sender_socket:
            try:
                client.sendall(message)
            except Exception as e:
                print("Broadcast error:", e)
                if client in clients:
                    clients.remove(client)

def handle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)

            # Client disconnected
            if not data:
                break

            message = data.decode('utf-8')

            stamped = f"{get_time()} {message}"

            print(stamped)
            broadcast(stamped.encode('utf-8'), client_socket)

        except Exception as e:
            print(f"{usernames.get(client_socket, 'Unknown')} disconnected: {e}")
            break

    username = usernames.get(client_socket, "Unknown")

    # Notify remaining users when someone leaves
    leave_message = f"{get_time()} {username} left the chat"

    print(leave_message)
    broadcast(leave_message.encode('utf-8'), client_socket)

    if client_socket in clients:
        clients.remove(client_socket)

    if client_socket in usernames:
        del usernames[client_socket]

    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allows immediate server restart without waiting for port release
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host = '127.0.0.1'
    port = 50000

    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()

        print(f"Accepted connection from {client_address}")

        # Keep asking until a unique username is provided
        while True:
            username = client_socket.recv(1024).decode('utf-8')

            if username not in usernames.values():
                client_socket.sendall("USERNAME_ACCEPTED".encode('utf-8'))
                break
            else:
                client_socket.sendall("USERNAME_TAKEN".encode('utf-8'))

        usernames[client_socket] = username

        join_message = f"{get_time()} {username} joined the chat"

        print(join_message)

        clients.append(client_socket)

        # Inform existing users about the new participant
        broadcast(join_message.encode('utf-8'), client_socket)

        # Handle each client in a separate thread
        client_handler = threading.Thread(
            target=handle_client,
            args=(client_socket,)
        )

        client_handler.daemon = True
        client_handler.start()

if __name__ == "__main__":
    main()