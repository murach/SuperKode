#!/usr/bin/env python

import sys
from random import *
from PyKDE4 import kdeui
from PyKDE4 import kdecore
from PyQt4 import QtCore, QtGui			# todo: hg-bild oder so, beim schliessen auch noch ne warnung, row-anzeiger
from string import *				# beim verlieren nen hinweis

class MMind(kdeui.KMainWindow):
	def __init__(self, parent = None):
		global active, led, codeled, hboxhintled, level1, level2, level3, level, colgrid, grid, colorled, complete, row, anz, anz_chosen, pause, highscore, aboutData
		global appName, catalog, programName, version, description, license, copyright, text, homePage, bugEmail
		
		kdeui.KMainWindow.__init__(self)
		
		self.q = QtGui.QWidget(self)				#central widget
		self.setCentralWidget(self.q)
		self.setWindowIcon(QtGui.QIcon('KDE-Mastermind-Icon.png'))
		#self.q.setStyleSheet("QWidget { background-image: No-Ones-Laughing-3.png} ")
		
		new = kdeui.KAction(kdeui.KIcon('document-new'), "&New", self)
		new.setShortcut('Ctrl+N')
		self.connect(new, QtCore.SIGNAL('triggered()'), self.new)
		
		close = kdeui.KAction(kdeui.KIcon('application-exit'), 'Exit', self)
		close.setShortcut('Ctrl+Q')
		self.connect(close, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
		
		clear = kdeui.KAction(kdeui.KIcon('edit-clear-locationbar-ltr'), "Clear row", self)
		clear.setShortcut("Ctrl+C")
		self.connect(clear, QtCore.SIGNAL('triggered()'), self.clear)
		
		highscoreact = kdeui.KAction(kdeui.KIcon('games-highscores'), "Highscores", self)
		highscoreact.setShortcut('Ctrl+H')
		self.connect(highscoreact, QtCore.SIGNAL('triggered()'), self.highscorefkt)
		
		solve = kdeui.KAction(kdeui.KIcon('games-solve'), "Solve", self)
		solve.setShortcut('Ctrl+Alt+S')
		self.connect(solve, QtCore.SIGNAL('triggered()'), self.solve)
		
		submit = kdeui.KAction(kdeui.KIcon('games-endturn'), "Submit", self)
		submit.setShortcut('Return')
		self.connect(submit, QtCore.SIGNAL('triggered()'), self.submit)
		
		pause = kdeui.KAction(kdeui.KIcon('media-playback-pause'), "Pause", self)
		pause.setShortcut("Ctrl+P")
		self.connect(pause, QtCore.SIGNAL('triggered()'), self.pause)
		
		level1 = QtGui.QAction("Level &1", self)
		level1.setCheckable(True)
		level1.setChecked(True)
		self.connect(level1, QtCore.SIGNAL('triggered()'), self.level1)
		
		level2 = QtGui.QAction("Level &2", self)
		level2.setCheckable(True)
		self.connect(level2, QtCore.SIGNAL('triggered()'), self.level2)
		
		level3 = QtGui.QAction("Level &3", self)
		level3.setCheckable(True)
		self.connect(level3, QtCore.SIGNAL('triggered()'), self.level3)
		
		menu = self.menuBar()
		#menu = kdeui.KMenuBar(self)	doesn't really work -> why?
		file = menu.addMenu('&File')
		file.addAction(new)
		file.addAction(clear)
		file.addAction(submit)
		file.addAction(pause)
		file.addAction(solve)
		file.addSeparator()
		file.addAction(highscoreact)
		file.addSeparator()
		file.addAction(close)
		
		levelmenu = menu.addMenu('&Level')
		levelmenu.addAction(level1)
		levelmenu.addAction(level2)
		levelmenu.addAction(level3)
		
		help = self.helpMenu()
		menu.addMenu(help)
		
		self.toolbar = self.addToolBar("Exit")
		#self.toolbar = kdeui.KToolBar(self)
		self.toolbar.addAction(new)
		self.toolbar.addAction(clear)
		self.toolbar.addAction(submit)
		self.toolbar.addAction(pause)
		self.toolbar.addAction(solve)
		self.toolbar.addSeparator()
		self.toolbar.addAction(highscoreact)
		self.toolbar.addSeparator()
		self.toolbar.addAction(close)
		
		self.statusbar = self.statusBar()
		#self.statusbar = kdeui.KStatusBar(self)
		
		start()				#function that sets the hidden code
		
		grid = QtGui.QGridLayout(self.q)
		grid.setMargin(15)
		
		hline = QtGui.QFrame(self)
		hline.setFrameStyle(QtGui.QFrame.HLine)
		hboxcode = QtGui.QHBoxLayout()
		sol = QtGui.QLabel('Code:')
		solgrid = QtGui.QGridLayout()
		solgrid.addWidget(sol, 0, 0, 1, 1)
		solgrid.setMargin(5)
		codeled = ["", "", "", ""]
		
		for i in range(0,4,1):
			codeled[i] = kdeui.KLed()			#these are the four code-LEDs
			codeled[i].setColor(QtGui.QColor('grey'))
			codeled[i].setMinimumSize(30,30)
			codeled[i].setMaximumSize(30,30)
			hboxcode.addWidget(codeled[i])
		
		grid.addLayout(solgrid, 0, 2, 1, 1)
		grid.addLayout(hboxcode, 0, 3, 1, 1)
		
		grid.addWidget(hline, 1, 3, 1, 2)
		
		hboxsol = []
		hinthbox = []
		hboxhintled = []
		led = []
		
		for i in range(0,8,1):
			hboxsol.append("")		#array of hboxlayouts. each line of 4 user-set LEDs is one hbox
			hinthbox.append("")			#array of grids. each grid contains the rating-hint-LEDs
			hboxsol[i] = QtGui.QHBoxLayout()
			hinthbox[i] = QtGui.QGridLayout()
			hinthbox[i].setMargin(5)
			hboxhintled.append("")
			hboxhintled[i] = []
			led.append("")
			led[i] = []
			
			for j in range(0,4,1):
				hboxhintled[i].append("")
				hboxhintled[i][j] = kdeui.KLed()			#LEDs inside the rating-hint-grids
				hboxhintled[i][j].setColor(QtGui.QColor('grey'))
			
			hinthbox[i].addWidget(hboxhintled[i][2], 0, 0)
			hinthbox[i].addWidget(hboxhintled[i][3], 0, 1)
			hinthbox[i].addWidget(hboxhintled[i][0], 1, 0)
			hinthbox[i].addWidget(hboxhintled[i][1], 1, 1)
			grid.addLayout(hinthbox[i], i+2, 2, 1, 1)
			
			for j in range(0,4,1):
				led[i].append("")
				led[i][j] = newLed(i+1, j)		#these are the LEDs the user can give the color
				led[i][j].setColor(QtGui.QColor('grey'))
				led[i][j].setMinimumSize(30,30)
				led[i][j].setMaximumSize(30,30)
				led[i][j].clicked = 0
				hboxsol[i].addWidget(led[i][j])
			
			grid.addLayout(hboxsol[i], i+2, 3, 1, 1)
		
		colgrid = QtGui.QGridLayout()				#grid-layout containing the available colors
		
		colorled = []
		for i in range(0, 3+2*level,1):
			colorled.append("")
			colorled[i] = KLedCustom(i)			#LEDs inside the colgrid
			colorled[i].setMaximumSize(30,30)
			colorled[i].setMinimumSize(30,30)
			if i <= level:
				colgrid.addWidget(colorled[i],i,0)
			if i > level and i <= 2*level+1:
				colgrid.addWidget(colorled[i],i-(level+1),1)
			if i > 2*level+1:
				colgrid.addWidget(colorled[i],i,0,1,2)
				#colorled[i].setAlignment(QtCore.Qt.AlignCenter)
		
		grid.addLayout(colgrid, 3, 0, 5, 1)
		vline = QtGui.QFrame(self)
		vline.setFrameStyle(QtGui.QFrame.VLine)
		grid.addWidget(vline, 0, 1, 10, 1)
		
		spacer1 = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        	grid.addItem(spacer1, 10, 0, 1, 4)
		spacer2 = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        	grid.addItem(spacer2, 0, 3, 10, 1)
		
		self.q.setLayout(grid)
		self.timer = QtCore.QTimer()
		self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.time)
		self.statusbar.showMessage("00:00:00")
		self.timer.start(1000)
	
	def pause(self):
		global paused, led, color, pause
		if paused == True:
			paused = False
			pause.setIcon(kdeui.KIcon('media-playback-pause'))
			pause.setText("Pause")
			for i in range(0,3+2*level,1):
				for j in range(0,4,1):
					for k in range(0,3+2*level,1):
						if led[7-i][j].value == k and led[7-i][j].clicked == 1:
							led[7-i][j].setColor(QtGui.QColor(color[k]))
			self.timer.start(1000)
		else:
			self.timer.stop()
			paused = True
			pause.setIcon(kdeui.KIcon('media-playback-start'))
			pause.setText("Continue")
			for i in range(0, 8, 1):
				for j in range(0,4,1):
					led[i][j].setColor(QtGui.QColor('grey'))
					codeled[j].setColor(QtGui.QColor('grey'))
	
	def submit(self):
		global complete, row, led
		
		if led[row-1][0].clicked == 1 and led[row-1][1].clicked == 1 and led[row-1][2].clicked == 1 and led[row-1][3].clicked == 1:
			complete = True
		
		if complete == True:
			self.rate()
			row -= 1
			complete = False
	
	def solve(self):
		global codeled, pos, row, lost
		for i in range(0,4,1):
			codeled[i].setColor(QtGui.QColor(pos[i]))
		row = 0
		self.timer.stop()
		lost = 1
	
	def rate(self):
		global row, active, led, level, anz, anz_chosen, score, secs
		
		anz_correct = 0
		anz_correct_dummy = 0
		anz_almost = 0
		anz_hit = []
		for i in range(0,3+2*level,1):
			anz_hit.append(0)
		
		for i in range(0,4,1):
			if pos2[i] == led[row-1][i].value:
				anz_correct += 1
				for j in range(0,3+2*level,1):
					if pos2[i] == j:
						anz_hit[j] += 1
		
		if anz_correct == 4:
			anz_correct_dummy = 4
			rowdummy = row
			self.solve()
			row = rowdummy
			score = 1000*level + 2000-secs + row*25
			if score < 0:
				score = 0
			self.timer.stop()
			self.newhighscore()
		
		for i in range(0,3+2*level,1):
			if anz[i] >= anz_chosen[i]:
				anz_almost += anz_chosen[i] - anz_hit[i]
			elif anz_chosen[i] > anz[i]:
				anz_almost += anz[i] - anz_hit[i]
		
		for i in range(0,4,1):
			if anz_correct != 0:
				hboxhintled[row-1][i].setColor(QtGui.QColor('black'))
				hboxhintled[row-1][i].setWhatsThis("One color at the right place.")
				hboxhintled[row-1][i].setToolTip("One color at the right place.")
				anz_correct -= 1
			elif anz_almost != 0:
				hboxhintled[row-1][i].setColor(QtGui.QColor('white'))
				hboxhintled[row-1][i].setWhatsThis("One right color, but at the wrong place.")
				hboxhintled[row-1][i].setToolTip("One right color, but at the wrong place.")
				anz_almost -= 1
		
		for i in range(0,3+2*level, 1):
			anz_chosen[i] = 0
		
		if anz_correct_dummy == 4:
			row = 0
	
	def clear(self):
		global row, led, level, anz_chosen
		for i in range(0,4,1):
			led[row-1][i].value = 0
			led[row-1][i].setColor(QtGui.QColor('grey'))
			led[row-1][i].clicked = 0
		for i in range(0,3+2*level,1):
			anz_chosen[i] = 0
	
	def dialog(self, action):
		global dlg, lost
		if action == "level" and lost == 0:
			dlg = kdeui.KMessageBox.questionYesNo(self, "You are about to change the level. This is going to quit this game. Are you sure?")
		elif action == "level" and lost == 1:
			dlg = 3
		elif action == "new" and lost == 0:
			dlg = kdeui.KMessageBox.questionYesNo(self, "You are about to quit this game. Are you sure?")
		elif action == "new" and lost == 1:
			dlg = 3
	
	def level1(self):
		global active, level2, level3, level, colgrid, dlg, colorled, lost
		
		self.dialog("level")
		if dlg == 3:
			level1.setChecked(True)
			level2.setChecked(False)
			level3.setChecked(False)
			self.coldel()
			level = 1
			self.reset()
			for i in range(0,3+2*level,1):
				active.append(0)
			start()
			lost = 0
		else:
			level1.setChecked(False)
	
	def level2(self):
		global active, level1, level3, level, colgrid, dlg, colorled, lost
		
		self.dialog("level")
		if dlg == 3:
			level1.setChecked(False)
			level2.setChecked(True)
			level3.setChecked(False)
			self.coldel()
			level = 2
			self.reset()
			for i in range(0,3+2*level,1):
				active.append(0)
			start()
			lost = 0
		else:
			level2.setChecked(False)
	
	def level3(self):
		global active, level1, level2, level, colgrid, dlg, colorled, lost
		
		self.dialog("level")
		if dlg == 3:
			level1.setChecked(False)
			level2.setChecked(False)
			level3.setChecked(True)
			self.coldel()
			level = 3
			self.reset()
			for i in range(0,3+2*level,1):
				active.append(0)
			start()
			lost = 0
		else:
			level3.setChecked(False)
	
	def highscorefkt(self):
		self.newwin = highscorewindow()
		self.newwin.show()
	
	def newhighscore(self):
		global highscore, score, namestring, boldrow
		dummy = 10
		for i in range(9,-1,-1):
			if score > highscore[i]:
				dummy = i
		if dummy != 10:
			d = open("highscores", "w")
			for j in range(9,dummy,-1):
				highscore[j] = highscore[j-1]
				namestring[j] = namestring[j-1]
			highscore[dummy] = score	
			text, self.winnername = kdeui.KInputDialog.getText('Highscore!', 'Please enter your name:')
			if self.winnername:
				namestring[dummy] = unicode(text)
			score = 0
			for j in range(0,10,1):
				d.write(namestring[j] + " " + str(highscore[j]) + "\n")
			d.close()
			boldrow = dummy
			self.highscorefkt()
			dummy = 10
		
	def new(self):
		global active, level, dlg
		
		self.dialog("new")
		if dlg == 3:
			self.coldel()
			self.reset()
			for i in range(0,3+2*level,1):
				active.append(0)
			start()
			self.timer.start(1000)
	
	def reset(self):
		global active, led, codeled, hboxhintled, level, colgrid, colorled, secs, lost
		for i in range(0, 8, 1):
			for j in range(0,4,1):
				led[i][j].setColor(QtGui.QColor('grey'))
				led[i][j].value = 0
				led[i][j].clicked = 0
				hboxhintled[i][j].setColor(QtGui.QColor('grey'))
				codeled[j].setColor(QtGui.QColor('grey'))
		active = []
		colorled = []
		for i in range(0, 3+2*level,1):
			colorled.append("")
			colorled[i] = KLedCustom(i)
			colorled[i].setMaximumSize(30,30)
			colorled[i].setMinimumSize(30,30)
			if i <= level:
				colgrid.addWidget(colorled[i],i,0)
			if i > level and i <= 2*level+1:
				colgrid.addWidget(colorled[i],i-(level+1),1)
			if i > 2*level+1:
				colgrid.addWidget(colorled[i],i,0,1,2)
		secs = 0
		lost = 0

	def coldel(self):
		global level, colorled
		for i in range(0,3+2*level,1):
			colorled[i].deleteLater()
			colorled[i] = None
	
	def time(self):
		global secs
		secs += 1
		hours = secs/3600 - (secs%3600)/3600
		if hours < 10:
			hoursstr = "0%i" % hours
		else:
			hoursstr = str(hours)
		minutes = secs/60 - ((secs-hours*3600)%60)/60
		if minutes < 10:
			minutesstr = "0%i" % minutes
		else:
			minutesstr = str(minutes)
		seconds = secs - 60*minutes
		if seconds < 10:
			secondsstr = "0%i" % seconds
		else:
			secondsstr = str(seconds)
		showntime = "%s:%s:%s" % (hoursstr, minutesstr, secondsstr)
		self.statusbar.showMessage(showntime)

