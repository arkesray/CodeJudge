import socket
import threading
import os
class getFile(threading.Thread):
	def __init__(self,s):
		threading.Thread.__init__(self)
		self.sock = s

	def run(self):
		self.sock.send("Send".encode('utf-8'))
		data = self.sock.recv(1024).decode('utf-8')
		print(data)
		if data[:3] != 'ERR':
			fileSize,fileName = data.strip().split()[1:]
			fileName = 'new_'+fileName
			fileSize = int(fileSize.strip('bytes'))
			self.sock.send(('OK').encode('utf-8'))
			f = open(fileName, 'wb')
			data = self.sock.recv(1024)
			totalRecv = len(data)
			f.write(data)
			print(totalRecv)
			while(totalRecv < int(fileSize)):
				data = self.sock.recv(1024)
				totalRecv += len(data)
				f.write(data)
				print(str((totalRecv/float(fileSize))*100)+"% done")
			print("Completed")
		else:
			print("doesnt Exists")
def Main():
	print("clients")
	host = '192.168.137.50'
	port = 5015

	while(1):
		send = input('Send y/n : ')
		if(send == 'n'):
			s = socket.socket()
			s.connect((host,port))
			input('Enter enter...')
			s.send('Quit'.encode('utf-8'))
			s.close()
			break
		if(send == 'y'):
			s = socket.socket()
			s.connect((host,port))

			t = getFile(s)
			t.start()
			t.join()
			s.close()
if __name__ == '__main__':
	Main()
