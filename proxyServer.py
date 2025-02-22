from socket import *
import sys
import os

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server]')
    sys.exit(2)

# The proxy server is listening at 8888
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind((sys.argv[1], 8888))
tcpSerSock.listen(100)

while True:
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)

    message = tcpCliSock.recv(4096).decode()
    if not message:
        tcpCliSock.close()
        continue

    print(message)
    filename = message.split()[1][1:]
    filetouse = "cache/" + filename.replace('/', '_')
    fileExist = False

    try:
        with open(filetouse, "rb") as f:
            outputdata = f.read()
            fileExist = True

        tcpCliSock.send(b"HTTP/1.0 200 OK\r\n")
        tcpCliSock.send(b"Content-Type:text/html\r\n\r\n")
        tcpCliSock.send(outputdata)

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

                tcpCliSock.sendall(response)
            except Exception as e:
                print("Illegal request", e)
        else:
            tcpCliSock.send(b"HTTP/1.0 404 Not Found\r\n")
            tcpCliSock.send(b"Content-Type:text/html\r\n\r\n")

    tcpCliSock.close()
tcpSerSock.close()
