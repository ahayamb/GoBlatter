from Tkinter import *
import time
import thread
import socket
import cPickle
import msvcrt

userName = ''
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# clientSocket.connect(('10.151.33.2', 9999))
clientSocket.connect(('localhost', 9999))
running = False
alive = True
rcvObj = {}
wordState = ''
idNow = 0
notifLine = 0
idduel = ''
password = ''
tpoin = 0

challenging = False
challenged = False
answertoDuel = False
onDuel = False
objDuelReq = {}

while not running :
	print 'Username : '
	userName = raw_input()
	print 'Password : '
	a = ''
	password = ''
	while True :
		a = msvcrt.getch()
		if ord(a) == 13 : break
		password += a
	sntObj = {'m' : 'in', 'user' : userName, 'res' : 0, 'pass' : password}
	# print sntObj
	clientSocket.sendall(cPickle.dumps(sntObj))
	# print 'terkirimaaaa'

	rcvStr = clientSocket.recv(4096)
	rcvObjs = cPickle.loads(rcvStr)
	
	if rcvObjs['m'] == 'in' and rcvObjs['res'] == 1 : 
		running = True
		poin = rcvObjs['poin']
		print rcvObjs['msg']
	elif rcvObjs['m'] == 'in' and rcvObjs['res'] == 0 : 
		print rcvObjs['msg']

buttonList = []
mainForm = Tk()
mainForm.geometry('900x400+100+200')
mainForm.title('GoBlatter Client - ' + userName)
canvas = Canvas(mainForm, bg = '#00AAFF', width = 420, height = 150)
canvas.place(x = 8, y = 50)

playerList = Listbox(mainForm)
playerList.place(x = 450, y = 210)

#Constants
tX = 20
tY = 10
tW = 35
tH = 40

scoreVar = IntVar()				#variable bounder
scoreVar.set(poin)

categoryVar = StringVar()		#variable bounder
categoryVar.set('Menunggu..')

toVar = IntVar()				#variable bounder
toVar.set(10)

notifVar = StringVar()			#variable bounder
notifVar.set('')

waitVar = IntVar()
waitVar.set(0)

Label(mainForm, text = 'Waktu:', font = ('Consolas', 15)).place(x = 10, y = 10)
toLabel = Label(mainForm, textvariable = toVar, font = ('Consolas', 15, 'bold italic'), foreground = '#00AA22')
toLabel.place(x = 80, y = 10)

Label(mainForm, text = 'Kategori:', font = ('Consolas', 15)).place(x = 130, y = 10)
categoryLabel = Label(mainForm, textvariable = categoryVar, font = ('Consolas', 15, 'bold italic'), foreground = '#00AA22')
categoryLabel.place(x = 235, y = 10)

Label(mainForm, text = 'Notifikasi:', font = ('Consolas', 15)).place(x = 450, y = 10)
notifLabel = Label(mainForm, textvariable = notifVar, font = ('Consolas', 12, 'bold italic'), foreground = '#00AA22', justify = LEFT)
notifLabel.place(x = 450, y = 35)

duelNotif = Label(text = 'Tidak ada permintaan', font = ('Consolas', 15), foreground = '#FF0000', justify = LEFT)
duelNotif.place(x = 450, y = 180)

duelTimer = Label(textvariable = waitVar, font = ('Consolas', 15), foreground = '#FF0000', justify = LEFT)
duelTimer.place(x = 875, y = 180)

duelButton = Button(mainForm, text = 'Duel')
cancelButton = Button(mainForm)

yesButton = Button(mainForm, text = 'Terima')
noButton = Button(mainForm, text = 'Tolak')
yesButton.place(x = 800, y = 210)
noButton.place(x = 850, y = 210)
yesButton['state'] = 'disabled'
noButton['state'] = 'disabled'

def buttonClick(num) :
	global idNow
	global wordState
	global idduel
	if buttonList[num].button['state'] != 'disabled' :
		
		buttonList[num].button['state'] = 'disabled'
		sntObj = {}
		
		if not onDuel :
			sntObj['m'] = 'ans'
			sntObj['ch'] = ''
			sntObj['id'] = idNow
			sntObj['ch'] = buttonList[num].button['text']
			sntObj['state'] = wordState
		else :
			sntObj['m'] = 'duelquestans'
			sntObj['idduel'] = idduel
			sntObj['idquest'] = idNow
			sntObj['ch'] = buttonList[num].button['text']
			sntObj['state'] = wordState
			print sntObj
		clientSocket.sendall(cPickle.dumps(sntObj))

