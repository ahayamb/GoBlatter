from Tkinter import *
import time
import thread
import socket
import cPickle

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

while not running :
	print 'Masukkan username :'
	userName = raw_input()
	sntObj = {'m' : 'in', 'user' : userName, 'res' : 0}
	clientSocket.sendall(cPickle.dumps(sntObj))

	rcvStr = clientSocket.recv(4096)
	rcvObj = cPickle.loads(rcvStr)
				
	if rcvObj['m'] == 'in' and rcvObj['res'] == 1 : running = True
	else : print 'Username tidak tersedia'

buttonList = []
mainForm = Tk()
mainForm.geometry('900x400+100+200')
mainForm.title('GoBlatter Client - ' + userName)
canvas = Canvas(mainForm, bg = '#00AAFF', width = 420, height = 150)
canvas.place(x = 8, y = 50)

#Constants
tX = 20
tY = 10
tW = 35
tH = 40

scoreVar = IntVar()				#variable bounder
scoreVar.set(0)

categoryVar = StringVar()		#variable bounder
categoryVar.set('Menunggu..')

toVar = IntVar()				#variable bounder
toVar.set(10)

notifVar = StringVar()			#variable bounder
notifVar.set('')

Label(mainForm, text = 'Waktu:', font = ('Consolas', 15)).place(x = 10, y = 10)
toLabel = Label(mainForm, textvariable = toVar, font = ('Consolas', 15, 'bold italic'), foreground = '#00AA22')
toLabel.place(x = 80, y = 10)

Label(mainForm, text = 'Kategori:', font = ('Consolas', 15)).place(x = 130, y = 10)
categoryLabel = Label(mainForm, textvariable = categoryVar, font = ('Consolas', 15, 'bold italic'), foreground = '#00AA22')
categoryLabel.place(x = 235, y = 10)

Label(mainForm, text = 'Notifikasi:', font = ('Consolas', 15)).place(x = 450, y = 10)
notifLabel = Label(mainForm, textvariable = notifVar, font = ('Consolas', 12, 'bold italic'), foreground = '#00AA22', justify = LEFT)
notifLabel.place(x = 450, y = 35)

def buttonClick(num) :
	global idNow
	global wordState
	if buttonList[num].button['state'] != 'disabled' :
		
		buttonList[num].button['state'] = 'disabled'
		sntObj = {}
		sntObj['m'] = 'ans'
		sntObj['ch'] = ''
		sntObj['id'] = idNow
		sntObj['ch'] = buttonList[num].button['text']
		sntObj['state'] = wordState
		clientSocket.sendall(cPickle.dumps(sntObj))

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
		global categoryVar
		global toVar
		global scoreVar
		global idNow
		global alive
		global running
		global buttonList
		global wordState

		while alive :
			
			if running :
				try:
					rcvStr = clientSocket.recv(4096)
					rcvObj = cPickle.loads(rcvStr)

					if rcvObj['m'] == 'out' :
						clientSocket.close()
						running = False
						alive = False
						sys.exit(0)

					elif rcvObj['m'] == 'winmsg' :
						updateNotif(rcvObj['msg'])
						print rcvObj['msg']

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

				except : 
					print 'ternyata eror'
					pass

def keyboardHandler(event) :
	try :
		if event.char.islower() : buttonClick(ord(event.char.capitalize()) - 65)
		elif event.char.isupper() : buttonClick(ord(event.char - 65))
	except : pass

def updateTO(threadName, param) :
	global toVar
	global toLabel
	while True :
		try :
			if running :
				time.sleep(1)
				if toVar.get() > 0 : toVar.set(toVar.get() - 1)
				else : toVar.set(10)

				if toVar.get() <= 3 : toLabel['foreground'] = '#AA0000'
				else : toLabel['foreground'] = '#00AA22'
		except :
			pass

def updateNotif(text) :
	try :
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
	except : pass

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

thread.start_new_thread(updateTO, ('th', 0))
thread.start_new_thread(getQuestion, ('th', 0))

mainForm.bind("<Key>", keyboardHandler)
mainForm.focus_set()

mainForm.mainloop()