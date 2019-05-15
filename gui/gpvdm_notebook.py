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

## @package gpvdm_notebook
#  The main gpvdm notebook for the main window.
#


import os

#inp files
from inp import inp_load_file
from inp import inp_get_next_token_array
from inp import inp_isfile
from inp import inp_update_token_value

#tabs
from tab_main import tab_main
from tab import tab_class

#util
from win_lin import running_on_linux

#paths
from cal_path import get_bin_path
from cal_path import get_exe_args

from code_ctrl import enable_webbrowser
from cal_path import get_exe_command

#qt
from PyQt5.QtWidgets import QTabWidget,QWidget

#window
from tab_terminal import tab_terminal

if enable_webbrowser()==True:
	from information_webkit import information
else:
	from information_noweb import information

from help import help_window

import i18n
_ = i18n.language.gettext

from global_objects import global_object_register
from cal_path import get_sim_path

from tab_view import tab_view

from css import css_apply

class gpvdm_notebook(QTabWidget):
	item_factory=None

		
	def __init__(self):
		QWidget.__init__(self)
		css_apply(self,"tab_default.css")
		self.terminal=None
		self.update_display_function=None
		self.currentChanged.connect(self.changed_click)
		global_object_register("notebook_goto_page",self.goto_page)
		self.state_loaded=False

	def update(self):
		for i in range(0,self.count()):
			w=self.widget(i)
			w.update()

	def changed_click(self):

		if self.tabText(self.currentIndex()).strip()==_("Device structure"):
			help_window().help_set_help(["device.png",_("<big><b>The device structure tab</b></big><br> Use this tab to change the structure of the device, the layer thicknesses and to perform optical simulations.  You can also browse the materials data base and  edit the electrical mesh.")])

		if self.tabText(self.currentIndex()).strip()==_("Electrical parameters"):
			help_window().help_set_help(["tab.png",_("<big><b>The electrical parameters</b></big>\nThis tab contains the electrical model parameters, such as mobility, tail slope energy, and band gap.")])

		if self.tabText(self.currentIndex()).strip()==_("Terminal"):
			help_window().help_set_help(["utilities-terminal.png",_("<big><b>The terminal window</b></big>\nThe output of the model will be displayed in this window, watch this screen for debugging and convergence information.")])

		if self.tabText(self.currentIndex()).strip()==_("Information"):
			help_window().help_set_help(["help.png",_("<big><b>On-line help</b></big>\nYou can view the on-line help and manual here.")])
		
	def get_current_page(self):
		i=self.currentIndex()
		return self.tabText(i)


	def goto_page(self,page):
		self.blockSignals(True)
		for i in range(0,self.count()):
				if self.tabText(i)==page:
					self.setCurrentIndex(i)
					break
		self.blockSignals(False)

	def add_info_page(self):
		browser=information()
		self.addTab(browser,_("Information"))

	def load(self):
		self.clear()
		self.last_page=0

		#self.setTabsClosable(True)
		self.setMovable(True)
		if (os.path.isfile(os.path.join(get_sim_path(),"sim.gpvdm"))==True):

			widget=tab_main()
			self.addTab(widget,_("Device structure"))

			self.update_display_function=widget.update


			self.terminal=tab_terminal()
			self.terminal.init()
			self.addTab(self.terminal,_("Terminal"))
			self.terminal.run(os.getcwd(),get_exe_command()+" --version "+get_exe_args())
			global_object_register("terminal",self.terminal)

			widget=tab_view()
			self.addTab(widget,_("Output"))

			self.state_loaded=True

		else:
			self.add_info_page()
			self.goto_page(_("Information"))
			self.state_loaded=False
			
	def is_loaded(self):
		return self.state_loaded

	def setEnabled(self,val):
		for i in range(0,self.count()):
			w=self.widget(i)
			w.setEnabled(val)


