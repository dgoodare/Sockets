import socket
import selectors
import types

class Server:

    def __init__(self, host, port):
        #set up localhost IP address
        self.hostAddress = host
        #set up a non-privileged port for the server to listen on (>1023)
        self.port = port
        #create a selector object to handle multiple client connections
        self.slct = selectors.DefaultSelector()
        self.sckt = self.createSocket()

    def createSocket(self):
        #create a socket object
        sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sckt.bind((self.hostAddress, self.port))
        sckt.listen()
        print("Listening on:", (self.hostAddress, self.port))

        #set the scoket to non-blocking mode
        sckt.setblocking(False)
        #register the socket to be monitored for Read Events
        self.slct.register(sckt, selectors.EVENT_READ, data=None)

        return sckt

    def startEventLoop(self):
        while True:
            #block until sockets are ready
            events = self.slct.select(timeout=None)

            for key, mask in events:
                if key.data is None:
                    self.getNewSocket(key.fileobj)
                else:
                    self.handleClientConnection(key, mask)

    def getNewSocket(self, socket):
        clientConn, clientAddr = socket.accept()
        print(clientAddr, "has connected")
        #put socket in non-blocking mode, otherwise, if it did block the entire server would stall
        clientConn.setblocking(False)
        #create object to hold client's data
        clientData = types.SimpleNamespace(clientAddr=clientAddr, inb=b'', outb=b'')
        #the client has data needing to be written/read, so both must be set
        events = selectors.EVENT_READ | selectors.EVENT_WRITE

        self.slct.register(clientConn, events, data=clientData)

    def handleClientConnection(self, key, mask):
        socket = key.fileobj
        clientData = key.data

        #if there is a read event
        if mask and selectors.EVENT_READ:
            recvData = socket.recv(1024)
            #if there is data to read
            if recvData:
                clientData.outb += recvData
            else:
                print(clientData.clientAddr, "has closed the connection")
                self.slct.unregister(socket)
                socket.close()

        if mask and selectors.EVENT_WRITE:
            if clientData.outb:
                print('Echoing', repr(clientData.outb), 'to', clientData.clientAddr)
                sentData = socket.send(clientData.outb)
                clientData.outb = clientData[:sentData]





newServer = Server('127.0.0.1', 500)
newServer.startEventLoop()