class KLedCustom(kdeui.KLed):
	def __init__(self, lednumber, parent = None):
		kdeui.KLed.__init__(self)
		
		self.i = lednumber
		for j in range(0,3+2*level,1):
			if lednumber == j:
				self.setColor(QtGui.QColor(color[j]))	
				
	def mousePressEvent(self, event):
		global active, level
		
		for i in range(0,3+2*level,1):
			if i == self.i:
				active[i] = 1
				self.setState(0)
			else:
				active[i] = 0
				colorled[i].setState(1)

class newLed(kdeui.KLed):
	def __init__(self, led_row, led_col, parent = None):
		kdeui.KLed.__init__(self)
		self.row = led_row
		self.col = led_col
		self.value = 0
	
	def mousePressEvent(self, event):
		global row, active, level, anz_chosen
		
		for i in range(0,3+2*level,1):
			if active[i] == 1 and self.row == row:
				self.setColor(QtGui.QColor(color[i]))
				anz_chosen[i] += 1
				if self.clicked == 1:
					anz_chosen[self.value] -= 1
				self.value = i
				self.clicked = 1


def start():
	global row, anz, anz_chosen, pos, pos2, level
	
	pos = []
	pos2 = []
	anz = []
	anz_chosen = []
	row = 8
	for i in range(0,3+2*level,1):
		anz.append(0)
		anz_chosen.append(0)
	
	for i in range(0,4,1):
		seed()
		pos.append(0)
		pos2.append(0)
		pos[i] = randint(0,3+2*level-1)
		pos2[i] = pos[i]
		
		for j in range(0,3+2*level,1):
			if pos[i] == j:
				pos[i] = color[j]
				anz[j] += 1


