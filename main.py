import socket
import struct
import threading

servers_dict = {} # [addr -> socket_object]
clients_dict = {} # [addr -> (name, socket_object)]

addrs = [('127.0.0.1', 5050), ('127.0.0.1', 6060), ('127.0.0.1', 7070), ('127.0.0.1', 8080), ('127.0.0.1', 9090)]
serverPort = int(input('Please choose a port to listen on: '))


def convertData(messageType, subtype, data, pData=b''):
    msg = struct.pack('>bbhh', messageType, subtype, len(data) + len(pData), len(pData))
    print(msg + pData + data)
    return msg + pData + data


def connectToExistServer(addr):
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        conn.bind(('0.0.0.0', serverPort))
        conn.connect(addr)
        # try to connect to other servers
        print('Connected to ', addr)
        servers_dict[addr] = conn #while the connection success add this server to your dict
        request = convertData(messageType=2, subtype=0, data=b'')  # send message to say that I'm a server
        conn.send(request)
        request = convertData(messageType=0, subtype=0, data=b'')
        # send message to request the list of other servers he has for connecting them to
        conn.send(request)
        threading.Thread(target=respondMessage, args=(conn, addr)).start()
        # start a thread to get any respond message
    except ConnectionRefusedError:
        pass
    except OSError:
        pass


def respondMessage(conn_socket, conn_address):
    try:
        while True:
            data = conn_socket.recv(6)
            if not data:
                break
            type, subtype, msglen, sublen = struct.unpack('>bbhh', data)
            message = conn_socket.recv(msglen)
            if type == 0: # receive request for users list
                if subtype == 0:
                    serverIConnectTO = '\0'.join(f'{ip}:{port}' for ip, port in servers_dict.keys())
                    reply = convertData(messageType=1, subtype=0, data=serverIConnectTO.encode())
                    conn_socket.send(reply)
                elif subtype == 1:
                    username = '\0'.join(conn_info[0] for temp1, conn_info in clients_dict)
                    reply = convertData(messageType=1, subtype=1, data=username.encode())
                    conn_socket.send(reply)

            elif type == 1: # receive response for users list request
                if subtype == 0:
                    if msglen > 0:
                        for serverAddr in message.decode().split('\0'):
                            ip, port = serverAddr.split(':')
                            addr = ip, int(port)
                            if port != serverPort:
                                threading.Thread(target=connectToExistServer, args=(addr,)).start()
                elif subtype == 1:
                    for username in message.decode().split('\0'):
                        print(username)

            elif type == 2: # login as name or as server
                if subtype == 0:
                    servers_dict[conn_address] = conn_socket
                elif subtype == 1:
                    clients_dict[conn_address] = (message.decode(), conn_socket)

            elif type == 3: # message
                name, message = message[0:sublen], message[sublen:] # split message data
                if conn_address in clients_dict: # is a client
                    senderName = clients_dict[conn_address][0]
                    name = senderName.encode() + b'\0' + name
                    for temp1, socket in servers_dict.items(): # broadcast to all servers
                        reply = convertData(messageType=3, subtype=0, data=message, pData=name)
                        socket.send(reply)

                for client_addr, conne in clients_dict.items():
                        client_sock = conne[1]
                        reply = convertData(messageType=3, subtype=0, data=message, pData=name)
                        client_sock.send(reply)


        conn_socket.close()
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

    for addr in addrs:
        if addr[1] != serverPort: # check for all of the existing servers (except of himself) if he can connect to one of them
            threading.Thread(target=connectToExistServer, args=(addr,)).start()
            #thread that start on function connectToExistServer to try connect the servers (check the notes there..)
    print('Listening to port ', serverPort)
    while True:
        conn, client_address = sock.accept()
        print('New connection from ', client_address)
        threading.Thread(target=respondMessage, args=(conn, client_address)).start()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

