import bitarray    

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
    


#def create_file_request(filename, file_len):
    #''' Creates a file request... '''
    #magic_no = 0x497E
    #print(f"MagicNo: {bin(magic_no)}")
    
    #part_two = 1
    
    # # Check the length
    #file_name_len = len(filename)
    
    #file_request = 0x0000
    #print(bin(file_request))
    #file_request = file_request | (magic_no)
    #print(bin(file_request))
    #file_request = file_request << 8
    #print(bin(file_request))
    #file_request = file_request | 0x1
    #print(bin(file_request))
    #file_request = file_request << 16
    #print(bin(file_request))
    #file_request = file_request | file_len
    #print(bin(file_request))
    
    #bits = get_string_bits(filename)
    #print(len(bin(bits)))
    
    #file_request = file_request << (file_len * 8)
    #file_request = file_request | bits
    #print(bin(file_request))
    
    
    
    
    
    
if __name__ == "__main__":
    #create_file_request("hello", 6)
    create_file_request("hello")
    #s#tring_from_bits('000000000110100001100101011011000110110001101111')