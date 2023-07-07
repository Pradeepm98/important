import socket
import threading

def forward_data(source_socket, destination_socket, is_reverse):


    source_socket.setblocking(False)
    destination_socket.setblocking(False)
    buffer_size = 4096

    while True:
        try:
            data = source_socket.recv(buffer_size)
            if data:
                    destination_socket.sendall(data)
                    print("hh")
                    print(data)
            else:
                break
        except socket.error:
            print("error1")
            

        try:
            data = destination_socket.recv(buffer_size)
            if data:
                    source_socket.sendall(data)
                    print(data)
                    print("gg")
            else:
                break
        except socket.error:
            print("error2")
            
        #print("hi")


def handle_client(client_socket):
    request = client_socket.recv(4096)
    print(request)
    first_line = request.split(b'\n')[0]
    method = first_line.split(b' ')[0]

    if method == b'CONNECT':
        # Extract the requested host and port
        host, port = (first_line.split(b' ')[1].decode('utf-8')).split(':')
        print(host, port)
        # Create a connection to the requested server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, int(port)))
        
        # Send the client a success response
        
        # Start forwarding data between client and server
        forward_data(client_socket, server_socket, is_reverse=False)
        print("okkkk")

        server_socket.close()
    else:
        print()


    


def start_proxy_server():
    proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_server.connect(('127.0.0.1', 3000))
    print('Connected to proxy server on port 3000')
    while True:
       handle_client(proxy_server)
       print("gcgfcgfc")


if __name__ == "__main__":
    start_proxy_server()te
