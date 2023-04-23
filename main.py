import socket
import struct
import threading

servers_dict = {}
clients_dict = {}

addresses_arr = [('127.0.0.1', 5050), ('127.0.0.1', 6060), ('127.0.0.1', 7070), ('127.0.0.1', 8080), ('127.0.0.1', 9090)]
serverPort = int(input('Please choose a port to listen to: '))


def convertData(messageType, subtype, data, pData=b''):
    # function that convert the message to required format
    msg = struct.pack('>bbhh', messageType, subtype, len(data) + len(pData), len(pData))
    return msg + pData + data


def connect_function(addr):
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        conn.bind(('0.0.0.0', serverPort))
        conn.connect(addr)
        # try to connect to other servers
        if addr[1] != serverPort:
            print('Connected to ', addr)
        servers_dict[addr] = conn  # while the connection success add this server to your dict
        request_msg = convertData(messageType=2, subtype=0, data=b'')  # send message to say that I'm a server
        conn.send(request_msg)
        request_msg = convertData(messageType=0, subtype=0, data=b'')
        # send message to request the list of other servers he has for connecting them to
        conn.send(request_msg)
        request_msg = convertData(messageType=0, subtype=1, data=b'')
        # send message to request the list of other users he has for connecting them to
        conn.send(request_msg)
        threading.Thread(target=respond_function, args=(conn, addr)).start()
        # start a thread to get any respond message
    except ConnectionRefusedError:
        pass
    except OSError:
        pass


def respond_function(conn_socket, conn_address):
    try:
        while True:
            data = conn_socket.recv(6)
            if not data:
                break
            type, subtype, msglen, sublen = struct.unpack('>bbhh', data)
            message = conn_socket.recv(msglen)
            if type == 0:  # get information about connection
                if subtype == 0:  # ask for servers dict
                    serverIConnectTO = '\0'.join(f'{ip}:{port}' for ip, port in servers_dict.keys())
                    reply = convertData(messageType=1, subtype=0, data=serverIConnectTO.encode())
                    conn_socket.send(reply)
                elif subtype == 1:  # ask for users dict
                    username = '\0'.join(conn_info[0] for temp1, conn_info in clients_dict)
                    reply = convertData(messageType=1, subtype=1, data=username.encode())
                    conn_socket.send(reply)
            elif type == 1:  # respond to information request
                if subtype == 0:  # send servers information
                    if msglen > 0:
                        for serverAddr in message.decode().split('\0'):
                            ip, port = serverAddr.split(':')
                            addr = ip, int(port)
                            if port != serverPort:
                                threading.Thread(target=connect_function, args=(addr,)).start()
                                # connect to each server who connected to this server I just connect to
                elif subtype == 1:  # send users information
                    for username in message.decode().split('\0'):
                        print(username)
            elif type == 2:  # define username for connect
                if subtype == 0:  # server connection
                    servers_dict[conn_address] = conn_socket  # add the server to the dictionary as: {address->socket}
                elif subtype == 1:  # client connection
                    clients_dict[conn_address] = (message.decode(), conn_socket)
                    # add the user to the dictionary as: {address->(name,socket)}
            elif type == 3:  # send message
                name, message = message[0:sublen], message[sublen:]  # split message data
                if conn_address in clients_dict:  # if this is a client
                    sender_name = clients_dict[conn_address][0]
                    name = sender_name.encode() + b'\0' + name # split and slice its name and the message to send
                    for temp1, socket in servers_dict.items():  # broadcast to all servers
                        reply = convertData(messageType=3, subtype=0, data=message, pData=name)
                        socket.send(reply)
                """ explanation: when the message is sent as broadcast to all servers the type of the message is 3 than we
                                    want that the servers which got the message will send it to their own clients so we run in FOR LOOP to send the message 
                                    for each server's client list(cause when the message-type 3 will be sent to server, 
                                    he will come to this scope of code (the following for loop->)"""
                for client_addr, conne in clients_dict.items():
                    client_sock = conne[1]
                    reply = convertData(messageType=3, subtype=0, data=message, pData=name)
                    client_sock.send(reply)

            elif type == 4:  # echo message
                reply = convertData(messageType=4, subtype=0, data=b'')
                conn_socket.send(reply)

        conn_socket.close()
    except ConnectionResetError:
        pass
    except OSError:
        pass


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', serverPort))
    sock.listen(1)
    for address in addresses_arr:
        if address[1] != serverPort:
            # check for all of the existing servers (except of himself) if he can connect to one of them
            threading.Thread(target=connect_function, args=(address,)).start()
            # thread that start on function connectToExistServer to try connect the servers (check the notes there..)
    while True:
        conn, client_address = sock.accept()
        print('Got a new connection from ', client_address)
        threading.Thread(target=respond_function, args=(conn, client_address)).start()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

