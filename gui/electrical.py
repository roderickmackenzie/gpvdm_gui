# 
#   General-purpose Photovoltaic Device Model - a drift diffusion base/Shockley-Read-Hall
#   model for 1st, 2nd and 3rd generation solar cells.
#   Copyright (C) 2012-2017 Roderick C. I. MacKenzie r.c.i.mackenzie at googlemail.com
#
#   https://www.gpvdm.com
#   Room B86 Coates, University Park, Nottingham, NG7 2RD, UK
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License v2.0, as published by
#   the Free Software Foundation.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# 

## @package electrical
#  The main window to electrical properties of the device.
#

import os
from icon_lib import icon_get

#qt
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget

#python modules
import webbrowser

#windows
from tab import tab_class

from PyQt5.QtCore import pyqtSignal

from QWidgetSavePos import QWidgetSavePos

from pl_main import pl_main

from help import help_window

from code_ctrl import enable_betafeatures

from dos_main import dos_main

from contacts_boundary import contacts_boundary


articles = []
mesh_articles = []

class electrical(QWidgetSavePos):

	changed = pyqtSignal()


	def changed_click(self):

		if self.notebook.tabText(self.notebook.currentIndex()).strip()==_("Device"):
			help_window().help_set_help(["tab.png",_("<big><b>Device tab</b></big><br>This tab contains information about the device,carrier density on the contacts.")])

		if self.notebook.tabText(self.notebook.currentIndex()).strip()==_("Complex DoS"):
			help_window().help_set_help(["tab.png",_("<big><b>The Complex DoS tab</b></big><br> Use this tab to edit the energetic distribution of the density of states. <b>If you want to use this feature contact me.</b>")])

		if self.notebook.tabText(self.notebook.currentIndex()).strip()==_("Luminescence"):
			help_window().help_set_help(["tab.png",_("<big><b>Luminescence</b></big>\nIf you set 'Turn on luminescence' to true, the simulation will assume recombination is a raditave process and intergrate it to produce Voltage-Light intensity curves (lv.dat).  Each number in the tab tells the model how efficient each recombination mechanism is at producing photons.")])
		

	def __init__(self):
		QWidgetSavePos.__init__(self,"electrical")
		self.setFixedSize(1000, 600)
		self.setWindowIcon(icon_get("preferences-system"))

		self.setWindowTitle(_("Electrical parameter editor")+" (https://www.gpvdm.com)") 
		

		self.main_vbox = QVBoxLayout()

		toolbar=QToolBar()
		toolbar.setIconSize(QSize(48, 48))

		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

		toolbar.addWidget(spacer)


		self.undo = QAction(icon_get("help"), _("Help"), self)
		self.undo.setStatusTip(_("Help"))
		self.undo.triggered.connect(self.callback_help)
		toolbar.addAction(self.undo)

		self.main_vbox.addWidget(toolbar)

		self.notebook = QTabWidget()

		self.notebook.setMovable(True)

		self.main_vbox.addWidget(self.notebook)

		widget=dos_main()
		widget.update()
		self.notebook.addTab(widget,_("Electrical parameters"))

		if enable_betafeatures()==True:
			widget=tab_bands()
			widget.update()
			self.notebook.addTab(widget,_("Complex DoS"))
		
		widget=pl_main()
		widget.update()
		self.notebook.addTab(widget,_("Luminescence"))



						
		self.setLayout(self.main_vbox)

		#self.connect("delete-event", self.callback_close_window) 
		self.notebook.currentChanged.connect(self.changed_click)
		#self.hide()

	def callback_help(self,widget):
		webbrowser.open('http://www.gpvdm.com/man/index.html')

	def update(self):
		for i in range(0,self.count()):
			w=self.widget(i)
			w.update()


