import ssl
import socket
from time import sleep
from socketserver import BaseRequestHandler, TCPServer
from utilities import contacts_dict_exist, get_user_name_from_list
from utilities import check_user_contact
import utilities
from threading import Thread

own_ip = None

potential_contact = ()

ignore_bcast_port = []


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
        try:
            if type(eval(self.data)) is tuple:
                if contacts_dict_exist():
                    self.data = eval(self.data)
                    # print(self.data)
                    email_exists = check_user_contact(self.data)
                    if email_exists:
                        self.request.sendall("Yes".encode())
                    elif not email_exists:
                        self.request.sendall("No".encode())
                else:
                    self.request.sendall("No".encode())
        except SyntaxError:
            confirmation = input(f"Contact <____> is sending a file. Accept (y/n)?")

            if confirmation == 'y' or confirmation == 'Y':
                f = open("recieved_file", "wb")
                f.write(self.data)
                running = True
                while running:
                    print("hang up in handle")
                    self.data = self.request.recv(1024)
                    if not self.data:
                        break
                    if self.data.decode() == "stop":
                        running = False
                        break
                    f.write(self.data)
                f.close()
                self.request.sendall("AWK from server".encode())
            else:
                print("File not accepted\n")
        # self.request.sendall("AWK from server".encode())


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


def tcp_client(port, data, is_file=False):
    host_ip = "127.0.0.1"

    # Initialize a TCP client socket using SOCK_STREAM
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cntx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    cntx.load_verify_locations("cert.pem")
    cntx.load_cert_chain("cert.pem")

    s = cntx.wrap_socket(s, server_hostname="test.server")

    if not is_file:
        try:
            # Establish connection to TCP server and exchange data
            s.connect((host_ip, port))
            s.sendall(data.encode())
            # Read data from the TCP server and close the connection
            recieved = s.recv(1024)
        finally:
            s.close()
    elif is_file:
        try:
            try:
                with open(data, 'rb') as f:

                    f = open(data, "rb")
                    s.connect((host_ip, port))
                    l = f.read(1024)
                    while l:
                        s.send(l)
                        print("Sent ", repr(l))
                        l = f.read(1024)
                    s.sendall("stop".encode())
                    recieved = s.recv(1024)
            except IOError as e:
                print(f"Could not open the file you want to trasnfer {e}")
                print(f"\tMake sure the file path is correct")
        finally:
            # s.send("stop")
            f.close()
            s.close()

    if recieved.decode() == "Yes":
        if potential_contact not in utilities.ONLINE_CONTACTS:
            utilities.ONLINE_CONTACTS.append(potential_contact)
            ignore_bcast_port.append(potential_contact[3])
    elif recieved.decode() == "No":
        pass
    else:
        pass


#######################################
#          Broadcast Handler          #
#######################################


def broadcast_listener(socket):
    try:
        while True:
            data = socket.recvfrom(4096)
            data = eval(data[0])
            # code to check if in contacts
            email_exists = check_user_contact(data)
            global potential_contact
            potential_contact = data
            # send back a yes if in contacts, with information back
            if email_exists and potential_contact[3] not in ignore_bcast_port:
                list = (
                    get_user_name_from_list(),
                    utilities.USER_EMAIL,
                    tcp_listen,
                    bcast_port,
                )
                ls = str(list)
                tcp_client(data[2], ls)
    except KeyboardInterrupt:
        pass


def broadcast_sender(port):
    list = (get_user_name_from_list(), utilities.USER_EMAIL, tcp_listen, bcast_port)
    msg = str(list)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            if port != bcast_port:
                s.sendto(msg.encode(), ("255.255.255.255", port))
            if port == 2000:
                port = 1337
            elif port != 2000:
                port += 1
            sleep(0.01)  # goes through all the ports in about a minute
    except KeyboardInterrupt:
        pass


#######################################
#               Driver                #
#######################################


def communication_manager():

    # broadcast to other users that you exist
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.bind(("", bcast_port))

    broadcast_listener_worker = Thread(
        target=broadcast_listener,
        name="broadcast_listener_worker",
        args=(broadcast_socket,),
    )

    broadcast_sender_worker = Thread(
        target=broadcast_sender, name="broadcast_sender_worker", args=(bcast_port,)
    )

    tcp_listener_worker = Thread(
        target=tcp_listener, name="tcp_listener_worker", args=(tcp_listen,)
    )

    procs = [
        broadcast_listener_worker,
        broadcast_sender_worker,
        tcp_listener_worker,
    ]

    try:
        for p in procs:
            p.start()

    except KeyboardInterrupt:
        for p in procs:
            print("Terminating: {}".format(p.name))
            if p.is_alive():
                p.terminate()
                sleep(0.1)
            if not p.is_alive():
                print(p.join())