def passiveTimer(threadName, param) :
	global waitVar
	global challenged
	global playerList
	global clientSocket
	global objDuelReq
	global duelNotif
	global onDuel
	global idduel
	global yesButton
	global noButton
	waitVar.set(0)

	while waitVar.get() < 10 and challenged :
		time.sleep(1)
		waitVar.set( waitVar.get() + 1 )

	print 'challenged ' + str(challenged)
	if challenged : 
		challenged = False
		clientSocket.sendall(cPickle.dumps({'m' : 'duelans', 'to' : objDuelReq['to'], 'from' : objDuelReq['from'], 'ans' : 0}))
		duelNotif['text'] = 'Tidak ada permintaan'
		yesButton['state'] = 'disabled'
		noButton['state'] = 'disabled'
		waitVar.set(0)

	else :
		if answertoDuel : 
			clientSocket.sendall(cPickle.dumps({'m' : 'duelans', 'to' : objDuelReq['to'], 'from' : objDuelReq['from'], 'ans' : 1}))
			onDuel = True
			duelNotif['text'] = 'duel dimulai, be prepared'
			idduel = objDuelReq['from'] + objDuelReq['to']
		else : 
			clientSocket.sendall(cPickle.dumps({'m' : 'duelans', 'to' : objDuelReq['to'], 'from' : objDuelReq['from'], 'ans' : 0}))
			duelNotif['text'] = 'Tidak ada permintaan'
			idduel = ''
			# print 'di pasif timer'

	waitVar.set(0)

def updateWordState(word) :
	
	tX = 20
	tY = 10
	tW = 35
	tH = 40

	global canvas
	canvas.delete('all')

	for i in word :
		
		if tX >= canvas.winfo_width() - tW :
			tX = 20
			tY += tH
		
		if i == ' ' : canvas.create_text(tX, tY, anchor = NW, font = ('Consolas', 30), fill = 'white', text = '_')
		elif i == '_' : canvas.create_text(tX, tY, anchor = NW, font = ('Consolas', 30), fill = 'white', text = ' ')
		else : canvas.create_text(tX, tY, anchor = NW, font = ('Consolas', 30), fill = 'white', text = i)
		
		tX += tW

