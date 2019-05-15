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

## @package ribbon
#  Main ribbon class for main window.
#


import os

from dump_io import dump_io
from tb_item_sim_mode import tb_item_sim_mode
from tb_item_sun import tb_item_sun

from code_ctrl import enable_betafeatures
from cal_path import get_css_path

#qt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt,QFile,QIODevice
from PyQt5.QtWidgets import QWidget,QSizePolicy,QVBoxLayout,QLabel,QHBoxLayout,QPushButton,QDialog,QFileDialog,QToolBar,QMessageBox, QLineEdit, QToolButton
from PyQt5.QtWidgets import QTabWidget

#from ribbon_device import ribbon_device
from ribbon_database import ribbon_database
from ribbon_simulations import ribbon_simulations
from ribbon_configure import ribbon_configure
from ribbon_information import ribbon_information
from ribbon_home import ribbon_home
from icon_lib import icon_get

from about import about_dlg

from ribbon_cluster import ribbon_cluster
from css import css_apply

from status_icon import status_icon_stop
from global_objects import global_object_get
from server import server_get

from connect_to_cluster import connect_to_cluster
from ribbon_base import ribbon_base
from error_dlg import error_dlg
from ribbon_file import ribbon_file
from PyQt5.QtCore import pyqtSignal
import webbrowser

class QLabel_click(QLabel):
	clicked=pyqtSignal()
	def __init(self, parent):
		QLabel.__init__(self, QMouseEvent)

	def mousePressEvent(self, ev):
		self.clicked.emit()

class ribbon(ribbon_base):


	def update(self):
		#self.device.update()
		self.database.update()
		self.simulations.update()
		self.configure.update()
		self.information.update()
		self.home.update()

	def callback_about_dialog(self):
		dlg=about_dlg()
		dlg.exec_()

	def callback_questions(self):
		webbrowser.open("https://www.gpvdm.com/questions.html")

	def __init__(self):
		ribbon_base.__init__(self)
		self.cluster_tab=None
		self.setMaximumHeight(140)

		#self.setStyleSheet("QWidget {	background-color:cyan; }")

		self.myserver=server_get()

		self.holder=QWidget()
		self.hbox=QHBoxLayout()
		self.holder.setLayout(self.hbox)
		self.toolbar=QToolBar()
		self.toolbar.setIconSize(QSize(32, 32))

		self.help_message=QLabel_click(_("Questions? Contact <a href=\"info@gpvdm.com\">info@gpvdm.com</a>"))
		self.help_message.clicked.connect(self.callback_questions)
		self.about = QToolButton(self)
		self.about.setText(_("About"))
		self.about.pressed.connect(self.callback_about_dialog)

		self.cluster_button = QAction(icon_get("not_connected"), _("Connect to cluster"), self)
		self.cluster_button.triggered.connect(self.callback_cluster_connect)
		self.toolbar.addAction(self.cluster_button)
		
		self.hbox.addWidget(self.help_message)
		self.hbox.addWidget(self.toolbar)
		self.hbox.addWidget(self.about)

		self.setCornerWidget(self.holder)

		self.file=ribbon_file()
		self.addTab(self.file,_("File"))
		
		self.home=ribbon_home()
		self.addTab(self.home,_("Home"))
		
		self.simulations=ribbon_simulations()
		self.addTab(self.simulations,_("Simulations"))
		
		self.configure=ribbon_configure()
		self.addTab(self.configure,_("Configure"))
		
		#self.device=ribbon_device()
		#self.addTab(self.device,_("Device"))
		
		self.database=ribbon_database()
		self.addTab(self.database,_("Databases"))

		if enable_betafeatures()==True:
			self.tb_cluster=ribbon_cluster()
			self.addTab(self.tb_cluster,_("Cluster"))

		self.information=ribbon_information()
		self.addTab(self.information,_("Information"))

		#self.setStyleSheet("QWidget {	background-color:cyan; }") 
		css_apply(self,"style.css")
			

	def callback_cluster_connect(self):
		dialog=connect_to_cluster()
		if dialog.exec_():
			self.cluster_tab=global_object_get("cluster_tab")
			global_object_get("notebook_goto_page")(_("Terminal"))
			if self.myserver.cluster==False:
				if self.myserver.connect()==False:
					error_dlg(self,_("Can not connect to cluster."))
			else:
				self.myserver.cluster_disconnect()
				print("Disconnected")

		print(self.myserver.cluster)

		self.tb_cluster.update()
		if self.myserver.cluster==True:
			self.cluster_button.setIcon(icon_get("connected"))
			status_icon_stop(True)
		else:
			status_icon_stop(False)
			self.cluster_button.setIcon(icon_get("not_connected"))

