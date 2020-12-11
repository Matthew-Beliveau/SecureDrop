import socket
import sys
import threading
import time 

HEADER = 128 #email assumed to be <= 128 characters
PORT = 5060
SERVER = socket.gethostbyname(socket.gethostname()) #returns the current IP address
Address = (SERVER, PORT)
FORMAT = 'utf-8'

DISCONNECT_MESSAGE = "!DISCONNECT"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

c_email = "b@gmail.com"
our_email = "h@gmail.com"

CONNECTION_CONFIRMATION = "CONF"
CONNECTION_FAIL_MESSAGE = "FAIL"

#Lock object to protect send_possible_list
lock_object = threading.Lock()

#Lock object to protect ports_seen
lock_object_port = threading.Lock()

#This global dictionary holds the list of contacts that the user can send a msg to
#This list will be the one returned by >list
#This list will be protected by semaphores
send_possible_list = {} 

#This global list keeps track of all of the ports that server.listen() has gotten
#connected to from (meaning that it is a list of ports that have connected to the
#server
#This list will be protected by semaphores
ports_seen =[]

def message_handling(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    return message, send_length

def handshake(conn, address):
    #connected = True 
    #while connected:
    msg_length = conn.recv(HEADER).decode(FORMAT) #receive header message
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT) #read up to msg_length characters
        print(f"[{address}] {msg}", "actual message is: ", msg)
        #if msg == DISCONNECT_MESSAGE:
            #connected = False
        #We have client's email, now we determine if client is in our list
        #The following check will be executed with the function I implemented in SD
        if msg == c_email: #client in our list, so send our email
            print("emails match")
            encoded_email, send_length = message_handling(our_email)
            conn.send(send_length)
            conn.send(encoded_email)
        else: #client not in our list, connection is not possible, end it
            fail_msg, sl = message_handling(CONNECTION_FAIL_MESSAGE)
            conn.send(sl)
            conn.send(fail_msg)
        #Receive confirmation msg
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            conf_msg = conn.recv(msg_length).decode(FORMAT)
            print("conf message: ", conf_msg)
            if conf_msg == CONNECTION_CONFIRMATION:
                #Insert semaphore code to protect send_possible_list
                #Add port to send_possible_list
                Is_lock_not_available = True
                Is_lock_not_available2 = True
                print("got confirmation")
                while Is_lock_not_available:
                    if not lock_object.locked(): #no-one has acquired lock
                        lock_object.acquire() #get lock, we should get it, else wait
                        if msg not in send_possible_list:
                            send_possible_list[msg] = address[1]
                            print(send_possible_list)
                            conn.close()
                            Is_lock_not_available = False
                            lock_object.release()
                            exit()
                        Is_lock_not_available = False
                        lock_object.release() #release at will
                        #At this point, we've updated send_possible_list
                        #We now wait for a disconnect message
                        is_client_online = True
                        while is_client_online:
                            msg_length = conn.recv(HEADER).decode(FORMAT)
                            if msg_length:
                                msg_length = int(msg_length)
                                dc = conn.recv(msg_length).decode(FORMAT)
                                is_client_online = False
                                print(dc)
                                #we got disconnect message
                                #get lock, update send_possible_list, end handshake
                                while Is_lock_not_available2:
                                    if not lock_object.locked():
                                        lock_object.acquire()
                                        #edit send_possible_list
                                        del send_possible_list[msg]
                                        print("boom baby: {address[1]}")
                                        Is_lock_not_available2 = False
                                        lock_object.release()
                                        conn.close()
            else:
                conn.close()

def send(msg):
    message, sl = message_handling(msg)
    cond = True
    while cond:
        try:
            server.send(sl) #send header
            cond = False
        except BrokenPipeError:
            #print("no one is online yet")
            pass
        except OSError:
            pass
    server.send(message)
    #we got server's email back, need to check if they in our list
    msg_length = server.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        sent_email = server.recv(msg_length).decode(FORMAT)
        if sent_email == our_email: #connection possible, send conf 
            print("sending conf")
            conf_msg, sl = message_handling(CONNECTION_CONFIRMATION)
            server.send(sl)
            server.send(conf_msg)
        else:
            fail_msg, sl = message_handling(CONNECTION_FAIL_MESSAGE)
            server.send(sl)
            server.send(fail_msg)
            server.close()

def send_dc(msg):
    dc_msg, sl = message_handling(DISCONNECT_MESSAGE)
    server.send(sl)
    server.send(dc_msg)
    server.close()

#This is the listen/scan thread -> needs to be run in seperate thread
def listen_start():
    print("listening thread activated")
    cond = True
    while cond:
        try:
            server.listen()
            cond = False
        except OSError:
            pass
    while True:
        #waits for another user to connect or "appear online"
        conn, address = server.accept()

        #This block of code adds the port just seen to the ports_seen list if it
        #is not already in the list
        port_just_seen_not_added = True
        while port_just_seen_not_added:
            if not lock_object_port.locked():
                lock_object_port.acquire()
                if address[1] not in ports_seen:
                    ports_seen.append(address[1])
                port_just_seen_not_added = False
                lock_object_port.release()

        #when a connection occurs, immediately check if a connection is possible
        thread = threading.Thread(target=handshake, args = (conn, address))
        thread.start()
        print(f"active connections {threading.activeCount() -1}")

def send_email_over_network():
    time_now = time.time()
    t_end = time.time() + 2
    while time_now < t_end:
        send(our_email)
        t_end += time_now + 1

#Now we try and bind to the socket, if we can, we are the first online, if not, we
#must be a client
try:
    server.bind(Address)
except OSError:
    print("I'm a client")
    #Now we connect to server
    server.connect(Address)

#At this point we are either a server or a client, either way, we need to begin 
#sending our email across the network

send_thread = threading.Thread(target=send_email_over_network)
send_thread.start()

listening_thread = threading.Thread(target=listen_start)
listening_thread.start()

