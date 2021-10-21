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
#create list to store all sockets, including the server socket
socketList = [serverSckt]
#create list of users
clientList = {}


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
            print(f"Message received from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for clientSckt in clientList:
                if clientSckt != notified:
                    clientSckt.send(user['header'] + user['data'] + message['header'] + message['data'])

    #iterate through the error list and remove any problematic sockets
    for notified in exceptionSckt:
        socketList.remove(notified)
        del clientList[notified]