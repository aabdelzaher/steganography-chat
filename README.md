# steganography-chat
To run the application:

1) install the dependencies : 
    pip3 install pycrypto
    pip3 install stegano

2) run the server python file in the terminal
   python3 server.py

3) run the client python file
   python3 client.py

NOTE : The server IP should be known to the client. The server IP is written in the 'connect_to_server' under the server port. This line should be changed to the server IP (in the example the server runs on the localhost). To use another IP modify it to be 'host = YOUR_SERVER_IP'

4) to register choose join then enter the username and password

5) to login choose Login and enter the username and password

6) in order to send messages to another user, write it in the format:
    Reciever's username: message

NOTE: Reciever's username is case sensitive and there is no space between the name and the colon.

7) in order to send a broadcast message ( group chat), write it in the format: 
    ALL: message

NOTE: ALL is capital and there is no space between 'ALL' and the colon.

8) if you would like to run another client on the same device you have to change the port:
   - open client.py 
   - change port = xxxx to another port	(Applications cannot run on the same port)
   - run client.py normally in another terminal



