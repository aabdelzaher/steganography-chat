# import socket programming library 
import socket 
  
# import thread module 
from _thread import *
import threading 
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA256

import handle_passwords

def createKey():
   random_generator = Random.new().read
   key = RSA.generate(1024, random_generator)
   public_key = key.publickey()
   return key, public_key

  
# print_lock = threading.Lock() 

class peer:
    def __init__(self, name, ip, receiving_port, socket, key):
        self.name = name
        self.ip = ip
        self.receiving_port = int(receiving_port)
        self.socket = socket
        self.key = key

# name + ip + port
def to_string(p):
    return p.name+"#"+str(p.ip)+"#"+str(p.receiving_port)+'#'+p.key


peers = []

# thread fuction 
def threaded(c, addr): 
    global peers

    login_info = handle_login_info(c)

    if not login_info:
        c.close()
        return

    data = c.recv(4096) # name, port
    data = data.decode('ISO-8859-1')
    data = data.split(",")
    new_peer = peer(data[0], addr[0], data[1], c, data[2])
    name = new_peer.name
    peers += [new_peer]
    # lock acquired by client 
    # print_lock.acquire() 
    print('Connected to :', addr[0], ':', addr[1])
    peerStr = ','.join(map(lambda p: to_string(p), peers))
    # print(','.join(map(lambda p: toString(p), peers))) 
    # print(peerStr)
    for p in peers:
        p.socket.send(peerStr.encode('ISO-8859-1'))
    # Start a new thread and return its identifier


    while True: 
  
        # data received from client 
        data = c.recv(1024) 
        if not data: 
            print('Bye') 
            # remove peer
            peers = list(filter(lambda p: p.name != name, peers))
            peerStr = ','.join(map(lambda p: to_string(p), peers))
            # print(','.join(map(lambda p: toString(p), peers))) 
            # print(peerStr)
            for p in peers:
                p.socket.send(peerStr.encode('ISO-8859-1'))
        
            # lock released on exit 
            # print_lock.release() 
            break
    c.close() 

def toString(peer):
    return "("+peer.name + ", " + str(peer.receiving_port) +")"
  

def handle_login_info(s):
    while True:
        data = s.recv(4096) # name, port
        if not data:
            return False
        data = data.decode('ISO-8859-1')
        data = data.split(":")
        if data[0] == 'join':
            username = data[1]
            password = data[2]
            if username in handle_passwords.users_login:
                s.send("la".encode('ISO-8859-1'))
                continue
            handle_passwords.add_user(username, password)
            s.send("tamam".encode('ISO-8859-1'))
            # print(username, password)
            break
        elif data[0] == 'login':
            username = data[1]
            password = data[2]
            # print(username, password)
            valid = handle_passwords.validate_user(username, password)
            # print(valid)
            if valid:
                s.send("tamam".encode('ISO-8859-1'))
                break
            else:
                s.send("la".encode('ISO-8859-1'))
    return True

        

def Main(): 
    global peers
    host = "" 
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host, port)) 
    print("socket binded to port", port) 
  
    # put the socket into listening mode 
    s.listen(5) 
    print("socket is listening") 
    handle_passwords.init('./passwords.txt')
    # a forever loop until client wants to exit 
    while True: 
  
        # establish connection with client 
        print("Waiting for connection")
        c, addr = s.accept() # socket address

         
        start_new_thread(threaded, (c,addr)) 
    s.close() 
  
  
if __name__ == '__main__': 
    Main() 