def getQuestion(threadName, param) :

		global rcvObj
		global objDuelReq
		global categoryVar
		global toVar
		global scoreVar
		global idNow
		global alive
		global running
		global buttonList
		global wordState
		global playerList
		global challenging
		global challenged
		global duelButton
		global duelNotif
		global yesButton
		global noButton
		global answertoDuel
		global idduel
		global onDuel

		while alive :
			
			if running :
				# try:
				if True :
					rcvStr = clientSocket.recv(4096)
					rcvObj = cPickle.loads(rcvStr)

					if rcvObj['m'] == 'out' :
						clientSocket.close()
						running = False
						alive = False
						sys.exit(0)

					elif rcvObj['m'] == 'list' :
						
						idx = 0

						for item in rcvObj['client'] :
							if item != userName : 
								playerList.insert(idx, item)
								idx += 1

						if playerList.size() > 0 : duelButton['state'] = 'active'
						else : duelButton['state'] = 'disabled'

					elif rcvObj['m'] == 'duelreq' :
						
						for i in rcvObj :
							objDuelReq[i] = rcvObj[i]
						
						challenged = True
						challenging = False
						answertoDuel = False
						yesButton['state'] = 'active'
						noButton['state'] = 'active'
						duelNotif['text'] = rcvObj['from'] + ' menantang anda untuk duel'
						thread.start_new_thread(passiveTimer, ('threadName', 0))

					elif rcvObj['m'] == 'duelans' :
						print rcvObj
						yesButton['state'] = 'disabled'
						noButton['state'] = 'disabled'
						
						if rcvObj['ans'] == 1 : 
							duelNotif['text'] = 'duel dimulai, be prepared'
							onDuel = True
							print 'perubahan'
							print onDuel
							challenged = False
							# challenging = False #Terakhir
							idduel = rcvObj['from'] + rcvObj['to']

						else : 
							duelNotif['text'] = 'Tidak ada permintaan'
							print 'di terima duelans'
							challenging = False
							challenged = False
							print 'yeyeyeyyeyeyeyeyeyeyeyeye'
							onDuel = False

					elif rcvObj['m'] == 'duelcancel' :
						# print rcvObj
						yesButton['state'] = 'disabled'
						noButton['state'] = 'disabled'
						answertoDuel = False
						challenged = False
						duelNotif['text'] = 'Tidak ada permintaan'
						print 'di duelcancel'

					elif rcvObj['m'] == 'winmsg' :
						updateNotif(rcvObj['msg'])

					elif rcvObj['m'] == 'duellosemsg' :
						duelNotif['text'] = 'Tidak ada permintaan'
						updateNotif(rcvObj['msg'])
						updateNotif('Menyambungkan ke channel utama....')
						scoreVar.set(scoreVar.get() + rcvObj['poin'])
						onDuel = False
						challenging = False
						challenged = False


					elif rcvObj['m'] == 'duelwinmsg' :
						duelNotif['text'] = 'Tidak ada permintaan'
						updateNotif(rcvObj['msg'])
						updateNotif('Menyambungkan ke channel utama....')
						scoreVar.set(scoreVar.get() + rcvObj['poin'])
						onDuel = False
						challenging = False
						challenged = False

					elif rcvObj['m'] == 'duelquest' :
						idNow = rcvObj['idquest']
						wordState = rcvObj['state']
						toVar.set(10)
						updateWordState(rcvObj['state'])
						categoryVar.set(rcvObj['cat'])

						for i in buttonList :
							i.button['state'] = 'active'

					elif rcvObj['m'] == 'quest' :
						idNow = rcvObj['id']
						wordState = rcvObj['state']
						toVar.set(rcvObj['timeout'])
						updateWordState(rcvObj['state'])
						categoryVar.set(rcvObj['cat'])

						for i in buttonList :
							i.button['state'] = 'active'
						
					elif rcvObj['m'] == 'jud' :
						wordState = rcvObj['state']
						scoreVar.set(scoreVar.get() + rcvObj['res'])
						updateWordState(rcvObj['state'])
						categoryVar.set(rcvObj['cat'])

					elif rcvObj['m'] == 'dueljud' :
						wordState = rcvObj['state']
						updateWordState(rcvObj['state'])
						categoryVar.set(rcvObj['cat'])

				# except : 
				# 	clientSocket.close()
				# 	mainForm.destroy()
				# 	exit(10)
				# 	pass

def keyboardHandler(event) :
	# try :
	if True :
		if event.char.islower() : buttonClick(ord(event.char.capitalize()) - 65)
		elif event.char.isupper() : buttonClick(ord(event.char - 65))
	# except : pass

def updateTO(threadName, param) :
	global toVar
	global toLabel
	while True :
		# try :
		if True :
			if running :
				time.sleep(1)
				if toVar.get() > 0 : toVar.set(toVar.get() - 1)
				else : 
					toVar.set(10)
					toLabel['foreground'] = '#00AA22'

				if toVar.get() <= 3 : toLabel['foreground'] = '#AA0000'
		# except : pass

def updateNotif(text) :
	# try :
	if True :
		global notifVar
		global notifLabel
		global toVar
		global notifLine
		if notifVar.get() == '' : notifVar.set('- ' + text)
		else : 
			if notifLine < 6 : 
				notifVar.set(notifVar.get() + '\n- ' + text)
				notifLine += 1
			else :
				s = notifVar.get()
				notifVar.set(s[s.find('\n') + 1 : ] + '\n- ' + text)
	# except : pass

class GoButton :
	def __init__(self, num, px, py, master) :
		self.button = Button(master)
		self.id = num
		self.button.config(command = lambda : buttonClick(self.id))
		self.button.place(x = px, y = py)
		self.button['state'] = 'active'

posX = 20
posY = 210

for i in range(65, 91) :

	if (i - 65) % 10 == 0 and i != 65 :
		posX = 20
		posY += 60

	temp = GoButton(i - 65, posX, posY, mainForm)
	temp.button.config(font = ('Consolas', 20), text = str(unichr(i)), anchor = CENTER, relief = GROOVE, disabledforeground = '#00AA22')
	buttonList.append(temp)
	posX += 40

