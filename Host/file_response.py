'''
Contains everything needed for creating a FileResponse header
'''

def create_file_response(file_opened, data_length=0):
    
    response = bytearray(b'\x00')
    for i in range(0, 7):
        response += bytearray(b'\x00')
    
    # Add magic_no to file response    
    magic_no = 0x497E
    magic_no = magic_no.to_bytes(2, 'big')
    response[0] = response[0] | magic_no[0]
    response[1] = response[1] | magic_no[1]
    
    # Add Type field to file response
    response[2] = response[2] | 0x02    
    
    # Add Status field to file response
    if file_opened == 1:
        opened = 0x01
    else:
        opened = 0x00
    response[3] = response[3] | opened
    
    if opened == 0x00:
        pass
    else:
        data_length = data_length.to_bytes(4, 'big')
        response[4] = response[4] | data_length[0]
        response[5] = response[5] | data_length[1]
        response[6] = response[6] | data_length[2]
        response[7] = response[7] | data_length[3]
    
    
    print(response)
    print(len(response))
    
    return response


if __name__ == "__main__":
    create_file_response(1, 100_000_000)
    x = open("hello.txt")
    x = x.read()
    print(repr(x))
    print(type(x))