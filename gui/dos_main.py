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

## @package dos_main
#  The main DoS dialog.
#

import os
from tab_base import tab_base
from tab import tab_class
from epitaxy import epitaxy_get_layers
from epitaxy import epitaxy_get_dos_file
from epitaxy import epitaxy_get_electrical_file
from global_objects import global_object_register
from epitaxy import epitaxy_get_name

#qt5
from PyQt5.QtWidgets import  QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QSizePolicy,QVBoxLayout,QPushButton,QDialog,QFileDialog,QToolBar,QTabWidget

#windows
from QHTabBar import QHTabBar
from global_objects import global_object_register
from icon_lib import icon_get

from css import css_apply

from inp import inp_get_token_value
from cal_path import get_sim_path

class dos_main(QWidget,tab_base):

	def __init__(self):
		QWidget.__init__(self)
		self.setMinimumSize(1000, 600)

		self.main_vbox = QVBoxLayout()

		self.setWindowIcon(icon_get("preferences-system"))

		self.setWindowTitle(_("Electrical parameter editor")+" (https://www.gpvdm.com)") 

		toolbar=QToolBar()
		toolbar.setIconSize(QSize(48, 48))

		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

		toolbar.addWidget(spacer)


		self.help = QAction(icon_get("help"), _("Help"), self)
		self.help.setStatusTip(_("Help"))
		self.help.triggered.connect(self.callback_help)
		toolbar.addAction(self.help)

		self.main_vbox.addWidget(toolbar)

		self.notebook = QTabWidget()

		css_apply(self,"tab_default.css")


		self.main_vbox.addWidget(self.notebook)
		self.setLayout(self.main_vbox)

		#self.notebook.setTabsClosable(True)
		#self.notebook.setMovable(True)
		#self.notebook.setTabBar(QHTabBar())
		#self.notebook.setTabPosition(QTabWidget.West)

		global_object_register("dos_update",self.update)
		self.update()

	def update(self):
		self.notebook.clear()
		fulle_sim=True
		sim_type=inp_get_token_value(os.path.join(get_sim_path(),"math.inp"), "#newton_name")
		if sim_type=="newton_simple":
			fulle_sim=False

		for i in range(0,epitaxy_get_layers()):
			dos_file=epitaxy_get_dos_file(i)

			if dos_file.startswith("dos")==True:
				if fulle_sim==True:
					name="DoS of "+epitaxy_get_name(i)

					widget=tab_class()
					widget.init(dos_file+".inp",name)

					self.notebook.addTab(widget,name)
				else:
					electrical_file=epitaxy_get_electrical_file(i)
					name="Electrical "+epitaxy_get_name(i)

					widget=tab_class()
					widget.init(electrical_file+".inp",name)

					self.notebook.addTab(widget,name)

	def help(self):
		help_window().help_set_help(["tab.png","<big><b>Density of States</b></big>\nThis tab contains the electrical model parameters, such as mobility, tail slope energy, and band gap."])

	def callback_help(self,widget):
		webbrowser.open('http://www.gpvdm.com/man/index.html')


