import socket
import cPickle
import thread
import sys
import os
import msvcrt
import time

class GoBlatterClient:

	def __init__(self, connectParam) :

		self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clientSocket.connect(connectParam)
		self.running = False
		self.alive = True
		self.poin = 0
		self.userName = ''
		self.timeout = 0
		self.idNow = 0
		self.rcvStr = {}

	def register(self) :

		while not self.running:
			print 'Masukkan username :'
			self.userName = raw_input()
			sntObj = {'m' : 'in', 'user' : self.userName, 'res' : 0}
			self.clientSocket.sendall(cPickle.dumps(sntObj))

			rcvStr = self.clientSocket.recv(4096)
			self.rcvObj = cPickle.loads(rcvStr)
				
			if self.rcvObj['m'] == 'in' and self.rcvObj['res'] == 1 :
				self.running = True

			if self.running == False : 
				os.system('cls')
				print 'Username tidak tersedia'

		print 'Sukses terdaftar dengan username :', self.userName

		self.runClient()

	def printState(self, state, cat) :

		os.system('cls')
		printed = ''
		if state[0] == ' ': printed += '_ '
		else : printed += (state[0] + ' ')

		for i in range(1, len(state)):
			if state[i] == ' ': printed += '_ '
			elif state[i] == '_' : printed += '   '
			else : printed += (state[i] + ' ')
			
		print 'Kategori :', cat
		print printed
		print 'Panjang karakter :', len(cat)
		print 'Sisa waktu :', self.timeout
		print '\nPoin :', self.poin

	def inputing(self, threadName, param) :
	
		sntObj = {}
		sntObj['m'] = 'ans'
		sntObj['ch'] = ''
		
		while self.alive :

			if self.running :

				try :
					a = msvcrt.getch()
					a = a.capitalize()
					sntObj['id'] = self.idNow
					sntObj['ch'] = a
					sntObj['state'] = self.rcvObj['state']
					self.clientSocket.sendall(cPickle.dumps(sntObj))
				
				except : pass

	def updateView(self, threadName, param) :

		while self.alive :
			
			if self.running :
				
				try :
					printState(self.rcvObj['state'], self.rcvObj['cat'])
					time.sleep(1)
					self.timeout -= 1
				
				except : pass

	def getQuestion(self, threadName, param) :
	
		while self.alive :
			
			if self.running :
				try:
				
					rcvStr = self.clientSocket.recv(4096)
					self.rcvObj = cPickle.loads(rcvStr)

					if self.rcvObj['m'] == 'out' :
						self.clientSocket.close()
						self.running = False
						self.alive = False
						sys.exit(0)

					elif self.rcvObj['m'] == 'quest' :
						self.idNow = self.rcvObj['id']
						self.timeout = self.rcvObj['timeout']
						self.printState(self.rcvObj['state'], self.rcvObj['cat'])
					
					elif self.rcvObj['m'] == 'jud' :
						self.poin += self.rcvObj['res']
						self.printState(self.rcvObj['state'], self.rcvObj['cat'])
				
				except : pass

	def runClient(self) :

		thread.start_new_thread(self.getQuestion, ('th', 0))
		thread.start_new_thread(self.inputing, ('th1', 0))

		# thread.start_new_thread(self.updateView, ('th', 0))

		while self.running : pass

myClient = GoBlatterClient(('localhost', 9999))
myClient.register()