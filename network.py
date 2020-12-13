#!/usr/bin/env python3
import sys
import ssl
import socket
from time import sleep
from multiprocessing import Process
from socketserver import BaseRequestHandler, TCPServer

own_ip = None


def init_ip():
    global own_ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    own_ip = s.getsockname()[0]
    s.close()


def port_manager(bport, lport):
    open_port = False
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not open_port:
        try:
            test_socket.bind(("", bport))
            open_port = True
        except OSError:
            bport += 1
            lport += 1

    test_socket.close()
    return bport, lport


bcast_port, tcp_listen = port_manager(1337, 9900)
tcp_port = 9900

#######################################
#             TCP Handler             #
#######################################


class tcp_handler(BaseRequestHandler):
    def handle(self):
        """
        This function is what can handle whether or not the sender is a contact
        """
        self.data = self.request.recv(1024).strip()
        print("Echoing message from: {}".format(self.client_address[0]))
        # print(self.data)
        self.request.sendall("AWK from server".encode())


def tcp_listener(port):
    host = "localhost"
    cntx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    cntx.load_cert_chain("cert.pem", "cert.pem")

    server = TCPServer((host, port), tcp_handler)
    server.socket = cntx.wrap_socket(server.socket, server_side=True)
    try:
        server.serve_forever()
    except:
        print("listener shutting down")
        server.shutdown()


def tcp_client(port, data):
    host_ip = "127.0.0.1"

    # Initialize a TCP client socket using SOCK_STREAM
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cntx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    cntx.load_verify_locations("cert.pem")
    cntx.load_cert_chain("cert.pem")

    s = cntx.wrap_socket(s, server_hostname="test.server")

    try:
        # Establish connection to TCP server and exchange data
        s.connect((host_ip, port))
        s.sendall(data.encode())
        # Read data from the TCP server and close the connection
        recieved = s.recv(1024)
    finally:
        s.close()

    print("Bytes Sent:     {}".format(data))
    print("Bytes Recieved: {}".format(recieved.decode()))


#######################################
#          Broadcast Example          #
#######################################


def broadcast_listener(socket):
    try:
        while True:
            data = socket.recvfrom(4096)
            data = eval(data[0])
            # right now print the data recieved, but later we will check it
            # against user's contact list, and see if contact is there.
            print(data)
            # code to check if in contacts
            ...
            # send back a yes if in contacts
            tcp_client(data[2], "Yes")
    except KeyboardInterrupt:
        pass


def broadcast_sender(port):
    arr = ("matt", "matt@gmail.com", tcp_listen)
    msg = str(arr)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            if port != bcast_port:
                s.sendto(msg.encode(), ("255.255.255.255", port))
            if port != 2000:
                port += 1
            elif port == 2000:
                port = 1337
            sleep(0.01)  # goes through all the ports in about a minute
    except KeyboardInterrupt:
        pass


#######################################
#               Driver                #
#######################################


def communication_manager():
    # find own ip
    init_ip()

    print(bcast_port, tcp_listen)

    # broadcast to other users that you exist
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.bind(("", bcast_port))

    broadcast_listener_worker = Process(
        target=broadcast_listener,
        name="broadcast_listener_worker",
        args=(broadcast_socket,),
    )

    broadcast_sender_worker = Process(
        target=broadcast_sender, name="broadcast_sender_worker", args=(bcast_port,)
    )

    tcp_listener_worker = Process(
        target=tcp_listener, name="tcp_listener_worker", args=(tcp_listen,)
    )

    procs = [
        broadcast_listener_worker,
        broadcast_sender_worker,
        tcp_listener_worker,
    ]

    try:
        for p in procs:
            print("Starting: {}".format(p.name))
            p.start()
        while True:
            tcp_client(tcp_port, input())
            sleep(1)

    except KeyboardInterrupt:
        for p in procs:
            print("Terminating: {}".format(p.name))
            if p.is_alive():
                p.terminate()
                sleep(0.1)
            if not p.is_alive():
                print(p.join())


#######################################
#               Main                  #
#######################################


def main():
    if len(sys.argv) > 1:
        communication_manager()
    else:
        communication_manager()


if __name__ == "__main__":
    main()
