# import socket programming library 
import socket 
  
# import thread module 
from _thread import *
import threading 
from Crypto.PublicKey import RSA
import handle_passwords

  
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
def threaded(c): 
    while True: 
  
        # data received from client 
        data = c.recv(1024) 
        if not data: 
            print('Bye') 
              
            # TODO: remove peer

            # lock released on exit 
            # print_lock.release() 
            break
    c.close() 

def toString(peer):
    return "("+peer.name + ", " + str(peer.receiving_port) +")"
  
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
  
    # a forever loop until client wants to exit 
    while True: 
  
        # establish connection with client 
        print("Waiting for connection")
        c, addr = s.accept() # socket address
        data = c.recv(1024) # name, port
        data = data.decode('ISO-8859-1')
        data = data.split(",")
        new_peer = peer(data[0], addr[0], data[1], c, data[2])
        peers += [new_peer]
        # lock acquired by client 
        # print_lock.acquire() 
        print('Connected to :', addr[0], ':', addr[1])
        peerStr = ','.join(map(lambda p: to_string(p), peers))
        # print(','.join(map(lambda p: toString(p), peers))) 
        print(peerStr)
        for p in peers:
            p.socket.send(peerStr.encode('ISO-8859-1'))
        # Start a new thread and return its identifier 
        start_new_thread(threaded, (c,)) 
    s.close() 
  
  
if __name__ == '__main__': 
    Main() 

