import socket
import tqdm
import os

# all IPv4 address on the local machine
# if the server has two IPs on a network it should be reachable
# by both
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 9999
#receive 4096 bytes each time 
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

#TCP socket 
s = socket.socket()
s.bind((SERVER_HOST, SERVER_PORT))

# 5 is the number of unaccepted connections that the
# system will allow before refusal
s.listen(5)
print(f"\tListening as {SERVER_HOST}:{SERVER_PORT}")

#accept connection if there is any
client_socket, address = s.accept()
# code below this line will only execute if a connection 
# has been established
print(f"\t{address} is connected")

received = client_socket.recv(BUFFER_SIZE).decode()
file_name, file_size = received.split(SEPARATOR)

# remove absolute file path if included
file_name = os.path.basename(file_name)

#convert our file size to an int
file_size = int(file_size)

#start receiving file from our socket
# THIS COULD VERY WELL BE A FUNCTION ON ITS OWN
progress = tqdm.tqdm(range(file_size), f"Receiving {file_name}", unit = "B", unit_scale = True, unit_divisor = 1024)
with open(file_name, "wb") as f:
    for _ in progress:
        # read 1024 bytes from the socket
        bytes_read = client_socket.recv(BUFFER_SIZE)
        if not bytes_read:
            # nothing received 
            break
        # write to file with our received bytes
        f.write(bytes_read)
        # update fancy progress bar
        progress.update(len(bytes_read))

#close our client socket
client_socket.close()
#close our server socket
s.close()
