#!/usr/bin/env python

import sys
from random import *
from PyKDE4 import kdeui
from PyKDE4 import kdecore
from PyQt4 import QtCore, QtGui			#todo: hg-bild oder so

appName = "KMastermind"
catalog = ""
programName = kdecore.ki18n("KMastermind")
version = "0.1"
description = kdecore.ki18n("A simple KDE4 Mastermind Game")
license     = kdecore.KAboutData.License_GPL
copyright   = kdecore.ki18n("(c) 2009 Thomas Murach")
text        = kdecore.ki18n("test")
homePage    = "www.kommtnoch.com"
bugEmail    = "asiasuppenesser@gmx.de"
aboutData = kdecore.KAboutData(appName, catalog, programName, version, description, license, copyright, text, homePage, bugEmail)

kdecore.KCmdLineArgs.init(sys.argv, aboutData)

class MMind(kdeui.KMainWindow):
	def __init__(self, parent = None):
		global active, led, codeled, hboxhintled, level1, level2, level3, level, colgrid, grid, colorled, complete, row, anz, anz_chosen, pause
		global appName, catalog, programName, version, description, license, copyright, text, homePage, bugEmail, aboutData
		
		kdeui.KMainWindow.__init__(self)
		
		self.q = QtGui.QWidget(self)				#central widget
		self.setCentralWidget(self.q)
		
		new = kdeui.KAction(kdeui.KIcon('document-new'), "&New", self)
		new.setShortcut('Ctrl+N')
		self.connect(new, QtCore.SIGNAL('triggered()'), self.new)
		
		close = kdeui.KAction(kdeui.KIcon('application-exit'), 'Exit', self)
		close.setShortcut('Ctrl+Q')
		self.connect(close, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
		
		clear = kdeui.KAction(kdeui.KIcon('edit-clear-locationbar-rtl'), "Clear row", self)
		clear.setShortcut("Ctrl+C")
		self.connect(clear, QtCore.SIGNAL('triggered()'), self.clear)
		
		highscore = kdeui.KAction(kdeui.KIcon('games-highscores'), "Highscores", self)
		highscore.setShortcut('Ctrl+H')
		self.connect(highscore, QtCore.SIGNAL('triggered()'), self.highscore)
		
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
		#menu = kdeui.KMenuBar(self)
		file = menu.addMenu('&File')
		file.addAction(new)
		file.addAction(clear)
		file.addAction(submit)
		file.addAction(pause)
		file.addAction(solve)
		file.addAction(highscore)
		file.addSeparator()
		file.addAction(close)
		
		levelmenu = menu.addMenu('&Level')
		levelmenu.addAction(level1)
		levelmenu.addAction(level2)
		levelmenu.addAction(level3)
		
		help = self.helpMenu("&Help")
		#help.addData(aboutData)
		menu.addMenu(help)
		
		self.toolbar = self.addToolBar("Exit")
		#self.toolbar = kdeui.KToolBar(self)
		self.toolbar.addAction(new)
		self.toolbar.addAction(clear)
		self.toolbar.addAction(submit)
		self.toolbar.addAction(pause)
		self.toolbar.addAction(solve)
		self.toolbar.addSeparator()
		self.toolbar.addAction(highscore)
		self.toolbar.addSeparator()
		self.toolbar.addAction(close)
		
		self.statusbar = self.statusBar()
		#self.statusbar = kdeui.KStatusBar(self)
		
		start()				#function that sets the hidden code
		
		grid = QtGui.QGridLayout(self.q)
		grid.setMargin(15)
		
		frame = QtGui.QFrame(self)
		frame.setFrameStyle(QtGui.QFrame.Box)	#QFrame.HLine
		frame.setLineWidth(1)
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
		
		solgrid.addLayout(hboxcode, 0, 1)
		frame.setLayout(solgrid)
		grid.addWidget(frame, 0, 2, 1, 2)
		#grid.addLayout(hboxcode, 0, 3, 1, 1)
		
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
			grid.addLayout(hinthbox[i], i+1, 2, 1, 1)
			
			for j in range(0,4,1):
				led[i].append("")
				led[i][j] = newLed(i+1, j)		#these are the LEDs the user can give the color
				led[i][j].setColor(QtGui.QColor('grey'))
				led[i][j].setMinimumSize(30,30)
				led[i][j].setMaximumSize(30,30)
				led[i][j].clicked = 0
				hboxsol[i].addWidget(led[i][j])
			
			grid.addLayout(hboxsol[i], i+1, 3, 1, 1)
		
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
		
		grid.addLayout(colgrid, 2, 1, 5, 1)
		
		spacer1 = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        	grid.addItem(spacer1, 0, 1, 9, 1)
		spacer2 = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        	grid.addItem(spacer2, 0, 4, 9, 1)
		
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
		
		for i in range(0,3+2*level,1):
			if anz[i] >= anz_chosen[i]:
				anz_almost += anz_chosen[i] - anz_hit[i]
			elif anz_chosen[i] > anz[i]:
				anz_almost += anz[i] - anz_hit[i]
		
		for i in range(0,4,1):
			if anz_correct != 0:
				hboxhintled[row-1][i].setColor(QtGui.QColor('black'))
				anz_correct -= 1
			elif anz_almost != 0:
				hboxhintled[row-1][i].setColor(QtGui.QColor('white'))
				anz_almost -= 1
		
		for i in range(0,3+2*level, 1):
			anz_chosen[i] = 0
		
		if anz_correct == 4:
			self.solve()
			score = 1000*level + 2000-secs + (8-row)*25
			if score < 0:
				score = 0
			self.timer.stop()
			self.newhighscore()
	
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
		elif action == "new" and lost == 0:
			dlg = kdeui.KMessageBox.questionYesNo(self, "You are about to quit this game. Are you sure?")
	
	def level1(self):
		global active, level2, level3, level, colgrid, dlg
		
		self.dialog("level")
		if dlg == 3:
			level1.setChecked(True)
			level2.setChecked(False)
			level3.setChecked(False)
			self.coldel()
			level = 1
			dummy = 0
			self.reset()
			for i in range(0,3+2*level,1):
				active.append(0)
			start()
		else:
			level1.setChecked(False)
	
	def level2(self):
		global active, level1, level3, level, colgrid, dlg
		
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
			self.q.update()
		else:
			level2.setChecked(False)
	
	def level3(self):
		global active, level1, level2, level, colgrid, dlg
		
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
			colgrid.update()
			self.q.update()
		else:
			level3.setChecked(False)
	
	def highscore(self):
		self.newwin = highscorewindow()
		self.newwin.show()
	
	def newhighscore(self):
		global highscore, score
		for i in range(0,10,1):
			if score > highscore[i]:
				d = open("highscores", "w")
				for j in range(9,i-1,-1):
					highscore[j] = highscore[j-1]
				highscore[i] = score
				score = 0
				for j in range(0,10,1):
					d.write(str(highscore[j]) + "\n")
				d.close()
		
	def new(self):
		global active, level, dlg
		
		self.dialog("new")
		if dlg == 3:
			self.reset()
			for i in range(0,3+2*level,1):
				active.append(0)
			start()
	
	def reset(self):
		global active, led, codeled, hboxhintled, level, colgrid, colorled, secs
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
			else:
				active[i] = 0

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
		global highscore
		
		kdeui.KMainWindow.__init__(self)
		
		self.setWindowTitle("Highscores")
		
		self.widget = QtGui.QWidget(self)
		self.setCentralWidget(self.widget)
		self.grid = QtGui.QGridLayout(self.widget)
		self.grid.setSpacing(10)
		
		self.labelscore = []
		self.labelnumber = []
		
		for i in range(0,10,1):
			self.labelscore.append(0)
			self.labelscore[i] = QtGui.QLabel(str(highscore[i]))
			self.labelscore[i].setAlignment(QtCore.Qt.AlignRight)
			self.grid.addWidget(self.labelscore[i], i, 1)
			
			self.labelnumber.append(0)
			self.labelnumber[i] = QtGui.QLabel("#" + str(i+1) + ":")
			self.labelnumber[i].setAlignment(QtCore.Qt.AlignLeft)
			self.grid.addWidget(self.labelnumber[i], i, 0)
		
		self.widget.setLayout(self.grid)


level = 1
active = []
for i in range(0,3+2*level):
	active.append(0)
complete = False
row = 8
color = ["red", "blue", "yellow", "green", "purple", "brown", "orange", "pink", "black"]
secs = 0
paused = False
score = 0
dummy = 0
lost = 0

highscore = [0,0,0,0,0,0,0,0,0,0]

try:
	d = open("highscores")
	zeilen = d.readlines()
	for z in zeilen:
		highscore[z] = int(z)
	d.close()
except:
	pass

app = kdeui.KApplication()
mastermind = MMind()
mastermind.show()
sys.exit(app.exec_())