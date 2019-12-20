import socket
import os
import sys
import file_request


def exit(e, error_msg):
    ''' Prints the given error message and exception, e, then exits the program '''
    print(f"{e}\n{error_msg}")
    sys.exit(0)


def check_params_len(params):
    ''' Checks that exactly 3 parameters are on the command line, if not error message is printed and program exits '''
    if not (len(params) == 4):
        exit("", "There must only be 3 arguments on the command line.")


def check_port_num(port_num):
    ''' Checks that the given port number is between 1,024 and 64,000 (including) '''
    
    if not ((1_024 < port_num) and (port_num <= 64_000)):
        exit("", "Port number must be > 1_024 and <= 64_000") 


def check_file_exists(filename):
    ''' Returns True if the file exists and can be opened locally '''
    try:
        with open(filename, 'r') as i:
            pass
        exit("", "The file you are requesting already exists.")
    except Exception: # find actual exception
        return  
     

def get_address_info(address, port_num):
    ''' Checks if the address is an IP address or a hostname and that they are well formed '''
    #if len(address.split(".")) == 4: # Might be edge case CHECK******
        #print("IP")
        #print(type(address))
    #else:
        #print("Host")
    try:
        addr_info = socket.getaddrinfo(host=address, port=port_num)
        print(addr_info)
    except socket.gaierror as e: # Try seperate these
        exit(e, "Could not get address info as address does not exist or address is not well-formed")
    
    return addr_info


def create_socket():
    ''' Creates an instance of socket, prints error message and exits if it doesn't work '''
    try:
        sock = socket.socket()
        sock.settimeout(1.0) # Sets the timeout of the socket to 1 second
    except Exception as e:
        exit(e, "Could not create a socket.")
        
    return sock


def create_connection(sock, addr_info, addr, port_num):
    ''' 
    Trys to create a connection with the server if it cannot do
    this program exits. 
    '''
    try:
        sock.connect((addr, port_num,))
        print("Connected.") 
    except Exception as e:
        exit(e, "Could not connect.")
    

def process_server_response(hdr):
    ''' Checks the FileResponse is a valid FileResponse '''
    
    # Checks Magic Number is valid
    magic_no = (hdr[0] << 8) | hdr[1]
    if magic_no != 0x497E:
        print("Wrong magic no.")
        return False, 0
    
    # Checks the Type is correct
    if hdr[2] != 0x02:
        print("Wrong type")
        return False, 0
    
    # Checks that that the file status is valid
    if hdr[3] != 0x00 and hdr[3] != 0x01:
        print("Wrong Status")
        return False, 0 
    
    # Checks whether the file was found on the server
    if hdr[3] == 0x00:
        print("File not found")
        return False, 0 
    
    # Calculates the len of the requested file
    length = hdr[4]
    for i in range(5, 8):
        length = (length << 8) | hdr[i]
    
    return True, length


def check_incoming_data(hdr):
    ''' 
    Checks what the recieved FileResponse header contains,
    incoming is returned as True if the file len is > 0 and
    exists is true if the file exists on the server
    '''
    if hdr[3] == 0x00:
        exists = False
    else:
        exists = True
        
    length = hdr[4]
    for i in range(5, 8):
        length = (length << 8) | hdr[i]    
    if length <= 0:
        incoming = False
    else:
        incoming = True
        
    return incoming, exists


def receive_write_data(sock, outfile):
    ''' Receives bytes in 4096 blocks and writes them to outfile, if an error occurs the program exits '''
    total_bytes = 0
    recieving = True
    try:
        while recieving:
            data = sock.recv(4_096)
            if not data:
                recieving = False
            else:
                total_bytes += len(data)
                outfile.write(data)
    except socket.timeout as e:
        sock.close()
        outfile.close()
        exit(e, "The connection timed out")
    except Exception as e:
        sock.close()
        outfile.close()
        exit(e, "Error while recieving data")
        
    return total_bytes
        
    

def main():
    params = sys.argv
    check_params_len(params)
    address, server_port, file_name = params[1], int(params[2]), params[3]
    
    print(f"Address: {address}")
    print(f"Server Port Number: {server_port}")
    print(f"File Name: {file_name}")
    
    # REMOVED FOR TESTING ########
    # Check that the requested file doesnt already exist 
    #check_file_exists(file_name)
    
    # Check that it is a valid port number
    check_port_num(server_port)

    # Checks address is valid and gets the address info
    address_info = get_address_info(address, server_port)
    
    # Create a socket
    sock = create_socket()
    
    # Connect
    create_connection(sock, address_info, address, server_port)
    
    # Create FileRequest
    request = file_request.create_file_request(file_name)

    # Sends the FileRequest to the connected server
    print(f"{sock.send(request)} bytes sent.")
    
    # Receive the response
    try:
        data = sock.recv(8)
    except socket.timeout() as e:
        socket.close()
        exit(e, "The socket timed out while receiving.")
    print(data)
    
    # Process the received response
    valid, infile_len = process_server_response(data)
    if valid:
        data_coming, exists = check_incoming_data(data)
        
        # Closes the socket if there is no file coming
        if not data_coming:
            sock.close()
            exit("", "There is no incoming data.")
        
        # Closes the socket if the file on the server does not exist
        if not exists:
            sock.close()
            exit("", "The file does not exist on the server")
        
        # Tries to open the file to write the received data to
        try:
            outfile = open("done.docx", "wb")
        except Exception as e:
            sock.close()
            exit(e, "Could not write the data to a file.")
            
        # Writes the received data to the opened file
        total = receive_write_data(sock, outfile)
        outfile.close()
        
        # Checks the len of received data is the same as the expected len
        length = data[4]
        for i in range(5, 8):
            length = (length << 8) | data[i]        
        if total != length:
            sock.close()
            exit("", "The bytes received != the file len from FileResponse.")
        
    else:
        sock.close()
        exit("", "FileResponse was errorenous or timed out.")

    # Prints a message, closes the socket and exits
    print(f"File successfully transferred.\n{total} bytes were received.")
    sock.close()
    sys.exit(0)



if __name__ == "__main__":
    main()