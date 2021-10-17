import sys
import socket
import selectors
import types

slct = selectors.DefaultSelector()

def startServer():
    #check for correct number of arguments
    if len(sys.argv) != 3:
        print("usage:", sys.argv[0], "<host> <port>")
        sys.exit(1)

    hostAddr, portNo = sys.argv[1], int(sys.argv[2])
    #create socket object, bind to given address and port number
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.bind((hostAddr, portNo))
    sckt.listen()
    print("listening on", (hostAddr, portNo))
    #set to non-blocking mode
    sckt.setblocking(False)
    #register with selector
    slct.register(sckt, selectors.EVENT_READ, data=None)

def startEventLoop():
    try:
        while True:
            events = slct.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    acceptWrapper(key.fileobj)
                else:
                    serviceConnection(key, mask)
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        slct.close()

def acceptWrapper(sckt):
    conn, addr = sckt.accept()
    print("Connection from", addr, "accepted")
    #set socket to non-blocking mode
    conn.setblocking(False)
    #create data object to store client data
    clientData = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    #create object to monitor for read/write events
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #register with selector
    slct.register(conn, events, data=clientData)


def serviceConnection(key, mask):
    sckt = key.fileobj
    data = key.data

    #if there is a read event
    if mask & selectors.EVENT_READ:
        recvData = sckt.recv(1024)
        #if there is data to read
        if recvData:
            data.outb += recvData
        #if there isn't, close the connection
        else:
            print("closing connection to", data.addr)
            slct.unregister(sckt)
            sckt.close()

    #if there is a write event
    if mask & selectors.EVENT_WRITE:
        #if data exists, send
        if data.outb:
            print("echoing", repr(data.outb), "to", data.addr)
            sent = sckt.send(data.outb)
            data.outb = data.outb[sent:]


startServer()
startEventLoop()
