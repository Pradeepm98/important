import socket
import threading

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
        threading.Thread(target=forward_data, args=(client_socket, server_socket)).start()
        threading.Thread(target=forward_data, args=(server_socket, client_socket)).start()
    else:
        # Handle regular HTTP requests
        host = first_line.split(b' ')[1].decode('utf-8')
        
        # Create a connection to the target server on port 80
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, 443))
        
        # Forward the client's request to the server
        server_socket.send(request)
        
        # Start forwarding data between client and server
        threading.Thread(target=forward_data, args=(client_socket, server_socket)).start()
        threading.Thread(target=forward_data, args=(server_socket, client_socket)).start()

def forward_data(source_socket, destination_socket):
    while True:
        data = source_socket.recv(4096)
        if data:
            destination_socket.send(data)
        else:
            break

def start_proxy_server():
    proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_server.bind(('127.0.0.1', 8011))
    proxy_server.listen(5)
    print('Proxy server listening on port 8000')

    while True:
        client_socket, client_address = proxy_server.accept()
        print(f'Received connection from {client_address[0]}:{client_address[1]}')
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_proxy_server()
