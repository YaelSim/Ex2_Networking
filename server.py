import socket
import sys
import os

TIMEOUT_VAL = 1
IP_ADDR = '127.0.0.1'
CONNECTION_LIMIT = 1
BUFFER_SIZE = 1024


def main():
    port = sys.argv[1]
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', int(port)))
    server_socket.listen(CONNECTION_LIMIT)

    try:
        client_acception_and_handling(server_socket)
    finally:
        server_socket.close()


def client_acception_and_handling(server_socket):
    eol_index = -4
    eol_str = b'\r\n\r\n'
    while True:
        client_socket, client_address = server_socket.accept()
        client_socket.settimeout(TIMEOUT_VAL)
        while True:
            try:
                request_data = client_socket.recv(BUFFER_SIZE)
                if not request_data:  # The client sent an empty request
                    client_socket.close()
                    break

                # If the client's request is bigger than BUFFER_SIZE, continue reading (until we've got \r\n\r\n)
                while request_data[eol_index:] != eol_str:
                    request_data = request_data + client_socket.recv(BUFFER_SIZE)

            except socket.timeout:  # If a timeout has occurred
                client_socket.close()
                break
            # Our server shall print the request_data fully, with no other additions.
            decoded_request = request_data.decode()
            print(decoded_request)
            keep_alive = send_message_according_to_request(decoded_request, client_socket)
            if not keep_alive:
                client_socket.close()
                break


def send_message_according_to_request(data, client_socket):
    reply_msg = ""
    content = ""
    connection_state = ""
    file_size = 0
    get_str = "GET"
    connection_str = "Connection:"
    result_html_str = "/result.html"
    redirect_str = "/redirect"
    index_html_str = "/index.html"
    redirection_flag = False
    file_exist_flag = False

    data_lines = data.splitlines(keepends=True)
    for curr_line in data_lines:
        if curr_line.startswith(get_str):   # Some lines start with "GET [file] HTTP/1.1..."
            file_path = (curr_line.split(" ")[1])

            if file_path == redirect_str:
                file_path = result_html_str
                redirection_flag = True
            elif file_path == '/':
                file_path = index_html_str
            # All files are saved on "/files". So the file_path must contain this prefix.
            if file_path.startswith("/files"):
                file_path = file_path[1:]
            else:
                file_path = "files" + file_path
            file_exist_flag, content, file_size = file_handling(file_path)

        if curr_line.startswith(connection_str):
            connection_state = curr_line.split(" ")[1]  # close / Keep-alive according to the client's request
            if redirection_flag:  # redirect ...
                connection_state = "close"
                reply_msg = "HTTP/1.1 301 Moved Permanently\r\nConnection: " + \
                            connection_state + "\r\nLocation: /result.html" + "\r\n\r\n" + content.decode()
                client_socket.send(reply_msg.encode())

            elif file_exist_flag:  # The file exists.
                reply_msg = "HTTP/1.1 200 OK\r\nConnection: " + connection_state +\
                            "Content-Length: " + str(file_size) + "\r\n\r\n"
                client_socket.send(b''.join([reply_msg.encode(), content]))

            elif not file_exist_flag:  # The file doesn't exist.
                connection_state = "close"
                reply_msg = "HTTP/1.1 404 Not Found\r\nConnection: " + connection_state + "\r\n\r\n"
                client_socket.send(reply_msg.encode())

            if connection_state == "close":  # Close the client_socket.
                # client_socket.close()
                return False
            else:
                return True


def file_handling(file_path):
    file_exist_flag = True
    file_size = 0
    read_file = ""
    try:
        file = open(file_path, "rb")
        file_size = os.stat(file_path).st_size
        read_file = file.read(file_size)
        file.close()
    except IOError:  # File doesn't exist!
        file_exist_flag = False
    return file_exist_flag, read_file, file_size


if __name__ == '__main__':
    main()


