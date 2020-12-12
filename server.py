#server.py: i incorrectly renamed this file as client.py
import socket
import sys 

s = socket.socket()
s.bind(('localHost', 9999))
s.listen(10)
sc, address = s.accept()

print(f"address: {address}")
print(f"     SC: {sc}")

# print(address)



# open in binary

f = open('receivedFile.pdf', 'wb')


print('For debugging, printing raw bytes of file...')

while True:
    l = sc.recv(1026)
    while l:
        f.write(l)
        l = sc.recv(1026)
        print(l)

    #f.close()
    #sc.close()

# s.close()