Label(mainForm, text = 'Poin:', font = ('Consolas', 15)).place(x = posX + 50, y = posY + 15)
scoreLabel = Label(mainForm, textvariable = scoreVar, font = ('Consolas', 15, 'bold italic'), foreground = '#00AA22')
scoreLabel.place(x = posX + 110, y = posY + 15)

refreshButton = Button(mainForm, text = 'Segarkan daftar')
refreshButton.place(x = 580, y = 210)

def getPlayerList() :
	global clientSocket
	global playerList
	global duelButton
	global yesButton
	global noButton
	global cancelButton
	global refreshButton
	duelButton['state'] = 'disabled'
	cancelButton['state'] = 'disabled'
	yesButton['state'] = 'disabled'
	noButton['state'] = 'disabled'
	refreshButton['state'] = 'active'

	clientSocket.sendall(cPickle.dumps({'m' : 'list'}))
	playerList.delete(0, playerList.size())
	playerList['state'] = 'normal'

refreshButton['command'] = getPlayerList

duelButton.place(x = 580, y = 240)

cancelButton.place(x = 580, y = 270)

def duelreq(to) :
	global clientSocket
	global userName
	clientSocket.sendall(cPickle.dumps({'m' : 'duelreq', 'to' : to, 'from' : userName}))

def activeTimer(threadName, param) :
	global waitVar
	global challenging
	global playerList
	global clientSocket
	global duelNotif
	global onDuel
	waitVar.set(0)

	while waitVar.get() < 10 and challenging :
		time.sleep(1)
		waitVar.set( waitVar.get() + 1 )

	print onDuel
	if challenging and not onDuel :
		challenging = False
		cancelButton['state'] = 'disabled'
		duelButton['state'] = 'active'
		playerList['state'] = 'normal'
	elif challenging == False and onDuel == False :
		print 'masuk sini'
		clientSocket.sendall(cPickle.dumps({'m' : 'duelcancel', 'to' : playerList.get(playerList.curselection(), last = None), 'from' : userName}))

	waitVar.set(0)

def duelPlayer() :
	# m : 'duelreq', to : dueled, from : username
	global challenging
	global challenged
	global duelButton
	global cancelButton
	global playerList
	global yesButton
	global noButton
	global onDuel

	if not challenged and not onDuel :
		duelButton['state'] = 'disabled'
		cancelButton['state'] = 'active'
		playerList['state'] = 'disabled'
		yesButton['state'] = 'disabled'
		noButton['state'] = 'disabled'
		challenging = True
		challenged = False
		duelreq(playerList.get(playerList.curselection(), last = None))
		thread.start_new_thread(activeTimer, ('activeTimer', 0))

def dropDuel() :
	global challenging
	global challenged
	global cancelButton
	global duelButton
	global playerList
	global yesButton
	global noButton
	challenged = False
	challenging = False
	cancelButton['state'] = 'disabled'
	playerList['state'] = 'normal'
	yesButton['state'] = 'disabled'
	noButton['state'] = 'disabled'
	duelButton['state'] = 'active'

def recDuel() :
	global challenging
	global challenged
	global answertoDuel
	global yesButton
	global onDuel

	challenged = False
	challenging = False
	answertoDuel = True
	onDuel = True
	yesButton['state'] = 'disabled'
	noButton['state'] = 'disabled'
	playerList['state'] = 'normal'
	duelNotif['text'] = 'duel dimulai, be prepared'

def rejDuel() :
	global challenging
	global challenged
	global answertoDuel
	global playerList

	challenged = False
	challenging = False
	answertoDuel = False
	print 'hahahahahahahahhahahahahha'
	onDuel = False
	yesButton['state'] = 'disabled'
	noButton['state'] = 'disabled'
	playerList['state'] = 'normal'

cancelButton['text'] = 'Batal'
cancelButton['command'] = dropDuel
duelButton['command'] = duelPlayer
duelButton['state'] = 'disabled'
cancelButton['state'] = 'disabled'

yesButton['command'] = recDuel
noButton['command'] = rejDuel

thread.start_new_thread(updateTO, ('th', 0))
thread.start_new_thread(getQuestion, ('th', 0))

mainForm.bind("<Key>", keyboardHandler)
mainForm.focus_set()

mainForm.mainloop()