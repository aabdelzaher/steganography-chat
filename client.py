import socket 

import threading
from _thread import *
from stegano import lsb
from PIL import Image
import io
import os
from stegano import lsb
from Crypto.PublicKey import RSA
from Crypto import Random

from Crypto.Hash import SHA256

peers = []
name = ''
port = 5695
host = '127.0.0.1'
private_key = ''

class peer:
    def __init__(self, name, ip, receiving_port, key):
        self.name = name
        self.ip = ip
        self.receiving_port = receiving_port
        self.socket = None
        self.connected = False
        self.key = key

def parse_peer(s):
    att = s.split('#')
    return peer(att[0], att[1], int(att[2]), att[3])


def get_peer(port):
    global peers
    for p in peers:
        if(p.name == name):
            return p
    return None

def handle_peer_list(peer_list):
    global peers
    new_peers = []

    for new_peer in peer_list:
        # print("entered for")
        for i in range(len(peers)):
            # print("entered for")
            if peers[i].name == new_peer.name:
                new_peers += [peers[i]]
                break
        else:
            # print("entered else")
            new_peers = new_peers + [new_peer]
    peers = new_peers


def createKey():
   random_generator = Random.new().read
   key = RSA.generate(1024, random_generator)
   public_key = key.publickey()
   return key, public_key


# functions resposible for handling communication with server
def connect_to_server():
    global port
    global private_key
    # connect to the server
    serv_port = 12345
    host = '127.0.0.1'
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    s.connect((host,serv_port))

    private_key, public_key = createKey()
    puk = public_key.exportKey()

    s.send((name+","+str(port)+ "," + puk.decode('ISO-8859-1')).encode('ISO-8859-1'))
    # get peers list 
    data = s.recv(1024) 
    peer_list_str = data.decode('ISO-8859-1').split(',')
    peer_list = list(map(lambda pp: parse_peer(pp), peer_list_str))
    handle_peer_list(peer_list)
    # for pp in peer_list:
        # print(pp.name, pp.ip, str(pp.receiving_port), pp.key, pp.connected)
        
    start_new_thread(listen_to_server, (s, ))


def listen_to_server(s):
    while True: 
        data = s.recv(1024)
        # print(type(data))
        msg = data.decode('ISO-8859-1')
        peer_list_str = msg.split(',')
        peer_list = list(map(lambda pp: parse_peer(pp), peer_list_str))
        handle_peer_list(peer_list)
        # for pp in peer_list:
            # print(pp.name, pp.ip, str(pp.receiving_port), pp.key, pp.connected)

# functions responsible for creating a server for the current peer
def create_server(x):
    global port
    host = ""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host, port)) 
    s.listen(5) 
    while True: 
        c, addr = s.accept() 
        start_new_thread(listen_to_peers, (c,)) 
    s.close() 


def listen_to_peers(c):
    global private_key
    while True: 
        # data received from client 
        rec_msg = c.recv(1024)
        if(not rec_msg):
            break
        size = int(rec_msg.decode('ISO-8859-1'))

        c.sendall("GOT SIZE".encode('ISO-8859-1'))
        data = bytearray()
        while(len(data) < size):
            data += c.recv(40960000)
        
        if not data: 
            print('Bye') 
            break
  
        # check for digital signature

        image = Image.open(io.BytesIO(data))
        img_msg = lsb.reveal(image)
        decrypted = private_key.decrypt(img_msg.encode('ISO-8859-1'))
        received_msg = decrypted.decode('ISO-8859-1')
        received_msg = received_msg.split('#')
        sender_name = received_msg[0].strip()
        msg_body = str(':'.join(received_msg[1:]))
        # print(msg_body, received_msg)
        # print(received_msg, sender_name)
        print(sender_name, 'says :',msg_body)   

# functions responsible for sending messages to other peers
def send_steg_img(msg, img_path, sock):
    img = open(img_path, 'rb')
    bytes = img.read()
    secret = lsb.hide(img_path, msg)

    imgByteArr = io.BytesIO()
    secret.save(imgByteArr, format='png')
    bytes = imgByteArr.getvalue()

    # print(len(bytes))
    sock.sendall(str(len(bytes)).encode('ISO-8859-1'))

    resp = sock.recv(1024).decode('ISO-8859-1')
    if (resp == 'GOT SIZE'):
        sock.sendall(bytes)    


def encrypt_rsa(msg, p):
    puk = RSA.importKey(p.key)
    encrypted = puk.encrypt(msg.encode('ISO-8859-1'), 32)[0]
    return encrypted.decode('ISO-8859-1')


def send_msg_to_peer(peer_name, message):
    p = None
    for pp in peers:
        if pp.name == peer_name:
            p = pp
    if p:
        # print(p.name)
        pass
    else:
        print("No such user")
        return

    if p.connected:
        pass
    else:
        p.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        p.socket.connect((p.ip, p.receiving_port))
        p.connected = True

    

    encrypted_msg = encrypt_rsa(message, p)
    # print('tpye of encrypted msg', type(encrypted_msg))

    send_steg_img(encrypted_msg, './tst.jpeg', p.socket)

def create_client(x):
    while True:
        message = input()
        parsed_msg = message.split(':')
        send_to = [] # Users that I am going to send this msg to
        msg = name+"#"+str(':'.join(parsed_msg[1:]))
        if parsed_msg[0] == 'ALL':
            for p in peers:
                send_msg_to_peer(p.name, msg)    
        else:
            send_msg_to_peer(parsed_msg[0], msg)
        
        # p.socket.send((name+"#"+str(':'.join(parsed_msg[1:]))).encode('ISO-8859-1'))
        # print(parsed_msg[1], "sent to", parsed_msg[0])


def Main(): 
    # local host IP '127.0.0.1' 

    connect_to_server()
    start_new_thread(create_server, (1,))
    start_new_thread(create_client, (1,))
    
    while True:
        pass

 
if __name__ == '__main__': 

    command = input('Please type one of the following: Join or Login\n')
    command = command.lower()
    while command != 'join' and command != 'login':
        command = input('I got something else. Please type one of the following: Join or Login\n')
        command = command.lower()

    if command == 'join':
        valid_credentials = False
        username = ''
        password = ''
        while not valid_credentials:
            username = input('Please enter username. This can include alphanumeric characters and _\n')
            password = input('Please enter your password')
            valid_credentials = True
            for c in username:
                if c.isalnum() or c == '_':
                    pass
                else:
                    valid_credentials = False

        name = username
    elif command == 'login':
        pass
    else:
        print("I am surprised")

    Main()
