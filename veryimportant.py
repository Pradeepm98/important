import socket

def handle_client(client_socket):
    request = client_socket.recv(4096)
    first_line = request.split(b'\n')[0]
    method = first_line.split(b' ')[0]

    if method == b'CONNECT':
        # Extract the requested host and port
        host_port = first_line.split(b' ')[1].decode('utf-8')
        host, port = host_port.split(':')
        
        # Create a connection to the requested server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, int(port)))
        
        # Send the client a success response
        client_socket.send(b'HTTP/1.1 200 OK\r\n\r\n')
        
        # Start forwarding data between client and server
        forward_data(client_socket, server_socket)
        forward_data(server_socket, client_socket)
    else:
        # Handle regular HTTP requests
        host = first_line.split(b' ')[1].decode('utf-8')
        
        # Create a connection to the target server on port 80
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, 443))
        
        # Forward the client's request to the server
        server_socket.send(request)
        
        # Start forwarding data between client and server
        forward_data(client_socket, server_socket)
        forward_data(server_socket, client_socket)

def forward_data(source_socket, destination_socket):
    source_socket.setblocking(False)
    destination_socket.setblocking(False)
    buffer_size = 4096

    while True:
        try:
            data = source_socket.recv(buffer_size)
            if data:
                destination_socket.send(data)
            else:
                break
        except socket.error:
            pass

        try:
            data = destination_socket.recv(buffer_size)
            if data:
                source_socket.send(data)
            else:
                break
        except socket.error:
            pass



def start_proxy_server():
    proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_server.bind(('0.0.0.0', 8097))
    proxy_server.listen(5)
    print('Proxy server listening on port 8000')

    while True:
        client_socket, client_address = proxy_server.accept()
        print(f'Received connection from {client_address[0]}:{client_address[1]}')
        handle_client(client_socket)

if __name__ == "__main__":
    start_proxy_server()