class highscorewindow(kdeui.KMainWindow):
	def __init__(self, parent = None):
		global highscore, boldrow, namestring
		
		kdeui.KMainWindow.__init__(self)
		
		self.setWindowTitle("Highscores")
		self.resize(350, 350)
		
		self.widget = QtGui.QWidget(self)
		self.setCentralWidget(self.widget)
		self.grid = QtGui.QGridLayout(self.widget)
		self.grid.setSpacing(0)
		
		self.labelscore = []
		self.labelnumber = []
		self.namestrings = []
		
		for i in range(0,10,1):
			self.labelscore.append("")
			self.labelscore[i] = QtGui.QLabel(str(highscore[i]))
			self.labelscore[i].setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
			self.labelscore[i].setMargin(10)
			
			self.namestrings.append("")
			self.namestrings[i] = QtGui.QLabel(namestring[i])
			self.namestrings[i].setAlignment(QtCore.Qt.AlignCenter)
			
			self.labelnumber.append("")
			self.labelnumber[i] = QtGui.QLabel("#" + str(i+1) + ":")
			self.labelnumber[i].setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
			self.labelnumber[i].setMargin(10)
			
			if i%2 == 0 and i == boldrow:
				self.labelscore[i].setStyleSheet("QLabel {background-color: darkgrey; font: bold} ")
				self.namestrings[i].setStyleSheet("QLabel {background-color: darkgrey; font: bold} ")
				self.labelnumber[i].setStyleSheet("QLabel {background-color: darkgrey; font: bold} ")
			elif i%2 == 0 and i != boldrow:
				self.labelscore[i].setStyleSheet("QLabel {background-color: darkgrey} ")
				self.namestrings[i].setStyleSheet("QLabel {background-color: darkgrey} ")
				self.labelnumber[i].setStyleSheet("QLabel {background-color: darkgrey} ")
			elif i%2 != 0 and i == boldrow:
				self.labelscore[i].setStyleSheet("QLabel {font: bold} ")
				self.namestrings[i].setStyleSheet("QLabel {font: bold} ")
				self.labelnumber[i].setStyleSheet("QLabel {font: bold} ")
			
			self.grid.addWidget(self.labelnumber[i], i, 0)
			self.grid.addWidget(self.namestrings[i], i, 1)
			self.grid.addWidget(self.labelscore[i], i, 2)
		boldrow = 10
		
		self.widget.setLayout(self.grid)


