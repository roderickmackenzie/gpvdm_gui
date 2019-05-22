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

## @package play
#  A play button
#

import os

#qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QSizePolicy,QHBoxLayout,QPushButton,QDialog,QFileDialog,QToolBar,QMessageBox, QLineEdit

from icon_lib import icon_get
from util import str2bool
from help import help_window
from inp import inp_update_token_value
from inp import inp_get_token_value

from cal_path import get_sim_path
from util import wrap_text

from server import server_get
from lock import get_lock
from lock_gui import lock_gui


dump_fast=0
dump_slow=1
dump_custom=2

class play(QAction):

	start_sim = pyqtSignal()
	stop_sim = pyqtSignal()

	def start(self):
		self.setIcon(icon_get("media-playback-pause"))
		self.setText(_("Stop\nsimulation"))
		self.running=True

	def stop(self):
		self.setIcon(icon_get(self.play_icon))
		self.setText(self.run_text)
		self.running=False

	def do_emit(self):
		value=False
		if value==True:
			if self.running==False:
				self.start_sim.emit()
			else:
				server_get().killall()

	def __init__(self,parent,play_icon="media-playback-start",run_text=_("Run simulation")):
		self.play_icon=play_icon
		self.run_text=run_text
		self.running=False
		QAction.__init__(self,icon_get(self.play_icon),self.run_text,parent)
		self.triggered.connect(self.do_emit)
		server_get().sim_started.connect(self.start)
		server_get().sim_finished.connect(self.stop)


