import socket
import selectors
import types

slct = selectors.DefaultSelector()

class Client:

    def __init__(self, host, port):
        self.hostAddress = host
        self.port = port
        self.messages = [b'Message 1', b'Message 2']
        #self.slct = selectors.DefaultSelector()

    def beginConnection(self, numOfConnections):
        serverAddr = (self.hostAddress, self.port)

        for i in range(0, numOfConnections):
            connectionID = i+1
            print("Connecting ", connectionID, "to", serverAddr)
            #create new socket
            sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #set socket to non-blocking mode
            sckt.setblocking(False)
            #begin connection to server
            sckt.connect_ex(serverAddr)

            #set up socket for reading and writing
            events = selectors.EVENT_READ | selectors.EVENT_WRITE

            clientData =  types.SimpleNamespace(connectionID=connectionID, 
                                                msgSize = sum(len(x) for x in self.messages),#number of bytes
                                                recvTotal = 0,#size of data that has been received
                                                messages = list(self.messages),#the messages themselves, stored as a list
                                                outb = b'')
            slct.register(sckt, events, data=clientData)

    def tryConnect(self):
        try:
            while True:
                events = slct.select(timeout=0)
                if events:
                    for key, mask in events:
                        self.handleConnection(key, mask)

                if not slct.get_map():
                    break
        
        except KeyboardInterrupt:
            print("Keyboard input detected, closing connection")
        finally:
            slct.close()

    def handleConnection(self, key, mask):
        socket = key.fileobj
        clientData = key.data

        #if there is a read event
        if mask and selectors.EVENT_READ:
            recvData = socket.recv(1024)
            #if there is data to read
            if recvData:
                print("Received", repr(recvData), "from", clientData.connectionID)
                #increment running total of data received
                clientData.recvTotal += len(recvData)
            
            #check to see if the size of the message matches the size of the data received
            #It is possible that the client doesn't close its connection - causing the server to leave
            #the connection open. This is something we may want to guard against on the serverside, 
            #otherwise, unused client connections may end up accumulating unnecessarily
            if (not recvData) or (clientData.recvTotal == clientData.msgSize):
                #if data has finished transmitting (i.e. recvTotal == msgSize) close the connection
                print("closing connection:", clientData.connectionID)
                slct.unregister(socket)
                socket.close()

        #if there is a write event
        if mask and selectors.EVENT_WRITE:
            if not clientData.outb and clientData.messages:
                #get the first message from the list
                clientData.outb = clientData.messages.pop(0)
            #if outb contains a message
            if clientData.outb:
                print("sending", repr(clientData.outb), "to connection", clientData.connectionID)
                sentData = socket.send(clientData.outb)
                clientData.outb = clientData.outb[sentData:]

newClient = Client('127.0.0.1', 500)
newClient.beginConnection(1)
#newClient.tryConnect()
try:
    while True:
        events = slct.select(timeout=1)
        if events:
            for key, mask in events:
                newClient.handleConnection(key, mask)
        if not slct.get_map():
            break

except KeyboardInterrupt:
    print("Keyboard input detected, closing connection")
finally:
    slct.close()

            