appName = "KDE-Mastermind"
catalog = "KDE-Mastermind"
programName = kdecore.ki18n("KDE-Mastermind")
version = "0.1.6"
description = kdecore.ki18n("A simple KDE4 Mastermind Game")
license     = kdecore.KAboutData.License_GPL_V3
copyright   = kdecore.ki18n("(c) 2009 Thomas Murach")
text        = kdecore.ki18n("This is a KDE4-Mastermind game. \n Rules: Each black rating-stone means that there is one color at the right place.\n Each white stone means there is a correct color, but it is at a wrong place.\n")
homePage    = "http://www.kde-apps.org/content/show.php?content=102968"
bugEmail    = "asiasuppenesser@gmx.de"

aboutData = kdecore.KAboutData(appName, catalog, programName, version, description, license, copyright, text, homePage, bugEmail)
aboutData.setProgramIconName("ktip")

kdecore.KCmdLineArgs.init(sys.argv, aboutData)


level = 1				# initialized level (lowest one). alternatives: 2 and 3
active = []				# array containing information about which color has been chosen
for i in range(0,3+2*level):		# adding entries for the number of colors this level provides
	active.append(0)		#
complete = False			# saying that the first row isn't complete. therefore the code won't be submitted
row = 8					# status-information. which row has to be filled. 8 = on the bottom
color = ["red", "blue", "yellow", "green", "purple", "brown", "orange", "pink", "black"]	# provided colors
secs = 0				# time (starting with 0)
paused = False				# game isn't paused
score = 0				# game isn't solved -> score = 0
lost = 0				# game isn't finished -> lost = 0
boldrow = 10				# for displaying the highscore-info. boldrow = 10 means that none of the rows is
 					# displayed with bold letters, as you didn't reach a highscore right before

