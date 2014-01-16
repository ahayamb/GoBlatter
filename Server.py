import socket
import thread
import cPickle
import select
import time
import random
import sqlite3

class GoBlatterServer:
	
	def __init__(self, bindParam) :
		
		self.userDB = sqlite3.connect('user.db')
		# if True :
		try : 
			self.userDB.execute("create table USER (username TEXT, password TEXT, poin INT)")
		# if True :
		except : 
			self.userDB.commit()
			print 'tabel sudah ada'
			pass
		print 'terconstruct'
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverSocket.bind(bindParam)
		self.serverSocket.listen(100)
		self.clientProperty = {}
		self.clientProperty[self.serverSocket] = ['server', 0, True]
		self.duelRoom = {}
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
		# deleted = []
		while True :
			time.sleep(1)
			deleted = []
			for i in self.duelRoom :
				# try :
				if True :
					if self.duelRoom[i]['sc1'] == 10 or self.duelRoom[i]['sc2'] == 10 :
						self.clientProperty[ self.duelRoom[i]['p1'] ][2] = False
						self.clientProperty[ self.duelRoom[i]['p2'] ][2] = False
						name1 = self.clientProperty[ self.duelRoom[i]['p1'] ][0]
						name2 = self.clientProperty[ self.duelRoom[i]['p2'] ][0]
						if self.duelRoom[i]['sc1'] == 10 :
							self.duelRoom[i]['p1'].sendall(cPickle.dumps({'m' : 'duelwinmsg', 'poin' : 50, 'msg' : 'ANDA MENANG DUEL MELAWAN ' + name2}))
							self.duelRoom[i]['p2'].sendall(cPickle.dumps({'m' : 'duellosemsg', 'poin': -50,   'msg' : 'ANDA KALAH DUEL MELAWAN ' + name1}))
							self.clientProperty[self.duelRoom[i]['p1']][1] += 50
							self.clientProperty[self.duelRoom[i]['p2']][1] -= 50
						else :
							self.duelRoom[i]['p1'].sendall(cPickle.dumps({'m' : 'duellosemsg', 'poin' : -50, 'msg' : 'ANDA KALAH DUEL MELAWAN ' + name2}))
							self.duelRoom[i]['p2'].sendall(cPickle.dumps({'m' : 'duelwinmsg', 'poin' : 50, 'msg' : 'ANDA MENANG DUEL MELAWAN ' + name1}))
							self.clientProperty[self.duelRoom[i]['p2']][1] += 50
							self.clientProperty[self.duelRoom[i]['p1']][1] -= 50
						deleted.append(i)

					elif self.duelRoom[i]['to'] <= 0 and self.duelRoom[i]['sc1'] != 10 and self.duelRoom[i]['sc2'] != 10 :
						self.duelRoom[i]['to'] = 10;
						self.duelRoom[i]['idquest'] += 1
						num = random.randrange(0, len(self.wordCat))
						self.duelRoom[i]['cat'] = self.wordCat[ num ]
						self.duelRoom[i]['word'] = self.wordData[ num ][ random.randrange(0, len(self.wordData[num])) ]
						
						print i + ' ' + str(self.duelRoom[i]['idquest']) + ' ' + self.duelRoom[i]['word']
						
						sndObj = {'m' : 'duelquest', 'state' : '', 'cat' : self.duelRoom[i]['cat'], 'idquest' : self.duelRoom[i]['idquest']}
						
						# print i + ' : ' + self.duelRoom[i]['word']

						for x in range(len(self.duelRoom[i]['word'])) :
							if self.duelRoom[i]['word'][x] != '_' : sndObj['state'] += ' '
							else : sndObj['state'] += '_'

						sntStr = cPickle.dumps(sndObj)

						self.duelRoom[i]['p1'].sendall(sntStr)
						self.duelRoom[i]['p2'].sendall(sntStr)
					
					elif self.duelRoom[i]['to'] > 0 and (self.duelRoom[i]['sc1'] != 10 and self.duelRoom[i]['sc2'] != 10) :
						self.duelRoom[i]['to'] -= 1

			for i in deleted :
				self.duelRoom.pop(i)

				# except : pass
			

	def runServer(self) :
		
		# thread.start_new_thread(self.listenClient, ('listenClient', 0))

		thread.start_new_thread(self.postQuest, ('postQuest', 0))
		thread.start_new_thread(self.duelHandler, ('duelHandler', 0))
		self.listenClient('listenClient', 0)
		
	
	def listenClient(self, threadName, param) :
		
		while self.running :
			try :
			# if 1 == 1 :
				errorConn = False
				temp = self.serverSocket
				r, w, e = select.select(self.clientProperty.keys(), [], [])
			
				for i in r :
		
					if i == self.serverSocket :
						dummyClt, dummyAddr = i.accept()
						self.clientProperty[dummyClt] = ['client1', 0, False]
						# print 'success'
					
					else :
						temp = i
						rcvStr = i.recv(4096)
						errorConn = True
						rcvObj = cPickle.loads(rcvStr)
						
						if rcvObj['m'] == 'in' :     # m, user, res
							exist = False
							existOnDB = False
							
							for t in self.clientProperty.values() :
								if t[0] == rcvObj['user'] :
									exist = True
									break
							
							if not exist : 
								query = "select * from USER where username = '" + rcvObj['user'] + "' and password = '" + rcvObj['pass'] + "'"
								result = self.userDB.execute(query).fetchall()
								if len(result) == 0 :
									print 'tidak ada'
									self.userDB.execute("insert into USER values ('" + rcvObj['user'] +"', '" + rcvObj['pass'] + "', 0)")
									self.userDB.commit()
									rcvObj['res'] = 0
									rcvObj['msg'] = 'Sukses terdaftar dengan USERNAME ' + rcvObj['user'] + " dengan PASSWORD = " + rcvObj['pass'] + " ..."
									i.sendall(cPickle.dumps(rcvObj))
								else :
									print 'ada'
									self.clientProperty[i][0] = rcvObj['user']
									self.clientProperty[i][1] = result[0][2]
									rcvObj['res'] = 1
									rcvObj['msg'] = "SUKSES LOGIN dg USERNAME : " + rcvObj['user']
									rcvObj['poin'] = result[0][2]
									i.sendall(cPickle.dumps(rcvObj))

								# self.clientProperty[i][0] = rcvObj['user']
								# rcvObj['res'] = 1
								# i.sendall(cPickle.dumps(rcvObj))
									
									if self.timeout > 0 :
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
								rcvObj['msg'] = 'USER SEDANG AKTIF....'
								i.sendall(cPickle.dumps(rcvObj))
								# self.clientProperty.pop(i)
							
						elif rcvObj['m'] == 'duelquestans' :
							strCheck = self.duelRoom[ rcvObj['idduel'] ]['word']
							sndObj = {'m' : 'dueljud', 'res' : 0, 'cat' : self.duelRoom[ rcvObj['idduel'] ]['cat'], 'state' : ''}
							newState = ''
							# print str(rcvObj['idquest']) + ' ' + str(self.duelRoom[ rcvObj['idduel'] ]['idquest'])
							if rcvObj['state'] != strCheck and rcvObj['idquest'] == self.duelRoom[ rcvObj['idduel'] ]['idquest'] :
								if rcvObj['state'].find(rcvObj['ch']) == -1 :
									exist = False
									for x in range(len(strCheck)) :
										if strCheck[x] == rcvObj['ch'] :
											newState += rcvObj['ch']
											exist = True
										else : newState += rcvObj['state'][x]
									rcvObj['state'] = newState
									if newState == strCheck :
										if i == self.duelRoom[rcvObj['idduel']]['p1'] : self.duelRoom[rcvObj['idduel']]['sc1'] += 1
										else : self.duelRoom[rcvObj['idduel']]['sc2'] += 1
										sndObj['res'] = 1
										self.duelRoom[rcvObj['idduel']]['to'] = 0
										self.duelRoom[rcvObj['idduel']]['p1'].sendall(cPickle.dumps({'m' : 'winmsg', 'msg' : str( self.clientProperty[i][0] ) + ' berhasil menjawab'}))
										self.duelRoom[rcvObj['idduel']]['p2'].sendall(cPickle.dumps({'m' : 'winmsg', 'msg' : str( self.clientProperty[i][0] ) + ' berhasil menjawab'}))
							sndObj['state'] = newState
							i.sendall(cPickle.dumps(sndObj))

						elif rcvObj['m'] == 'ans' :  # m, state, ch, res, id
							#sndObj : m, res, cat, state, room
							sndObj = {}
							sndObj['m'] = 'jud'
							sndObj['res'] = 0
							sndObj['cat'] = self.currentWordCat
							newState = ''
							
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
											self.clientProperty[i][1] += sndObj['res']
											msg = self.clientProperty[i][0] + ' + ' + str(self.timeout) + ' poin'
											self.broadcastMsg(msg)
										else : 
											sndObj['res'] = 1
											self.clientProperty[i][1] += 1
									else : 
										sndObj['res'] = -1
										self.clientProperty[i][1] -= 1
									
								else : 
									sndObj['res'] = 0
									newState = rcvObj['state']
								
							else : 
								sndObj['res'] = 0
								newState = rcvObj['state']
							
							sndObj['state'] = newState
							i.sendall(cPickle.dumps(sndObj))

						elif rcvObj['m'] == 'list' :
							clientList = []
							for tt in self.clientProperty :
								if not self.clientProperty[tt][2] : clientList.append(self.clientProperty[tt][0])
							i.sendall(cPickle.dumps({'m' : 'list', 'client' : clientList}))
							# print cPickle.dumps({'m' : 'list', 'client' : clientList})

						elif rcvObj['m'] == 'duelreq' : # m : duelreq, from : dueler, to : dueled
							self.clientProperty[i][2] = True
							
							for tt in self.clientProperty :
								if self.clientProperty[tt][0] == rcvObj['to'] :
									if not self.clientProperty[tt][2] :
										self.clientProperty[tt][2] = True
										tt.sendall(rcvStr)
										# print 'terkirim'
									else :
										self.clientProperty[tt][2] = False
										self.clientProperty[i][2] = False
										# print 'ditolak'
										tt.sendall(cPickle.dumps({'m' : 'duelans', 'from' : rcvObj['from'], 'to' : rcvObj['to'], 'ans' : 0}))
									break

						elif rcvObj['m'] == 'duelans' : # m : duelans, from : dueler, to : dueled, ans : 1 / 0
							if rcvObj['ans'] == 1 :
								for tt in self.clientProperty :
									if self.clientProperty[tt][0] == rcvObj['from'] :
										self.clientProperty[i][2] = True
										self.clientProperty[tt][2] = True

										self.duelRoom[ rcvObj['from'] + rcvObj['to'] ] = { 'p1' : tt, 'p2' : i, 'sc1' : 0, 'sc2' : 0, 'cat' : '', 'word' : '', 'to' : 0, 'idquest' : 0}
										
										tt.sendall(rcvStr)
										break

							else :
								self.clientProperty[i][2] = False
								for tt in self.clientProperty :
									if self.clientProperty[tt][0] == rcvObj['from'] :
										self.clientProperty[tt][2] = False
										tt.sendall(rcvStr)

							# print len(self.duelRoom)

						elif rcvObj['m'] == 'duelcancel' :
							self.clientProperty[i][2] = False
							for tt in self.clientProperty :
								if self.clientProperty[tt][0] == rcvObj['to'] :
									tt.sendall(rcvStr)
									self.clientProperty[tt][2] = False
									break

			except : 
				if not errorConn : 
					self.userDB.execute("update USER set POIN = " + str(self.clientProperty[temp][1]) + " where username = '" + self.clientProperty[temp][0] + "'")
					print 'ERROR KAKAKAKAKAKAKAKAKAKAKA' + str(self.clientProperty[temp][1])
					self.userDB.commit()
					self.clientProperty.pop(temp)
				# print 'jan'
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

			print self.currentWord
			
			for i in range(len(self.currentWord)) :
				if self.currentWord[i] != '_' : sndObj['state'] += ' '
				else : sndObj['state'] += '_'
			
			sndObj['id'] = self.idNow
			sndObj['timeout'] = self.timeout
			sndStr = cPickle.dumps(sndObj)
			
			# Sending to the clients
			for i in self.clientProperty.keys() :
				try :
					if i != self.serverSocket and not self.clientProperty[i][2] and self.clientProperty[i][0] != 'client1' :
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