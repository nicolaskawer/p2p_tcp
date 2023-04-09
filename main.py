# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import threading
import socket
servers_dict = {}
clients_dict = {}
my_data_protocol = []
ports = [1000, 1001, 1002, 1003, 1004]


def server_start(port_input):
    # Create a socket and start listening on the port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port_input))
    server_socket.listen()
    while True:
        def wait_for_conns():
            while True:

                conn, addr = server_socket.accept()
                # Receive the first 6 bytes of the data from the connection
                data_protocol = conn.recv(6)
                # Extract the data type, subtype, length of the data and the length of the subtype from the received data
                # type_- first byte represents the type of data
                # sub_type -second byte represents the subtype of data
                # len_- third and fourth bytes represent the length of the data in bytes, converted to integer using big-endian byte order
                # sub_len - fifth and sixth bytes represent the length of the subtype in bytes, converted to integer using big-endian byte order
                type_, sub_type, len_, sub_len = data_protocol[0], data_protocol[1], int.from_bytes(data_protocol[2:4],'big'), int.from_bytes(data_protocol[4:6],'big')
                for p in ports:
                    if p != port_input:
                        try:
                            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            client_socket.connect(('127.0.0.1', p))
                            client_socket.send("Hello".encode())
                            data = client_socket.recv(1024).decode()
                            if data == 'World':
                                print(f'{port_input} successfully connect to {p}.')
                        except ConnectionRefusedError:
                            print(f"Connection refused on port {p}")
                if type_ == 0:
                    servers_dict[addr[0]] = addr[1]
                    print(f'Connected to {addr}')
                    # subtype 0: Information about servers that the server is connected to
                    if sub_type == 0:
                        servers_str = ""
                        for key, value in servers_dict.items():
                            servers_str += f"{key}:{value}\0"
                        # create a bytes object to send over the socket
                        # the first byte is the message type (1), the second byte is the message subtype (0)
                        # the next two bytes are the length of the message (in bytes), in big-endian format
                        # the following two bytes are reserved for future use and are set to 0
                        # the remaining bytes are the message content (the server key-value pairs), encoded as bytes
                        server_socket.sendall(bytes([1, 0]) + len(servers_str).to_bytes(2, 'big') + bytes([0, 0]) + servers_str.encode())
                    elif sub_type == 1:
                        # subtype 1: Information about users who are connected to this server itself
                        clients_str = ""
                        for key in clients_dict.keys():
                            clients_str += f"{key}\0"
                            # create a bytes object to send over the socket
                            # the first byte is the message type (1), the second byte is the message subtype (1)
                            # the next two bytes are the length of the message (in bytes), in big-endian format
                            # the following two bytes are reserved for future use and are set to 0
                            # the remaining bytes are the message content (the client usernames), encoded as bytes
                        server_socket.sendall(bytes([1, 1]) + len(clients_str).to_bytes(2, 'big') + bytes([0, 0]) + clients_str.encode())

                elif type_ == 1:
                    data_str = data_protocol.decode()
                    if sub_type == 0:
                        # split the string into key-value pairs
                        pairs = data_str.split('\0')
                        print(f'server: {pairs} is received')
                        for pair in pairs:
                            # split each pair into key and value
                            key, value = pair.split(':')
                        # add the server to the list of servers
                        servers_dict[key] = value
                            # split the string into client IDs
                    elif sub_type == 1:
                        client_ids = data_str.split('\0')
                        print(f'client: {client_ids} is received')
                        for client_id in client_ids:
                            # add the client to the list of clients
                            clients_dict[client_id] = server_socket

                elif type_ == 2:
                    if sub_type == 0: # server connection
                        pass # do nothing for now
                    elif sub_type == 1: # user connection
                        username = data_protocol[6:].decode()
                        clients_dict[username] = server_socket
                        print(f"{username} connected")



                elif type_ == 3:
                    username_len = sub_len
                    username = conn.recv(username_len).decode()
                    message_len = len_ - username_len
                    message = conn.recv(message_len).decode()
                    print(f"{username}: {message}")
                    # add sender's username and forward message to recipient or other server
                    if username in clients_dict.values():
                        clients_dict[username].sendall(bytes([1, 3]) + bytes([0, len(username)]) + username.encode() + message.encode())
                    else:
                        for server_address, server_name in servers_dict.items():
                            forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            forward_socket.connect(server_address)
                            forward_socket.sendall(bytes([1, 3]) + bytes([0, len(server_name + 'b\0' + username)]) + (server_name + 'b\0' + username).encode() + message.encode())
                            forward_socket.close()

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

        port_index = int(input(f"Choose a port index between 0 and {len(ports) - 1}: "))
        if port_index not in range(len(ports)):
            print("Invalid port index")
            exit(1)
        port = ports[port_index]
        server_start(port)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