highscore = [0,0,0,0,0,0,0,0,0,0]	# standard highscores. are going to be overwritten in the next few lines
namestring = ["-:-", "-:-", "-:-", "-:-", "-:-", "-:-", "-:-", "-:-", "-:-", "-:-"]	# standard names
highscorestring = [0,0,0,0,0,0,0,0,0,0]		# standard complete string of highscores and names

try:
	laufnr = 0									#
	d = open("highscores")								#
	rows = d.readlines()								#
	for z in rows:									#
		highscorestring[laufnr] = z						#
		s = rfind(highscorestring[laufnr], " ")					#
		if s == -1:								#
			highscore[laufnr] = int(highscorestring[laufnr])		# reading out info about highscores
		else:									# and names
			namestring[laufnr] = highscorestring[laufnr][0:s]		#
			highscore[laufnr] = int(highscorestring[laufnr][s+1:-1])	#
		if laufnr == 9:								#
			laufnr = 0							#
		laufnr += 1								#
	d.close()									#

except:											# exception. only used if file 
	pass										# can't be found. names and 
											# highscores get values from above

app = kdeui.KApplication()			# application-name
mastermind = MMind()				# instance of the class MMind
mastermind.show()				# show the main window
sys.exit(app.exec_())				# keeping the main window in the main loop