from socket import *
import sys
import os
import select

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server]')
    sys.exit(2)

# The proxy server is listening at 8888
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind((sys.argv[1], 8888))
tcpSerSock.listen(100)

# List to keep track of socket descriptors
sockets_list = [tcpSerSock]

print('Ready to serve...')

while True:
    # Get the list of sockets which are ready to be read
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # If the notified socket is the server socket, it means a new connection is coming in
        if notified_socket == tcpSerSock:
            tcpCliSock, addr = tcpSerSock.accept()
            print('Received a connection from:', addr)
            sockets_list.append(tcpCliSock)
        else:
            # Existing socket is sending data
            message = notified_socket.recv(4096).decode()
            if not message:
                # If no data is received, close the connection
                print('Closing connection from:', notified_socket.getpeername())
                sockets_list.remove(notified_socket)
                notified_socket.close()
                continue

            print(message)
            filename = message.split()[1][1:]
            filetouse = "cache/" + filename.replace('/', '_')
            fileExist = False

            try:
                with open(filetouse, "rb") as f:
                    outputdata = f.read()
                    fileExist = True

                notified_socket.send(b"HTTP/1.0 200 OK\r\n")
                notified_socket.send(b"Content-Type:text/html\r\n\r\n")
                notified_socket.send(outputdata)

            except IOError:
                if not fileExist:
                    try:
                        hostn = filename.split('/')[0]
                        c = socket(AF_INET, SOCK_STREAM)
                        c.connect((hostn, 80))
                        c.sendall(message.encode())

                        response = b""
                        while True:
                            data = c.recv(4096)
                            if not data:
                                break
                            response += data
                        c.close()

                        os.makedirs("cache", exist_ok=True)
                        with open(filetouse, "wb") as cache_file:
                            cache_file.write(response)

                        notified_socket.sendall(response)
                    except Exception as e:
                        print("Illegal request", e)
                else:
                    notified_socket.send(b"HTTP/1.0 404 sendErrorErrorError\r\n")
                    notified_socket.send(b"Content-Type:text/html\r\n")
                    notified_socket.send(b"\r\n")

            # Close the connection after handling the request
            sockets_list.remove(notified_socket)
            notified_socket.close()

    # Handle exception sockets
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        notified_socket.close()

tcpSerSock.close()