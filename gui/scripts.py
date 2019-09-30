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

## @package scripts
#  The main script editor
#


import os
from inp import inp_update_token_value
from inp import inp_get_token_value
from plot_gen import plot_gen
from icon_lib import icon_get
import zipfile
import glob
from scan_item import scan_item_add
from tab import tab_class
import webbrowser
from progress_class import progress_class
from help import my_help_class

#path
from cal_path import get_materials_path
from cal_path import get_exe_command

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QHBoxLayout,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QSystemTrayIcon,QMenu, QComboBox, QMenuBar, QLabel
from PyQt5.QtGui import QIcon

#windows
from band_graph import band_graph
from plot_widget import plot_widget
from error_dlg import error_dlg

from server import server_get

from global_objects import global_object_run
from global_objects import global_object_delete
from cal_path import get_sim_path
from QWidgetSavePos import QWidgetSavePos

from script_ribbon import script_ribbon

from css import css_apply
from gui_util import yes_no_dlg
from script_editor import script_editor
from inp import inp_lsdir

class scripts(QWidgetSavePos):

	def __init__(self):
		QWidgetSavePos.__init__(self,"optics")

		self.setWindowIcon(icon_get("optics"))

		self.setMinimumSize(1000, 600)
		self.setWindowTitle(_("Script editor")+" (https://www.gpvdm.com)")    

		self.ribbon=script_ribbon()


		self.setWindowIcon(icon_get("script"))

		self.main_vbox=QVBoxLayout()

		self.ribbon.run.start_sim.connect(self.callback_run)

		self.ribbon.help.triggered.connect(self.callback_help)

		self.ribbon.tb_save.clicked.connect(self.callback_save)

		self.ribbon.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		self.main_vbox.addWidget(self.ribbon)



		self.notebook = QTabWidget()
		css_apply(self.notebook,"tab_default.css")
		self.notebook.setMovable(True)


		for f in inp_lsdir("sim.gpvdm"):
			if f.endswith(".py"):
				a=script_editor()
				a.load(f)
				self.notebook.addTab(a,f)


		self.notebook.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.main_vbox.addWidget(self.notebook)


		self.setLayout(self.main_vbox)


	def closeEvent(self, event):
		global_object_delete("optics_force_redraw")
		self.hide()
		event.accept()

	def callback_save(self):
		tab = self.notebook.currentWidget()
		tab.save()

	def optics_sim_finished(self):
		inp_update_token_value("dump.inp", "#dump_optics",self.dump_optics)
		inp_update_token_value("dump.inp", "#dump_optics_verbose",self.dump_optics_verbose)
		self.force_redraw()

	def force_redraw(self):

		self.fig_gen_rate.draw_graph()

		for i in range(0,len(self.plot_widgets)):
			self.plot_widgets[i].update()
			
		self.ribbon.update()
		
	def callback_run(self):
		tab = self.notebook.currentWidget()
		tab.run()


	def callback_help(self, widget, data=None):
		webbrowser.open('https://www.gpvdm.com/man/index.html')

