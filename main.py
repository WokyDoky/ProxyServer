import socket

def start_proxy_server(host='127.0.0.1', port=8888):
    # Create a socket object
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the host and port
    proxy_socket.bind((host, port))
    
    # Listen for incoming connections
    proxy_socket.listen(5)
    print(f"Proxy server is listening on {host}:{port}...")
    
    while True:
        # Accept a connection from the client
        client_socket, client_address = proxy_socket.accept()
        print(f"Accepted connection from {client_address}")
        
        # Receive the HTTP request from the client
        request = client_socket.recv(4096).decode('utf-8')
        print(f"Received request:\n{request}")
        
        # Extract the destination server and path from the request
        first_line = request.split('\n')[0]
        url = first_line.split(' ')[1]
        
        # Parse the URL to get the host and path
        http_pos = url.find("://")
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos + 3):]
        
        port_pos = temp.find(":")
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)
        
        webserver = ""
        port = -1
        if port_pos == -1 or webserver_pos < port_pos:
            port = 80
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]
        
        path = temp[webserver_pos:]
        
        # Create a socket to connect to the destination server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((webserver, port))
        
        # Forward the request to the destination server
        server_socket.send(request.encode())
        
        # Receive the response from the destination server
        response = server_socket.recv(4096)
        
        # Forward the response back to the client
        client_socket.send(response)
        
        # Close the sockets
        server_socket.close()
        client_socket.close()

if __name__ == "__main__":
    start_proxy_server()
