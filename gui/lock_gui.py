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

## @package register
#  Registration window
#


import os

#qt
from PyQt5.QtCore import Qt 
from PyQt5.QtWidgets import QWidget,QDialog

from inp import inp_load_file

from error_dlg import error_dlg
from lock import lock
from code_ctrl import am_i_rod
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal
from register import register

from lock import get_lock
from trial import trial
from msg_dlg import msg_dlg

from code_ctrl import am_i_rod
from cal_path import get_image_file_path

class lock_gui(QWidget):
	#disable_all=pyqtSignal()
	#enable_all=pyqtSignal()


	def bing(self):
		self.timer.stop()
		if get_lock().get_next_gui_action()=="register":
			#self.disable_all.emit()
			self.register=register()
			ret=self.register.run()
			if ret==QDialog.Accepted:
				get_lock().debug_tx_info()
				image_file=""
				text="Thank you for registering gpvdm."

				msgBox = msg_dlg()

				msgBox.setText(text)


				msgBox.exec_()
				#self.enable_all.emit()
			else:
				return
		
		if get_lock().status=="expired":
			self.trial=trial(override_text="<br><br>Please renew your gpvdm license it has expired.<br>")
			ret=self.trial.run()
			if ret==QDialog.Accepted:
				msgBox = msg_dlg()
				msgBox.setText("Thank you for buying gpvdm")
				reply = msgBox.exec_()
		#if get_lock().is_disabled()==True:
		#	self.disable_all.emit()

		get_lock().debug_tx_info()

		
		if get_lock().get_next_gui_action()=="no_internet":
			msgBox = msg_dlg()
			msgBox.setText("I can not connect to the update server.  Gpvdm may not be able to run.  Please connect to the internet.")
			reply = msgBox.exec_()
			return



	def __init__(self):
		QWidget.__init__(self)
		self.timer=QTimer()
		self.timer.timeout.connect(self.bing)

	def run(self):
		#if am_i_rod()==False:
		#	self.timer.start(10000)
		#else:
		self.timer.start(1000)


