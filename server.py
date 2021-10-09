import socket

#set up localhost IP address
hostAddress = '127.0.0.1'
#set up a non-privileged port for the server to listen on (>1023)
port = 500

#set up a listening socket
#socket() -> bind() -> listen() -> accept()
def createServerSocket(hostAddress, port):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sckt:
        sckt.bind((hostAddress, port))#bind the socket to localHost address and non-privileged port
        sckt.listen()#get socket to listen

        #For now, the socket has been setup using IPv4, but we may need to change this to IPv6.
        #Doing so will require the addition of flowinfo and scopeid
        clientConnection, clientAddress = sckt.accept()
        with clientConnection:
            print(clientAddress, " connected to the server")
            while True:#loop through blocking calls and read data sent by client
                clientData = clientConnection.recv(1024)

                #if clientData is empty, then client closed connection and the loop is ended
                if not clientData:
                    break#end loop
                
                clientConnection.sendall(clientData)#echoes back the data sent by client




createServerSocket(hostAddress, port)