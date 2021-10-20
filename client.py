import sys
import socket
import select
import errno

#constant values
headerLen = 10
IPaddress = "127.0.0.1"
portNo = 1000

#get username from user (console input)
newUsername = input("Please enter your username: ")
#create socket for the client
clientSckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSckt.connect((IPaddress, portNo))
#set to non-blocking mode to prevent the server from stalling while trying to service the connection
clientSckt.setblocking(False)

username = newUsername.encode('utf-8')
usernameHeader = f"{len(username):<{headerLen}}".encode('utf-8')
clientSckt.send(usernameHeader + username)

while True:
    message = input(f"{newUsername} : ")

    if message:
        message = message.encode('utf-8')
        messageheader = f"{len(message) :< {headerLen}}".encode('utf-8')

        clientSckt.send(messageheader + message)

    try:
        #receive data on the username and the message
        while True:
            #receive username data
            usernameHeader = clientSckt.recv(headerLen)

            #if no data is received, the connection must have been closed
            if not len(usernameHeader):
                print("Server closed connection")
                sys.exit()
            
            #get the length of the username
            usernameLen = int(usernameHeader.decode('utf-8'))
            #get the first 'usernameLen' bytes and store as the username
            username = clientSckt.recv(usernameLen).decode('utf-8')

            #receive message data
            messageheader = clientSckt.recv(headerLen)
            #get the length of the message
            messageLen = int(messageheader.decode('utf-8'))
            #get the first 'messageLen' bytes and store as the message
            message = clientSckt.recv(messageLen).decode('utf-8')

            #print the message
            print(f"{username} : {message}")

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print("An error occurred when reading:", str(e))
            sys.exit()
        continue
    except Exception as e:
        print("An error occurred:", str(e))
        sys.exit()
        pass