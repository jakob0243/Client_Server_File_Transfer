import sys
import socket
import file_response


def exit(e, error_msg):
    ''' Prints the given error message and exception, e, then exits the program '''
    print(f"{e}\n{error_msg}")
    sys.exit(0)    


def check_port_num(port_num):
    ''' Checks that the given port number is between 1,024 and 64,000 (including) '''
    
    return ((1_024 < port_num) and (port_num <= 64_000))


def bind_socket(sock, port_num):
    ''' 
    Trys to bind the given socket to the given port_num, 
    if this fails program exits
    '''
    try:
        sock.bind(('localhost', port_num))
    except Exception as e:
        sock.close()
        exit(e, f"Socket could not bind to port {port_num}.")
        
        
def create_socket(port_num):
    ''' Creates a socket and tries to bind it to the port number '''
    # Create socket instance
    try:
        sock = socket.socket()
        print(sock.fileno())
    except Exception as e:
        exit(e, f"Could not create the socket.")
        
    # Bind the socket to the port number
    try:
        bind_socket(sock, port_num)
        print(f"Socket name: {sock.getsockname()}")
    except Exception as e:
        sock.close()
        exit(e, f"Could not bind socket to port number {port_num}.")
    
    return sock
    
        
def set_socket_listen(sock):
    ''' Trys to call listen() on the socket, if this fails program exits '''
    try:
        sock.listen()
    except Exception as e:
        sock.close()
        exit(e, "Socket doesn't want to listen")
        
        
def check_header_valid(hdr):
    ''' Checks that the given is a valid FileRequest header '''
    magic_no = (hdr[0] << 8) | hdr[1]
    if magic_no != 0x497E:
        print("Wrong magic no.")
        return False, 0
    
    if hdr[2] != 0x01:
        print("Wrong type")
        return False, 0
    
    f_name_len = (hdr[3] << 8) | hdr[4]
    if f_name_len < 1 or f_name_len > 1_024:
        print("Wrong len")
        return False
    
    return True, f_name_len


def get_file(filename):
    ''' 
    Attempts to open file, filename, if successful returns the 
    a FileResponse header and the content of the file in a byte array.
    If not successful then it returns a FileResponse header and -1
    '''
    filename = filename.decode('utf-8')
    # Trys to open the file
    try:
        infile = open(filename)
        file_contents = infile.read()
        infile.close()
        file_contents = bytearray(file_contents, 'utf-8')
        file_opened = 1
        response = file_response.create_file_response(file_opened, len(file_contents))
        
        return response, file_contents
    except Exception as e:
        print(e)
        file_opened = 0
        response = file_response.create_file_response(file_opened)
    
        return response, None
    

def main(port_num):
    ''' Print the cmd input '''
    # Check that port number is valid
    port_num = int(port_num)
    port_valid = check_port_num(port_num)
    if not port_valid:
        exit("", f"{port_num} is not a valid port number.")
    
    print(f"Port Number: {port_num}")
    print(f"Input type: {type(port_num)}")
    
    # Create socket instance
    sock = create_socket(port_num)
    
    # Make the socket listen
    set_socket_listen(sock)
    
    done = False
    count = 0
    while not done:
        try:
            # SET TIME OUT SECTION 3.4
            connection, addr = sock.accept()
            
            with connection:
                print(f"Connected to {addr}")
                data = bytearray(connection.recv(5)) # Check difference between this and recvfrom()
                valid, name_len = check_header_valid(data)
                if valid:
                    data = bytearray(connection.recv(int(name_len))) #ERROR CAPTURE
                    print(data)
                    response, content = get_file(data)
                    if not content:
                        connection.send(response)
                        raise Exception("The file doesn't exist or couldn't be opened.")
                    else:
                        connection.send(response)
                        connection.send(content)
                        print(f"{len(content)} bytes of data were successfully sent to {addr}.")
                        # CHeck File Recieved
                else:
                    raise Exception("The File Response Header was erroneous")
                print("Success!")
        except Exception as e:
            connection.close()
            print(e)
            
        if count == 0:
            done = True
        count += 1
        
    
    # Close the socket
    sock.close()
    
    print("Done")
    
    
if __name__ == "__main__":
    main(sys.argv[1])
    #print(check_header_valid(bytearray(b'I~\x01\x00\x05')))
    #get_file_response(b'poggers')