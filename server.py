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
                request_data =  client_socket.recv(BUFFER_SIZE)
                # If the client's request is bigger than BUFFER_SIZE, continue reading (until we've got \r\n\r\n)
                while request_data[eol_index:] != eol_str:
                    request_data = request_data + client_socket.recv(BUFFER_SIZE)
            except socket.timeout:  # If a timeout has occurred
                break
            # Our server shall print the request_data fully, with no other additions.
            decoded_request = request_data.decode()
            print(decoded_request)
            connection_flag, file_name = get_connection_and_filename_from_request(decoded_request)



def get_connection_and_filename_from_request(data):
    get_str = "GET"
    connection_str = "Connection:"
    result_html_str = "/result.html"
    redirect_str = "/redirect"
    index_html_str = "/index.html"
    redirection_flag = False
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

        elif curr_line.startswith(connection_str):
            connection_flag = curr_line.split(" ")[1]
            if redirection_flag:






def file_handling(file_path):
    file_exist_flag = True
    read_file = ""
    try:
        file = open(file_path, "rb")
        file_size = os.stat(file_path).st_size
        read_file = file.read(file_size)
        file.close()
    except IOError:  # File doesn't exist!
        file_exist_flag = False
    return file_exist_flag, read_file


if __name__ == '__main__':
    main()


