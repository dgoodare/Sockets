import sys
import socket
import selectors
import types

slct = selectors.DefaultSelector()
messages = [b"Message 1", b"Message 2"]

def receiveArgs():
    #check if number of arguments is correct
    if len(sys.argv) != 4:
        print("Incorrect number of arguments:", sys.argv[0], "<host address> <port number> <number of connections>")
        sys.exit(1)
    
    hostAddr, portNo, connections = sys.argv[1:4]
    beginConnection(hostAddr, int(portNo), int(connections))


def beginConnection(host, port, connections):
    serverAddr = (host, port)
    #iterate through the different connections, creating a socket for each
    for i in range(0, connections):
        connid = i + 1
        print("starting connection", connid, "to", serverAddr)
        #create socket object,
        #currently only IPv4, changin gto IPv6 will require the addition of 'flowinfo' and 'scopeID' in the tuple
        sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #set to non-blocking mode to prevent the server from stalling, 
        #preventing other sockets from being serviced
        sckt.setblocking(False)
        #connect to server
        sckt.connect_ex(serverAddr)

        #prepare an object to store the messages being sent to the server
        clientData = types.SimpleNamespace(
            connID=connid,
            msgSize=sum(len(m) for m in messages),
            recvTotal=0,
            messages=list(messages),
            outb=b"",
        )
        #create object to monitor for read/write events
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        #register socket with the selector
        slct.register(sckt, events, data=clientData)


def serviceConnection(key, mask):
    sckt = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recvData = sckt.recv(1024)
        if recvData:
            print("received", repr(recvData), "from connection", data.connID)
            data.recvTotal += len(recvData)
        if not recvData or data.recvTotal == data.msgSize:
            print("closing connection", data.connID)
            slct.unregister(sckt)
            sckt.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("sending", repr(data.outb), "to connection", data.connID)
            sent = sckt.send(data.outb)
            data.outb = data.outb[sent:]


receiveArgs()

try:
    while True:
        events = slct.select(timeout=1)
        if events:
            for key, mask in events:
                serviceConnection(key, mask)
        if not slct.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    slct.close()