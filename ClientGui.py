from Tkinter import *
import time
import thread

buttonList = []
mainForm = Tk()
mainForm.geometry('800x400+100+200')
mainForm.title('GoBlatter Client')
canvas = Canvas(mainForm, bg = '#00AAFF', width = 420, height = 150)
canvas.place(x = 8, y = 50)
nameList = ['AHMAD', 'HAYAM', 'BRILIAN']

#Constants
tX = 20
tY = 10
tW = 35
tH = 40
scoreVar = IntVar()
scoreVar.set(1000)
categoryVar = StringVar()
categoryVar.set('Klub Bola')
toVar = IntVar()
toVar.set(10)
notifVar = StringVar()
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
	if buttonList[num].button['state'] != 'disabled' :
		buttonList[num].button['state'] = 'disabled'
		updateWord(buttonList[num].button['text'])

def keyboardHandler(event) :
	if event.char.islower() :
		buttonClick(ord(event.char.capitalize()) - 65)
	elif event.char.isspace() :
		updateWord(' ')
		for i in buttonList :
			i.button['state'] = 'active'

def updateWord(character) :
	global canvas
	global tX
	global tY
	global tH
	global tW
	if tX >= canvas.winfo_width() - tW :
		tX = 20
		tY += tH
	
	canvas.create_text(tX, tY, anchor = NW, font = ('Consolas', 30), fill = 'white', text = character)
	tX += tW

def updateTO(threadName, param) :
	global toVar
	global toLabel
	while True :
		time.sleep(1)
		if toVar.get() > 0 : toVar.set(toVar.get() - 1)
		else : toVar.set(10)

		if toVar.get() <= 3 : toLabel['foreground'] = '#AA0000'
		else : toLabel['foreground'] = '#00AA22'

def updateNotif(threadName, param) :
	global notifVar
	global notifLabel
	global toVar
	i = 0
	while True :
		if i >= len(nameList) : i = 0
		if toVar.get() == 10 : notifVar.set('- ' + nameList[i] + ' berhasil menjawab')
		else : notifVar.set(notifVar.get() + '\n- ' + nameList[i] + ' berhasil menjawab')
		i += 1
		time.sleep(4)


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
	temp.button.flash()
	buttonList.append(temp)
	posX += 40

Label(mainForm, text = 'Poin:', font = ('Consolas', 15)).place(x = posX + 5, y = posY + 10)
scoreLabel = Label(mainForm, textvariable = scoreVar, font = ('Consolas', 15, 'bold italic'), foreground = '#00AA22')
scoreLabel.place(x = posX + 65, y = posY + 10)

thread.start_new_thread(updateTO, ('th', 0))
thread.start_new_thread(updateNotif, ('th', 0))

mainForm.bind("<Key>", keyboardHandler)
mainForm.focus_set()

mainForm.mainloop()