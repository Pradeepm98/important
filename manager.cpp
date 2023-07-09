#include <iostream>
#include <boost/asio.hpp>
#include <boost/bind/bind.hpp>
#include <thread>

using boost::asio::ip::tcp;

void handle_client(std::shared_ptr<tcp::socket> client_socket) {
    boost::asio::streambuf request_buffer;
    boost::system::error_code error;

    // Read the request from the client
    size_t request_length = boost::asio::read_until(*client_socket, request_buffer, "\r\n\r\n", error);

    if (!error) {
        // Extract the first line of the request
        std::istream request_stream(&request_buffer);
        std::string first_line;
        std::getline(request_stream, first_line);

        // Extract the method from the first line
        std::istringstream iss(first_line);
        std::string method;
        iss >> method;

        if (method == "CONNECT") {
            // Extract the requested host and port
            std::string host_port;
            iss >> host_port;
            size_t colon_pos = host_port.find(':');
            std::string host = host_port.substr(0, colon_pos);
            std::string port = host_port.substr(colon_pos + 1);

            std::cout << "Host: " << host << std::endl;
            std::cout << "Port: " << port << std::endl;

            boost::asio::io_context server_io_context;
            tcp::socket server_socket(server_io_context);

            // Create a connection to the requested server
            tcp::resolver resolver(server_io_context);
            tcp::resolver::query query(host, port);
            boost::asio::connect(server_socket, resolver.resolve(query));

            // Send the client a success response
            boost::asio::write(*client_socket, boost::asio::buffer("HTTP/1.1 200 OK\r\n\r\n"));

            // Start forwarding data between client and server
            std::thread client_to_server_thread([client_socket, &server_socket]() {
                try {
                    while (true) {
                        boost::asio::streambuf buffer;
                        size_t length = boost::asio::read(*client_socket, buffer, boost::asio::transfer_at_least(1));
                        boost::asio::write(server_socket, buffer, boost::asio::transfer_exactly(length));
                    }
                } catch (const std::exception&) {
                }
            });

            std::thread server_to_client_thread([&server_socket, client_socket]() {
                try {
                    while (true) {
                        boost::asio::streambuf buffer;
                        size_t length = boost::asio::read(server_socket, buffer, boost::asio::transfer_at_least(1));
                        boost::asio::write(*client_socket, buffer, boost::asio::transfer_exactly(length));
                    }
                } catch (const std::exception&) {
                }
            });

            client_to_server_thread.join();
            server_to_client_thread.join();
        } else {
            // Handle regular HTTP requests
            std::cout << "Regular HTTP request" << std::endl;
            // ...
        }
    }
}

void start_proxy_server() {
    boost::asio::io_context io_context;
    tcp::acceptor acceptor(io_context, tcp::endpoint(tcp::v4(), 8097));

    std::cout << "Proxy server listening on port 8097" << std::endl;

    
    while (true) {
        std::shared_ptr<tcp::socket> client_socket = std::make_shared<tcp::socket>(io_context);

        acceptor.accept(*client_socket);

        std::string client_address = client_socket->remote_endpoint().address().to_string();
        std::cout << "Received connection from " << client_address << std::endl;

        std::thread client_thread(handle_client, client_socket);
        client_thread.detach();
    }

}

int main() {
    start_proxy_server();

    return 0;
}
