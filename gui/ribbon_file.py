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

## @package ribbon_file
#  A ribbon for the file menu
#


import os
from icon_lib import icon_get

from dump_io import dump_io
from tb_item_sim_mode import tb_item_sim_mode
from tb_item_sun import tb_item_sun

from code_ctrl import enable_betafeatures
from cal_path import get_css_path

#qt
from PyQt5.QtWidgets import  QAction, QMenu
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget,QSizePolicy,QVBoxLayout,QHBoxLayout,QToolBar, QToolButton
from PyQt5.QtWidgets import QTabWidget

import webbrowser
from lock import get_lock
from QAction_lock import QAction_lock
from used_files import used_files_load
from PyQt5.QtCore import pyqtSignal

class ribbon_file(QToolBar):
	used_files_click= pyqtSignal(str)
	def __init__(self):
		QToolBar.__init__(self)

		self.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		self.setIconSize(QSize(42, 42))
		
		self.home_new = QAction_lock("document-new", _("New simulation").replace(" ","\n"), self,"main_new")
		#self.home_new.setText(_("New\nsimulation"))
		self.addAction(self.home_new)

		self.old = QAction(icon_get("document-new"), _("New simulation").replace(" ","\n"), self)


		self.home_open = QAction_lock("document-open", _("Open\nsimulation"), self,"main_open")

		self.used_files_menu = QMenu(self)
		self.populate_used_file_menu()
		self.home_open.setMenu(self.used_files_menu)


		self.addAction(self.home_open)

		self.home_export = QAction_lock("document-export", _("Export\ndata"), self,"main_export")
		#self.addAction(self.home_export)

		self.home_export_xls = QAction_lock("export_xls", _("Export\nto Excel"), self,"main_export_xls")
		#self.home_export_xls = QAction(icon_get("export_xls"), _("Export\nto Excel"), self)
		self.addAction(self.home_export_xls)

		self.home_export_xls.clicked.connect(self.callback_export_xls)


		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.addWidget(spacer)

		if get_lock().is_trial()==True and get_lock().is_registered()==True:
			self.home_cart = QAction(icon_get("upgrade"), _("Upgrade to\ngpvdm professional."), self)
			self.home_cart.triggered.connect(self.callback_buy)
			self.addAction(self.home_cart)

		self.home_help = QAction(icon_get("internet-web-browser"), _("Help"), self)
		self.addAction(self.home_help)

	def populate_used_file_menu(self):
		self.used_files_menu.clear()
		files=used_files_load()
		for f in files:
			f=QAction(f, self)
			f.triggered.connect(self.callback_menu)
			self.used_files_menu.addAction(f)

	def callback_menu(self):
		action = self.sender()
		self.used_files_click.emit(action.text())

	def callback_buy(self):
		webbrowser.open("https://www.gpvdm.com/buy.html")

	def update(self):
		self.populate_used_file_menu()

	def callback_export_xls(self):
		from dlg_export import dlg_export_xls
		dlg_export_xls(self)

	def setEnabled(self,val,do_all=False):
		self.home_new.setEnabled(val)
		self.home_open.setEnabled(val)
		self.home_export.setEnabled(val)
		self.home_export_xls.setEnabled(val)


	def setEnabled_other(self,val):
		self.home_export.setEnabled(val)
		self.home_export_xls.setEnabled(val)
