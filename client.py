import socket
import sys
import time

HOST = 'localHost'
PORT = 9999

s = socket.socket()
print(f"[+] Connecting to {HOST}:{PORT}")
s.connect((HOST, PORT))
print("[+] Connected.")

file_name = input('Please enter file you would like to transfer: ')

try:
    with open(file_name, 'rb') as f:
        print('File Exists! Requesting to send file to client...')
        l = f.read(1026) 
        while(l):
            s.send(l)
            l = f.read(1026)
        print(f'File {file_name} sent successfully')
except IOError as e:
    print(f'Could not open file you want to transfer {e} ')
    print("\tMake sure file you're trying to send exists")
