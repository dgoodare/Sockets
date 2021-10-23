import socket
import select

#constant values
headerLen = 10
IPaddress = "::1"
portNo = 1000

#create socket for server
serverSckt = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
#set socket option to allow client to re-connect
serverSckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSckt.bind((IPaddress, portNo, 0 ,0))
serverSckt.listen()
print("Listening on", (IPaddress, portNo))
#create list to store all sockets, including the server socket
socketList = [serverSckt]
#create list of clients
clientList = {}
#create list of usernames
usernameList = []


def recvMessage(clientSckt):
    try:
        msgHeader = clientSckt.recv(headerLen)
        
        #if no data is received, assume client closed connection
        if not len(msgHeader):
            return False

        #get the length of the message
        msgLen = int(msgHeader.decode("utf-8"))
        #return a dictionary containing the message header and the message itself
        return {"header": msgHeader, "data":clientSckt.recv(msgLen)}

    except:
        return False

def getUser(message):
    #remove the '@' (the first character)
    message = message[1:]
    #split the message by spaces
    user = message.split(' ')
    #split() returns a tuple where each element is a word, we only need the first element
    return user[0]

while True:
    #read list, write list, error list
    readSckt, _, exceptionSckt = select.select(socketList, [], socketList)

    #iterate through the read list and handle any new connections or new messages
    for notified in readSckt:
        #if there is a new connection
        if notified == serverSckt:
            #accept connection from client
            clientSckt, clientAddr = serverSckt.accept()

            newUser = recvMessage(clientSckt)
            #check if client disconnected
            if newUser is False:
                continue
            #if they did not, add their socket to the socket list
            socketList.append(clientSckt)
            clientList[clientSckt] = newUser

            clientIP, clientPort = clientAddr[0], clientAddr[1]
            clientName = newUser['data'].decode('utf-8')
            usernameList.append(clientName)
            print("Connection from", clientIP, clientPort, "with username:", clientName, "accepted")
        else:
            message = recvMessage(notified)

            if message is False:
                print(f"Connection from {clientList[notified]['data'].decode('utf-8')} closed")
                #remove socket from socket and client lists
                socketList.remove(notified)
                del clientList[notified]
                continue
            
            user = clientList[notified]
            userMsg = message['data'].decode('utf-8')
            print(f"Message received from {user['data'].decode('utf-8')}: {userMsg}")

            #check for private message
            if userMsg[0] == '@':
                userMatch = False
                #retrieve the username from the message
                recipient = getUser(userMsg)
                if recipient:
                    #start counnter at 1, as the first item in socketList is the server socket
                    counter = 1
                    #iterate through the list of usernames and check for matches
                    for username in usernameList:
                         if recipient == username:
                             userMatch = True
                             break
                         counter += 1
                    
                    if userMatch:
                        #get the user's socket from the corresponding socketList
                        clientSckt = socketList[counter]
                        #send the message to only the specified user
                        clientSckt.send(user['header'] + user['data'] + message['header'] + message['data'])
                    else:
                        #if no matching username could be found
                        print("No user with the name", recipient, "could be found")
            else:
                #not a private message so send to all users
                for clientSckt in clientList:
                    if clientSckt != notified:
                        clientSckt.send(user['header'] + user['data'] + message['header'] + message['data'])

    #iterate through the error list and remove any problematic sockets
    for notified in exceptionSckt:
        socketList.remove(notified)
        del clientList[notified]