import socket

hostAddress = '127.0.0.1'#server's IP address
port = 500#port being used by the server

def createClientSocket(hostAddress, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sckt:
        sckt.connect((hostAddress, port))
        sckt.sendall(b'testing testing...')
        data = sckt.recv(1024)

    print("Received ", repr(data))

createClientSocket(hostAddress, port)