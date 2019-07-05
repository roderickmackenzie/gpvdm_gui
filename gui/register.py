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
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QLineEdit,QComboBox,QHBoxLayout,QPushButton,QLabel,QDialog,QVBoxLayout,QSizePolicy
from PyQt5.QtGui import QPainter,QIcon,QImage
from PyQt5.QtGui import QFont

from icon_lib import icon_get

from PyQt5.QtCore import QSize, Qt

from inp import inp_load_file
import re

from error_dlg import error_dlg
from lock import lock
from code_ctrl import am_i_rod

def isValidEmail(email):
	if len(email) > 7:
		if email.count("@")==1:
			return True
	return False

from lock import get_lock

class register(QDialog):

	def callback_register(self):

		if isValidEmail(self.email0.text()) == False :
			error_dlg(self,_("This is not a valide e-mail address"))
			return

		if self.email0.text()!=self.email1.text():
			error_dlg(self,_("The e-mail addresses do not match."))
			return

		if self.name.text()=="":
			error_dlg(self,_("Please enter your name."))
			return

		if self.company.text()=="":
			error_dlg(self,_("Please enter your Company/University."))
			return

		ret=get_lock().register(email=self.email0.text(),name=self.name.text(),company=self.company.text())
		if ret==False:
			if get_lock().error=="no_internet":
				error_dlg(self,_("I can't access the internet, or gpvdm.com is down."))
			
			if get_lock().error=="too_old":
				error_dlg(self,_("Your version of gpvdm is too old to register, please download the latest version."))

			return
		get_lock().get_license()

		self.accept()

	def __init__(self):
		QWidget.__init__(self)
		self.setWindowIcon(icon_get("icon"))
		self.setWindowTitle(_("Registration window (www.gpvdm.com)")) 
		self.setWindowFlags(Qt.WindowStaysOnTopHint)

		vbox=QVBoxLayout()

		l=QLabel(_("Please register to use gpvdm. Thanks!"))
		l.setFont(QFont('SansSerif', 25))
		vbox.addWidget(l)

		hbox_widget=QWidget()
		hbox=QHBoxLayout()
		hbox_widget.setLayout(hbox)
		l=QLabel("<b>"+_("Name")+"</b>:")
		l.setFont(QFont('SansSerif', 14))
		hbox.addWidget(l)
		self.name = QLineEdit()
		hbox.addWidget(self.name)
		vbox.addWidget(hbox_widget)


		hbox_widget=QWidget()
		hbox=QHBoxLayout()
		hbox_widget.setLayout(hbox)
		l=QLabel("<b>"+_("Company/University")+"</b>:")
		l.setFont(QFont('SansSerif', 14))
		hbox.addWidget(l)
		self.company = QLineEdit()
		hbox.addWidget(self.company)
		vbox.addWidget(hbox_widget)

		hbox_widget=QWidget()
		hbox=QHBoxLayout()
		hbox_widget.setLayout(hbox)
		l=QLabel("<b>"+_("E-mail")+"</b>:")
		l.setFont(QFont('SansSerif', 14))
		hbox.addWidget(l)
		self.email0 = QLineEdit()
		hbox.addWidget(self.email0)
		vbox.addWidget(hbox_widget)

		hbox_widget=QWidget()
		hbox=QHBoxLayout()
		hbox_widget.setLayout(hbox)
		l=QLabel("<b>"+_("Confirm e-mail")+"</b>:")
		l.setFont(QFont('SansSerif', 14))
		hbox.addWidget(l)
		self.email1 = QLineEdit()
		hbox.addWidget(self.email1)
		vbox.addWidget(hbox_widget)

		button_box=QHBoxLayout()

		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		button_box.addWidget(spacer)

		self.register=QPushButton("Register", self)
		self.register.clicked.connect(self.callback_register)
		button_box.addWidget(self.register)

		button_box_widget=QWidget()
		button_box_widget.setLayout(button_box)
		vbox.addWidget(button_box_widget)

		self.setLayout(vbox)

		self.setMinimumWidth(400)


		if am_i_rod()==True:
			self.email0.setText("r.c.i.mackenzie@googlemail.com")
			self.email1.setText("r.c.i.mackenzie@googlemail.com")
			self.company.setText("The University of Nottingham")

			self.name.setText("波长-反射光")
		
		
	def run(self):
		return self.exec_()


