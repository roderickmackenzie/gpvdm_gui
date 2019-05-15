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

## @package spectra_main
#  An editro for optical spectra.
#

import os
from tab import tab_class
from icon_lib import icon_get

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget
from PyQt5.QtGui import QPainter,QIcon

#python modules
import webbrowser

from help import help_window

from equation import equation
from win_lin import desktop_open

from ref import get_ref_text
from QWidgetSavePos import QWidgetSavePos

from ribbon_spectra import ribbon_spectra

articles = []
mesh_articles = []

class spectra_main(QWidgetSavePos):

	def changed_click(self):

		if self.notebook.tabText(self.notebook.currentIndex()).strip()==_("Refractive index"):
			text=get_ref_text(os.path.join(self.path,"n.ref"))
			if text==None:
				text=""
			help_window().help_set_help(["n.png",_("<big><b>Refractive index</b></big><br>"+text)])

	def callback_help(self):
		webbrowser.open("https://www.gpvdm.com/man/index.html")

	def __init__(self,path):
		QWidgetSavePos.__init__(self,"spectra_main")
		self.path=path
		self.setMinimumSize(900, 600)
		self.setWindowIcon(icon_get("spectra_file"))

		self.setWindowTitle(_("Optical spectrum editor")+" (https://www.gpvdm.com)"+" "+os.path.basename(self.path)) 
		

		self.main_vbox = QVBoxLayout()

		self.ribbon=ribbon_spectra()
		
		#self.ribbon.cost.triggered.connect(self.callback_cost)
		#self.ribbon.folder_open.triggered.connect(self.callback_dir_open)
		#self.ribbon.import_data.triggered.connect(self.import_data)
		#self.ribbon.tb_ref.triggered.connect(self.callback_ref)

		#self.ribbon.help.triggered.connect(self.callback_help)


		self.main_vbox.addWidget(self.ribbon)

		self.notebook = QTabWidget()

		self.notebook.setMovable(True)

		self.main_vbox.addWidget(self.notebook)


		files=["mat.inp"]
		description=[_("Parameters")]

		eq=equation(self.path,"spectra_eq.inp","spectra_gen.inp","spectra.inp","#spectra_equation_or_data",toolbar=self.ribbon.main_toolbar)
		eq.show_solar_spectra=True
		eq.set_default_value("3")
		eq.set_ylabel(_("Intensity")+" (au)")
		eq.init()
		self.notebook.addTab(eq,_("Intensity"))

		for i in range(0,len(files)):
			tab=tab_class()
			tab.init(os.path.join(self.path,files[i]),description[i])
			self.notebook.addTab(tab,description[i])


		self.setLayout(self.main_vbox)
		
		self.notebook.currentChanged.connect(self.changed_click)



