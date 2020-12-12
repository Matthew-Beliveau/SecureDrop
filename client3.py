import sys
import socket
import tqdm
import os

SEPARATOR = "<SEPARATOR>"
# arbitrary, will send 4096 bytes each time step
BUFFER_SIZE = 4096
HOST = 'localHost'
# hardcode port 9999
PORT = 9999

file_name = input('Please enter the file you would like to transfer: ')

# catch any error with file_name
try:
    with open(file_name, 'rb') as f:
        print('File Exists!')
        f.close()
except IOError as e:
    print(f'Could not open file you want to trasnfer {e}')
    print("\t Make sure you're specifying the correct path/filename")
    sys.exit()

# get the file size in bytes
file_size = os.path.getsize(file_name)

# create the client socket 
s = socket.socket()

#connect to the server 
print(f"Connecting to {HOST}:{PORT}")
s.connect((HOST, PORT))
print("Connected.")

# send the filename and filesize, encode() encodes as utf-8
s.send(f"{file_name}{SEPARATOR}{file_size}".encode())

# this could be a function right here to send the file with progress bars
progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit = "B", unit_scale = True, unit_divisor = 1024)
with open(file_name, "rb") as f:
    for _ in progress:
        # read bytes from the file
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            # file transmitting is done
            break
        # sendall to assure transmission in a busy network for example
        s.sendall(bytes_read)
        # update our progress bar
        progress.update(len(bytes_read))

#close the socket
s.close()
