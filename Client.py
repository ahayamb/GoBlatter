import socket
import cPickle
import thread
import sys
import os, msvcrt, time

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect(('localhost', 9999))
sndObj = {'m' : 'in', 'user' : 'paijox', 'res' : 0}
clientSocket.sendall(cPickle.dumps(sndObj))
running = True
rcvObj = {}
idNow = 0
poin = 0
timeout = 0

def printState(state, cat):
	
	os.system('cls')
	printed = ''
	if state[0] == ' ': printed += '_ '
	else : printed += (state[0] + ' ')
		
	for i in range(1, len(state)):
		if state[i] == ' ': printed += '_ '
		else : printed += (state[i] + ' ')
		
	print 'Kategori :', cat
	print printed
	print 'Panjang karakter :', len(cat)
	print 'Sisa waktu :', timeout
	print '\nPoin :', poin

def inputing(threadName, param):
	
	sntObj = {}
	sntObj['m'] = 'ans'
	sntObj['ch'] = ''
	while True:
		try:
			a = msvcrt.getch()
			a = a.capitalize()
			sntObj['id'] = idNow
			sntObj['ch'] = a
			sntObj['state'] = rcvObj['state']
			clientSocket.sendall(cPickle.dumps(sntObj))
		except:
			pass

def updateView(threadName, param):
	
	global timeout
	while True:
		try:
			printState(rcvObj['state'], rcvObj['cat'])
			time.sleep(1)
			timeout -= 1
		except:
			pass

def getQuestion(threadName, param):
	
	global running
	global rcvObj
	global idNow
	global poin
	global timeout
	while True:
		try:
			rcvStr = clientSocket.recv(4096)
			rcvObj = cPickle.loads(rcvStr)
			if rcvObj['m'] == 'in' and rcvObj['res'] == 0:
				clientSocket.close()
				running = False
				sys.exit(1)
			
			elif rcvObj['m'] == 'quest':
				idNow = rcvObj['id']
				timeout = rcvObj['timeout']
				printState(rcvObj['state'], rcvObj['cat'])
			
			elif rcvObj['m'] == 'jud':
				poin += rcvObj['res']
				printState(rcvObj['state'], rcvObj['cat'])
		except:
			pass

thread.start_new_thread(getQuestion, ('th', 0))
thread.start_new_thread(inputing, ('th', 0))
# thread.start_new_thread(updateView, ('th', 0))

while running:
	pass