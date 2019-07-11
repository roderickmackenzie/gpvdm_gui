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

## @package emission_main
#  Dialog to show information about a material.
#

import os
from tab import tab_class
from icon_lib import icon_get

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QDialog
from PyQt5.QtGui import QPainter,QIcon

#python modules
import webbrowser

from help import help_window

from win_lin import desktop_open

from ref import ref_window
from ref import get_ref_text
from ref_io import ref

from gpvdm_open import gpvdm_open


from QWidgetSavePos import QWidgetSavePos
from plot_widget import plot_widget

from ribbon_emission_db import ribbon_emission_db
from import_data import import_data
from equation_editor import equation_editor

articles = []
mesh_articles = []

class emission_main(QWidgetSavePos):

	def changed_click(self):
		if self.notebook.tabText(self.notebook.currentIndex()).strip()==_("Emission"):
			help_window().help_set_help(["tab.png",_("<big><b>Emission spectrum</b></big><br>Use this tab to edit the emission spectrum.")])
			self.ribbon.tb_save.setEnabled(True)
			self.ribbon.import_data.setEnabled(True)

	def callback_help(self):
		webbrowser.open("https://www.gpvdm.com/man/index.html")


	def __init__(self,path):
		QWidgetSavePos.__init__(self,"emission_main")
		self.path=path
		self.setFixedSize(900, 600)
		self.setWindowIcon(icon_get("emission"))

		self.setWindowTitle(_("Emission editor")+" (https://www.gpvdm.com)"+" "+os.path.basename(self.path)) 
		

		self.main_vbox = QVBoxLayout()

		self.ribbon=ribbon_emission_db()
		
		self.ribbon.import_data.secure_click.connect(self.import_data)
		self.ribbon.equation.secure_click.connect(self.callback_equation_editor)

		self.ribbon.tb_ref.triggered.connect(self.callback_ref)

		self.ribbon.help.triggered.connect(self.callback_help)


		self.main_vbox.addWidget(self.ribbon)

		self.notebook = QTabWidget()

		self.notebook.setMovable(True)

		self.main_vbox.addWidget(self.notebook)

		fname=os.path.join(self.path,"spectra.inp")
		self.emission=plot_widget()
		self.emission.init(enable_toolbar=False)
		self.emission.set_labels([_("Emission")])
		self.emission.load_data([fname])

		self.emission.do_plot()
		self.notebook.addTab(self.emission,_("Emission"))


		files=["mat.inp"]
		description=[_("Basic")]


		for i in range(0,len(files)):
			tab=tab_class()
			full_path=os.path.join(self.path,files[i])
			if os.path.isfile(full_path)==True:
				tab.init(os.path.join(self.path,files[i]),description[i])
				self.notebook.addTab(tab,description[i])
		self.setLayout(self.main_vbox)
		
		self.notebook.currentChanged.connect(self.changed_click)

	def callback_equation_editor(self):

		file_name="spectra.inp"
		equation_file="spectra_eq.inp"
		data_label="Emission"
		data_units="au"


		output_file=os.path.join(self.path,file_name)
		config_file=os.path.join(self.path,file_name+"import.inp")

		self.equation_editor=equation_editor(self.path,equation_file,file_name)
		self.equation_editor.data_written.connect(self.update)

		self.equation_editor.data.y_label="Wavelength"
		self.equation_editor.data.data_label=data_label

		self.equation_editor.data.y_units="nm"
		self.equation_editor.data.data_units=data_units
		self.equation_editor.load()

		self.equation_editor.show()

	def import_data(self):
		file_name="spectra.inp"

		output_file=os.path.join(self.path,file_name)
		config_file=os.path.join(self.path,file_name+"import.inp")
		self.im=import_data(output_file,config_file)
		self.im.run()
		self.update()

	def import_ref(self):
		file_name="spectra.inp"

		output_file=os.path.join(self.path,file_name)
		config_file=os.path.join(self.path,file_name+"import.inp")
		self.im=import_data(output_file,config_file)
		self.im.run()
		self.update()

	def update(self):
		self.emission.update()

	def callback_ref(self):
		file_name=None
		if self.notebook.tabText(self.notebook.currentIndex()).strip()==_("Emission"):
			file_name="spectra.gmat"

		if file_name!=None:
			self.ref_window=ref_window(os.path.join(self.path,file_name))
			self.ref_window.show()
