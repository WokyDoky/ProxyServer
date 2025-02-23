from socket import *
import sys
import select

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server]')
    sys.exit(2)

# The proxy server is listening at 8888
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind((sys.argv[1], 8888))
tcpSerSock.listen(100)

# List to keep track of socket descriptors
socket_list = [tcpSerSock]

print('Ready to serve...')

while True:
    # Use select to monitor sockets for incoming data
    read_sockets, _, exception_sockets = select.select(socket_list, [], socket_list)

    for notified_socket in read_sockets:
        # If the notified socket is the server socket, it means a new connection is incoming
        if notified_socket == tcpSerSock:
            tcpCliSock, addr = tcpSerSock.accept()
            print('Received a connection from:', addr)
            socket_list.append(tcpCliSock)
        else:
            # Existing socket is sending data
            try:
                # Receive the HTTP request from the client
                message = notified_socket.recv(4096).decode('utf-8')
                print(message)

                # Extract the hostname and path from the request
                first_line = message.split('\n')[0]
                url = first_line.split(' ')[1]

                # Parse the URL to extract the hostname and path
                http_pos = url.find("://")
                if http_pos == -1:
                    temp = url
                else:
                    temp = url[(http_pos + 3):]  # Skip "http://" or "https://"

                # Find the position of the first "/" to separate hostname and path
                webserver_pos = temp.find("/")
                if webserver_pos == -1:
                    webserver_pos = len(temp)

                # Extract the hostname and path
                webserver = temp[:webserver_pos]
                path = temp[webserver_pos:]

                # Default port is 80 for HTTP
                port = 80

                # Check if the hostname contains a port (e.g., "example.com:8080")
                port_pos = webserver.find(":")
                if port_pos != -1:
                    port = int(webserver[(port_pos + 1):])
                    webserver = webserver[:port_pos]

                print(f"Connecting to host: {webserver}, port: {port}, path: {path}")

                # Create a socket to connect to the destination server
                c = socket(AF_INET, SOCK_STREAM)
                c.connect((webserver, port))

                # Forward the request to the destination server
                request = f"GET {path} HTTP/1.1\r\nHost: {webserver}\r\nConnection: close\r\n\r\n"
                c.send(request.encode())

                # Receive the response from the destination server
                response = b""
                while True:
                    data = c.recv(4096)
                    if not data:
                        break
                    response += data

                # Forward the response back to the client
                notified_socket.send(response)

                # Close the connection to the destination server
                c.close()

            except Exception as e:
                print(f"Illegal request: {e}")
                # Send a 500 Internal Server Error response to the client
                notified_socket.send(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
                notified_socket.send(b"<html><body><h1>500 Internal Server Error</h1></body></html>")

            # Close the client socket and remove it from the list
            notified_socket.close()
            socket_list.remove(notified_socket)

    # Handle any socket exceptions
    for notified_socket in exception_sockets:
        socket_list.remove(notified_socket)
        notified_socket.close()