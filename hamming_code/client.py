import socket

sock = socket.socket()
sock.connect(('localhost', 9090))
message = '00000000010101'.encode('cp1251')
sock.send(message)

data = sock.recv(1024)
sock.close()

,iprint( data )
