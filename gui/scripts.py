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
from inp import inp_save_lines_to_file

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
from gui_util import dlg_get_text

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
		self.ribbon.tb_new.clicked.connect(self.callback_add_page)
		#self.ribbon.tb_rename.clicked.connect(self.callback_rename_page)

		self.ribbon.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		self.main_vbox.addWidget(self.ribbon)



		self.notebook = QTabWidget()
		css_apply(self.notebook,"tab_default.css")
		self.notebook.setMovable(True)

		added=0
		for f in inp_lsdir("sim.gpvdm"):
			if f.endswith(".py"):
				file_name=os.path.join(get_sim_path(),f)
				a=script_editor()
				a.load(file_name)
				self.notebook.addTab(a,f)
				added=added+1
		if added==0:
			file_name=os.path.join(get_sim_path(),"example.py")
			self.new_script(file_name)
			a=script_editor()
			a.load(file_name)
			self.notebook.addTab(a,"example.py")

		self.notebook.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.main_vbox.addWidget(self.notebook)


		self.setLayout(self.main_vbox)

	def new_script(self,file_name):
		data=[]
		data.append("#!/usr/bin/env python3")
		data.append("# -*- coding: utf-8 -*-")
		data.append("import os")
		data.append("import sys")
		data.append("")
		data.append("from gpvdm_api import gpvdm_api")
		data.append("")
		data.append("def run():")
		data.append("	a=gpvdm_api(verbose=True)")
		data.append("	a.set_save_dir(device_data)")
		data.append("	a.edit(\"light.inp\",\"#light_model\",\"qe\")")
		data.append("	a.edit(\"jv0.inp\",\"#Vstop\",\"0.8\")")
		data.append("	a.run()")

		inp_save_lines_to_file(file_name,data)

	def callback_add_page(self):
		new_sim_name=dlg_get_text( "Add a new script:", "exampe.py","document-new.png")
		if new_sim_name.ret!=None:
			name=os.path.join(get_sim_path(),new_sim_name.ret)
			self.new_script(name)
			a=script_editor()
			a.load(name)
			self.notebook.addTab(a,os.path.basename(name))

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

