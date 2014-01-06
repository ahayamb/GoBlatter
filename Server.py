import socket
import thread
import cPickle
import select
import time
import random

class GoBlatterServer:
	
	def __init__(self, bindParam) :
		
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverSocket.bind(bindParam)
		self.serverSocket.listen(100)
		self.clientProperty = {}
		self.clientProperty[self.serverSocket] = ['server', 0, False]
		self.duelRoom = []
		self.running = True
		self.currentWord = ''
		self.currentWordCat = ''
		self.wordCat = ['NAMA KOTA', 'NEGARA', 'NAMA BUAH', 'KLUB BOLA']
		self.wordData = {}
		self.idNow = 0
		self.timeout = 3
		self.initWordBank()
		
	def broadcastMsg(self, msg) :

		sndObj = {}
		print 'Haha'
		sndObj['m'] = 'winmsg'
		sndObj['msg'] = msg
		for i in self.clientProperty.keys() :
			if i != self.serverSocket :
				i.sendall(cPickle.dumps(sndObj))

	def initWordBank(self) :  
		
		self.wordData[0] = ['ACHEN', 'BOJONEGORO', 'SURABAYA', 'JAKARTA', 'BANDUNG', 'SEMARANG', 'PALEMBANG', 'SERANG', 'TANGERANG', 'MAKASSAR']
		self.wordData[1] = ['INDONESIA', 'BRAZIL', 'MALAYSIA', 'SINGAPURA', 'THAILAND', 'CHINA', 'ARGENTINA', 'JERMAN', 'BELANDA', 'VENEZUELA']
		self.wordData[2] = ['APEL', 'NANAS', 'JERUK', 'MANGGA', 'DURIAN', 'ANGGUR', 'SIMALAKAMA', 'BUAH_NAGA', 'DELIMA', 'SIRSAK']
		self.wordData[3] = ['REAL_MADRID', 'INTER_MILAN', 'BAYERN_MUENCHEN', 'CHELSEA', 'ARSENAL', 'MANCHESTER_UNITED', 'LIVERPOOL', 'ASTON_VILA']
		
	def duelHandler(self, threadName, param) :

		while self.running :
			
			if len(self.duelRoom) > 0 : time.sleep(1)

			for i in range(len(self.duelRoom)) :
				
				if self.duelRoom[i][4] > 0 : self.duelRoom[i][4] -= 1

				else :
					
					sndObj = {'m' : 'duelquest', 'state' : '', 'room' : i, 'cat' : ''}
					num = random.randrange(0, len(self.wordCat))
					self.duelRoom[i][4] = self.wordCat[ num ]
					sndObj['cat'] = self.duelRoom[i][4]
					self.duelRoom[i][5] = self.wordData[ num ][ random.randrange(0, len(self.wordData[num])) ] 
					sndObj['cat'] = self.duelRoom[i][5]
					
					for it in range(len(self.duelRoom[i][5])) :
						if self.duelRoom[i][5][it] != '_' : sndObj['state'] += ' '
						else : sndObj['state'] += '_'

					sntStr = cPickle.dumps(sndObj)

					self.duelRoom[i][0].sendall(sntStr)
					self.duelRoom[i][1].sendall(sntStr)

					self.duelRoom[i][4] = 10

	def runServer(self) :
		
		# thread.start_new_thread(self.listenClient, ('listenClient', 0))

		thread.start_new_thread(self.postQuest, ('postQuest', 0))
		self.listenClient('listenClient', 0)
		
		# while self.running : pass
	
	def listenClient(self, threadName, param) :
		
		while self.running :
			try :
				errorConn = False
				r, w, e = select.select(self.clientProperty.keys(), [], [])
					
				for i in r :
		
					if i == self.serverSocket :
						dummyClt, dummyAddr = i.accept()
						self.clientProperty[dummyClt] = ['client1', 0, False]
						print 'success'
					
					else :
						rcvStr = i.recv(4096)
						rcvObj = cPickle.loads(rcvStr)
						
						if rcvObj['m'] == 'in' :     # m, user, res
							exist = False
							
							for t in self.clientProperty.values() :
								if t[0] == rcvObj['user'] :
									exist = True
									break
							
							if not exist: 
								self.clientProperty[i][0] = rcvObj['user']
								rcvObj['res'] = 1
								i.sendall(cPickle.dumps(rcvObj))
									
								if (self.timeout > 0) :
									sndObj = {}
									sndObj['m'] = 'quest'
									sndObj['state'] = ''
									num = random.randrange(0, len(self.wordCat))
									self.currentWordCat = self.wordCat[ num ]
									self.currentWord = self.wordData[ num ][ random.randrange(0, len(self.wordData[num])) ] 
									sndObj['cat'] = self.currentWordCat
									
									for x in range(len(self.currentWord)) :
										if self.currentWord[x] != '_' : sndObj['state'] += ' '
										else : sndObj['state'] += '_'

									sndObj['id'] = self.idNow
									sndObj['timeout'] = self.timeout
									i.sendall(cPickle.dumps(sndObj))
								
							
							else:
								rcvObj['res'] = 0
								i.sendall(cPickle.dumps(rcvObj))
								self.clientProperty.pop(i)
							
						elif rcvObj['m'] == 'ans' :  # m, state, ch, res, id
							#sndObj : m, res, state
							sndObj = {}
							sndObj['m'] = 'jud'
							sndObj['res'] = 0
							sndObj['cat'] = self.currentWordCat
							newState = ''
							# print self.clientProperty[i]
							if rcvObj['id'] == self.idNow and rcvObj['state'] != self.currentWord:
									
								if rcvObj['state'].find(rcvObj['ch']) == -1 : 
									exist = False
									
									for x in range(len(self.currentWord)) :
										if self.currentWord[x] == rcvObj['ch'] :
											newState += rcvObj['ch']
											exist = True
										else : newState += rcvObj['state'][x]
									
									if exist :
										if newState == self.currentWord : 
											sndObj['res'] = self.timeout
											msg = self.clientProperty[i][0] + ' berhasil menjawab mendapat poin ' + str(self.timeout)
											self.broadcastMsg(msg)
										else : sndObj['res'] = 1
									else : sndObj['res'] = -1
									
								else : 
									sndObj['res'] = 0
									newState = rcvObj['state']
								
							else : 
								sndObj['res'] = 0
								newState = rcvObj['state']
							
							sndObj['state'] = newState
							i.sendall(cPickle.dumps(sndObj))

						elif rcvObj['m'] == 'duelreq' : # m : duelreq, from : dueler, to : dueled
							for tt in self.clientProperty :
								if self.clientProperty[tt] == rcvObj['to'] :
									tt.sendall(rcvStr)
									break

						elif rcvObj['m'] == 'duelans' : # m : duelans, from : dueler, to : dueled, ans : 1 / 0
							if rcvObj['ans'] == 1 :
								for tt in self.clientProperty :
									if self.clientProperty[tt][0] == rcvObj['from'] :
										self.duelRoom.append([i, tt, 0, 0, 0, 'cat', 'word'])	# player1, player2, score1, score2, timeout, word
										self.clientProperty[i][2] = True
										self.clientProperty[tt][2] = True
										tt.sendall(rcvStr)
										break
							else :
								for tt in self.clientProperty :
									if self.clientProperty[tt][0] == rcvObj['from'] :
										tt.sendall(rcvStr)

						elif rcvObj['m'] == 'duelcancel' :
							for tt in self.clientProperty :
								if self.clientProperty[tt][0] == rcvObj['to'] :
									tt.sendall(rcvStr)
									break

			except : 
				print 'error di sini kaka'
				pass
			
	def postQuest(self, threadName, param) :        
		
		while self.running : # m, state, bebas, id, timeout
			self.timeout = 10
			
			#Initialize sent question
			sndObj = {}
			sndObj['m'] = 'quest'
			sndObj['state'] = ''
			num = random.randrange(0, len(self.wordCat))
			self.currentWordCat = self.wordCat[ num ]
			self.currentWord = self.wordData[ num ][ random.randrange(0, len(self.wordData[num])) ] 
			sndObj['cat'] = self.currentWordCat
			for i in range(len(self.currentWord)) :
				if self.currentWord[i] != '_' : sndObj['state'] += ' '
				else : sndObj['state'] += '_'
			
			sndObj['id'] = self.idNow
			sndObj['timeout'] = self.timeout
			sndStr = cPickle.dumps(sndObj)
			
			# Sending to the clients
			for i in self.clientProperty.keys() :
				try :
					if i != self.serverSocket and not self.clientProperty[i][2] :
						i.sendall(sndStr)
				except :
					print 'error sending to', i
					self.clientProperty.pop(i)
					pass
			
			while self.timeout > 0 :
				time.sleep(1)
				self.timeout -= 1
			
			self.idNow += 1

# myServer = GoBlatterServer(('10.151.33.2', 9999))
myServer = GoBlatterServer(('localhost', 9999))
myServer.runServer()