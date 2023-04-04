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
    def wait_for_conns():
        # Start a new thread to wait for connections
        while True:
            conn, addr = server_socket.accept()
            data_protocol = conn.recv(1)
            type_, sub_type, len_, sub_len = data_protocol[0], data_protocol[1], data_protocol[2], data_protocol[3]
            if type_ == 0:
                servers_dict[addr[0]] = addr[1]
                print(f'Connected to {addr}')
                if sub_type == 0:
                    for key, value in servers_dict.items():
                        # send the key as a string
                        server_socket.sendall(str(key).encode())

                        # send a separator character
                        server_socket.sendall(':'.encode())

                        # send the value as a string
                        servers_dict.sendall(str(value).encode())

                        # send a delimiter character
                        servers_dict.sendall('\0'.encode())
                elif sub_type == 1:
                    for key, value in clients_dict.items():
                        # send the key as a string
                        server_socket.sendall(str(key).encode())

                        # send a separator character
                        server_socket.sendall('='.encode())

                        # send the value as a string
                        servers_dict.sendall(str(value).encode())

                        # send a delimiter character
                        servers_dict.sendall(';'.encode())

            elif type_ == 1:
                server_socket.recv(1024)







def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while True:
        port_index = int(input(f"Choose a port index between 0 and {len(ports) - 1}: "))
        if port_index not in range(len(ports)):
            print("Invalid port index")
            exit(1)
        port = ports[port_index]
        server_start(port)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
