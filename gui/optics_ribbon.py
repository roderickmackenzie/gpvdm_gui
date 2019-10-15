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

## @package optics_ribbon
#  The ribbon for the optics window
#


import os

from dump_io import dump_io

from code_ctrl import enable_betafeatures
from cal_path import get_css_path

#qt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt,QFile,QIODevice
from PyQt5.QtWidgets import QWidget,QSizePolicy,QVBoxLayout,QHBoxLayout,QPushButton,QDialog,QFileDialog,QToolBar,QMessageBox, QLineEdit, QToolButton
from PyQt5.QtWidgets import QTabWidget

from icon_lib import icon_get

from about import about_dlg

from mode_selector import mode_selector
from tb_spectrum import tb_spectrum

from util import wrap_text
from ribbon_base import ribbon_base
from play import play
from QAction_lock import QAction_lock
from inp import inp_get_token_value
from inp import inp_update_token_value
from cal_path import get_sim_path

class mode_button(QAction_lock):
	def __init__(self,image,text,s,name):
		QAction_lock.__init__(self,image,text,s,name)
		self.setCheckable(True)
		self.mode="full"

class ribbon_optical_models(QToolBar):
	def __init__(self):
		QToolBar.__init__(self)
		self.actions=[]
		self.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		self.setIconSize(QSize(42, 42))
		
		a=mode_button("transfer_matrix", _("Transfer\nmatrix"), self,"optics_ribbon_export_image")
		a.mode="full"
		a.clicked.connect(self.callback_click)
		self.actions.append(a)

		a=mode_button("exp_light", _("Exponential\nprofile"), self,"optics_ribbon_mode_exp")
		a.mode="exp"
		a.clicked.connect(self.callback_click)
		self.actions.append(a)

		a=mode_button("flat_light", _("Flat\nprofile"), self,"optics_ribbon_mode_flat")
		a.mode="flat"
		a.clicked.connect(self.callback_click)
		self.actions.append(a)

		a=mode_button("file_light", _("From\nfile"), self,"optics_ribbon_mode_from_file")
		a.mode="fromfile"
		a.clicked.connect(self.callback_click)
		self.actions.append(a)

		a=mode_button("qe_light", _("From QE\nspectra"), self,"optics_ribbon_mode_qe")
		a.mode="qe"
		a.clicked.connect(self.callback_click)
		self.actions.append(a)

		for a in self.actions:
			self.addAction(a)

		self.set_mode()

	def set_mode(self):
		self.blockSignals(True)	
		used_model=inp_get_token_value(os.path.join(get_sim_path(),"light.inp"), "#light_model")
		for a in self.actions:
			a.setChecked(False)
			if a.mode==used_model:
				a.setChecked(True)
				break

		self.blockSignals(False)

	def callback_click(self,w):
		self.blockSignals(True)
		for a in self.actions:
			a.setChecked(False)

		w.setChecked(True)
		inp_update_token_value(os.path.join(get_sim_path(),"light.inp"), "#light_model",w.mode)
		self.blockSignals(False)


class optics_ribbon(ribbon_base):

	def optics(self):
		toolbar = QToolBar()
		toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		toolbar.setIconSize(QSize(42, 42))
		
		self.run = play(self,"optics_ribbon_run",run_text=wrap_text(_("Run optical simulation"),5))
		toolbar.addAction(self.run)

		self.fx_box=mode_selector()
		self.fx_box.show_all=True
		self.fx_box.update()
		toolbar.addWidget(self.fx_box)
		
		self.spectrum=tb_spectrum()
		toolbar.addWidget(self.spectrum)

		self.configwindow = QAction(icon_get("preferences-system"), _("Configure"), self)
		toolbar.addAction(self.configwindow)

		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		toolbar.addWidget(spacer)


		self.help = QAction(icon_get("help"), _("Help"), self)
		toolbar.addAction(self.help)
		return toolbar

	def export_data(self):
		toolbar = QToolBar()
		toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		toolbar.setIconSize(QSize(42, 42))
		
		self.tb_save = QAction_lock("export_image", _("Save graph"), self,"optics_ribbon_export_image")
		toolbar.addAction(self.tb_save)

		return toolbar

	def update(self):
		self.fx_box.update()

	def callback_about_dialog(self):
		dlg=about_dlg()
		dlg.exec_()

	def __init__(self):
		QTabWidget.__init__(self)
		#self.setStyleSheet("QWidget {	background-color:cyan; }")

		self.about = QToolButton(self)
		self.about.setText(_("About"))
		self.about.pressed.connect(self.callback_about_dialog)

		self.setCornerWidget(self.about)

		w=self.optics()
		self.addTab(w,_("Optics"))

		w=ribbon_optical_models()
		self.addTab(w,_("Optical models"))

		w=self.export_data()
		self.addTab(w,_("Export data"))

		sheet=self.readStyleSheet(os.path.join(get_css_path(),"style.css"))
		if sheet!=None:
			sheet=str(sheet,'utf-8')
			self.setStyleSheet(sheet)

