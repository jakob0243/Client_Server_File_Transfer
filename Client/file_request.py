'''
Contains everything needed for creating a FileRequest header
'''

def create_file_request(file_name):
    name_bytes = bytearray(file_name.encode('utf-8'))
    file_len = len(name_bytes)
    print(file_len)
    x = file_len
    request = bytearray(b'\x00')
    for i in range(0, 4):
        request += bytearray(b'\x00')
    
    # Add magic_no to file request    
    magic_no = 0x497E
    magic_no = magic_no.to_bytes(2, 'big')
    request[0] = request[0] | magic_no[0]
    request[1] = request[1] | magic_no[1]
    
    # Add Type field to file request
    request[2] = request[2] | 0x01
    
    # Add filenamelen to file request
    file_len = file_len.to_bytes(2, 'big')
    request[3] = request[3] | file_len[0]
    request[4] = request[4] | file_len[1] # ERROR CAPTURE
    print(request)
    
    request += name_bytes
    
    print(request)
    print(len(request))
    
    return request
    
    
if __name__ == "__main__":
    create_file_request("hello")