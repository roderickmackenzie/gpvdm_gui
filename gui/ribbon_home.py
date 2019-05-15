# -*- coding: utf-8 -*-
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

## @package ribbon_home
#  The home ribbon.
#


import os

from dump_io import dump_io
from tb_item_sim_mode import tb_item_sim_mode
from tb_item_sun import tb_item_sun

from cal_path import get_css_path

#qt
from PyQt5.QtWidgets import QTextEdit, QAction
from PyQt5.QtCore import QSize, Qt,QFile,QIODevice
from PyQt5.QtWidgets import QWidget,QSizePolicy,QVBoxLayout,QHBoxLayout,QToolBar, QToolButton,QDialog

from plot_gen import plot_gen
from info import sim_info
from win_lin import desktop_open

#windows
from scan import scan_class 
from help import help_window
from gpvdm_open import gpvdm_open
from error_dlg import error_dlg
from server import server_get
from fit_window import fit_window

from global_objects import global_object_run
from util import isfiletype
from icon_lib import icon_get

from cal_path import get_sim_path
from inp import inp_isfile
from play import play
from util import wrap_text

import webbrowser

class ribbon_home(QToolBar):

	def callback_buy(self):
		webbrowser.open("https://www.gpvdm.com/buy.html")

	def __init__(self):
		QToolBar.__init__(self)
		self.myserver=server_get()

		self.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		self.setIconSize(QSize(42, 42))
		
		self.scan_window=None
		self.fit_window=None

		self.undo = QAction(icon_get("edit-undo"), _("Undo"), self)
		self.addAction(self.undo)

		self.addSeparator()

		self.run = play(self,run_text=wrap_text(_("Run\nsimulation"),2))#QAction(icon_get("media-playback-start"), _("Run simulation"), self)
		server_get().sim_finished.connect(self.run.stop)
		server_get().sim_started.connect(self.run.start)

		self.addAction(self.run)

		#self.stop = QAction(icon_get("media-playback-pause"), _("Stop\nsimulation"), self)
		#self.stop.triggered.connect(self.callback_simulate_stop)
		#self.addAction(self.stop)

		self.addSeparator()
		
		self.scan = QAction(icon_get("scan"), _("Parameter\nscan"), self)
		self.scan.triggered.connect(self.callback_scan)
		self.addAction(self.scan)


		self.addSeparator()

		self.fit = QAction(icon_get("fit"), _("Fit\ndata"), self)
		self.fit.triggered.connect(self.callback_run_fit)
		self.addAction(self.fit)

		self.addSeparator()
		
		self.plot = QAction(icon_get("plot"), _("Plot\nFile"), self)
		self.plot.triggered.connect(self.callback_plot_select)
		self.addAction(self.plot)

		self.addSeparator()

		self.sun=tb_item_sun()
		#self.sun.changed.connect(self.callback_sun)
		self.addWidget(self.sun)

		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.addWidget(spacer)


		self.help = QAction(icon_get("internet-web-browser"), _("Help"), self)
		self.addAction(self.help)



	#def callback_sun(self):
	#	global_object_run("gl_force_redraw")
		
	def update(self):
		if self.scan_window!=None:
			del self.scan_window
			self.scan_window=None

		if self.fit_window!=None:
			del self.fit_window
			self.fit_window=None
		self.sun.update()
		
		if inp_isfile(os.path.join(get_sim_path(),"fit.inp"))==True:
			self.fit.setVisible(True)
		else:
			self.fit.setVisible(False)

	def setEnabled(self,val):
		self.undo.setEnabled(val)
		self.run.setEnabled(val)
		#self.stop.setEnabled(val)
		self.scan.setEnabled(val)
		self.plot.setEnabled(val)
		self.sun.setEnabled(val)
		self.help.setEnabled(val)
		if inp_isfile(os.path.join(get_sim_path(),"fit.inp"))==True:
			self.fit.setEnabled(val)

	def callback_plot_select(self):
		help_window().help_set_help(["dat_file.png",_("<big>Select a file to plot</big><br>Single clicking shows you the content of the file")])

		dialog=gpvdm_open(get_sim_path(),show_inp_files=False)
		dialog.show_directories=False
		ret=dialog.exec_()
		if ret==QDialog.Accepted:
			file_name=dialog.get_filename()
			
			if os.path.basename(dialog.get_filename())=="sim_info.dat":
				self.sim_info_window=sim_info(dialog.get_filename())
				self.sim_info_window.show()
				return

			plot_gen([dialog.get_filename()],[],"auto")

			#self.plotted_graphs.refresh()
			#self.plot_after_run_file=dialog.get_filename()

	def callback_scan(self, widget):
		help_window().help_set_help(["scan.png",_("<big><b>The scan window</b></big><br> Very often it is useful to be able to systematically very a device parameter such as mobility or density of trap states.  This window allows you to do just that."),"list-add.png",_("Use the plus icon to add a new scan line to the list.")])
		#self.tb_run_scan.setEnabled(True)

		if self.scan_window==None:
			self.scan_window=scan_class(server_get())


		if self.scan_window.isVisible()==True:
			self.scan_window.hide()
		else:
			self.scan_window.show()
		
	def callback_simulate_stop(self):
		server_get().killall()

	def callback_run_fit(self, widget):
		if self.fit_window==None:
			self.fit_window=fit_window("fit")
			server_get().set_fit_update_function(self.fit_window.update)

		help_window().help_set_help(["fit.png",_("<big><b>Fit window</b></big><br> Use this window to fit the simulation to experimental data.")])
		if self.fit_window.isVisible()==True:
			self.fit_window.hide()
		else:
			self.fit_window.show()
