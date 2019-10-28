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

## @package scan_ribbon
#  The ribbon for the scan window.
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
from PyQt5.QtWidgets import QWidget,QSizePolicy,QVBoxLayout,QHBoxLayout,QPushButton,QDialog,QFileDialog,QToolBar, QLineEdit, QToolButton
from PyQt5.QtWidgets import QTabWidget

from icon_lib import icon_get

from about import about_dlg

from util import wrap_text

from code_ctrl import enable_betafeatures

from ribbon_base import ribbon_base
from play import play

class scan_ribbon(ribbon_base):
		
	def scan(self):
		toolbar = QToolBar()
		toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		toolbar.setIconSize(QSize(42, 42))

		self.tb_new = QAction(icon_get("document-new"), wrap_text(_("New scan"),2), self)
		toolbar.addAction(self.tb_new)

		self.tb_delete = QAction(icon_get("edit-delete"), wrap_text(_("Delete scan"),3), self)
		toolbar.addAction(self.tb_delete)

		self.tb_clone = QAction(icon_get("clone"), wrap_text(_("Clone scan"),3), self)
		toolbar.addAction(self.tb_clone)

		self.tb_rename = QAction(icon_get("rename"), wrap_text(_("Rename scan"),3), self)
		toolbar.addAction(self.tb_rename)

		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		toolbar.addWidget(spacer)

		self.home_help = QAction(icon_get("internet-web-browser"), _("Help"), self)
		toolbar.addAction(self.home_help)

		return toolbar

	def simulations(self):
		toolbar = QToolBar()
		toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		toolbar.setIconSize(QSize(42, 42))

		self.tb_simulate = play(self,"scan_play",play_icon="forward",run_text=wrap_text(_("Run scan"),2))#QAction(icon_get("build_play2"), wrap_text(_("Run scan"),2), self)
		toolbar.addAction(self.tb_simulate)

		self.tb_run_all =  play(self,"scan_play_all",play_icon="forward2",run_text=wrap_text(_("Run all scans"),5))#QAction(icon_get("forward2"), wrap_text(_("Run all scans"),3), self)
		toolbar.addAction(self.tb_run_all)

		toolbar.addSeparator()

		self.tb_plot = QAction(icon_get("plot"), wrap_text(_("Plot"),4), self)
		toolbar.addAction(self.tb_plot)
	
		#self.tb_plot_time = QAction(icon_get("plot_time"), wrap_text(_("Time domain plot"),6), self)
		#toolbar.addAction(self.tb_plot_time)


		self.box_widget=QWidget()
		self.box=QVBoxLayout()
		self.box_widget.setLayout(self.box)
		self.box_tb0=QToolBar()
		self.box_tb0.setIconSize(QSize(32, 32))
		self.box.addWidget(self.box_tb0)
		self.box_tb1=QToolBar()
		self.box_tb1.setIconSize(QSize(32, 32))
		self.box.addWidget(self.box_tb1)
		
		self.tb_build = QAction(icon_get("cog"), wrap_text(_("Build scan"),2), self)
		self.box_tb0.addAction(self.tb_build)

		self.tb_rerun = QAction(icon_get("play-green"), wrap_text(_("Rerun"),2), self)
		#self.box_tb0.addAction(self.tb_rerun)

		self.tb_zip = QAction(icon_get("package-x-generic"), wrap_text(_("Archive simulations"),2), self)
		self.box_tb0.addAction(self.tb_zip)


		self.tb_clean = QAction(icon_get("clean"), wrap_text(_("Clean simulation"),4), self)
		self.box_tb1.addAction(self.tb_clean )



		self.tb_notes = QAction(icon_get("text-x-generic"), wrap_text(_("Notes"),3), self)
		toolbar.addAction(self.tb_notes)

		toolbar.addWidget(self.box_widget)
		
		return toolbar

	def nested(self):
		toolbar = QToolBar()
		toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		toolbar.setIconSize(QSize(42, 42))

		self.menu_run_nested = QAction(icon_get("nested"), wrap_text(_("Build nested simulation"),5), self)
		toolbar.addAction(self.menu_run_nested)

		return toolbar

	def advanced(self):
		toolbar = QToolBar()
		toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		toolbar.setIconSize(QSize(42, 42))

		self.menu_plot_fits = QAction(icon_get("scan2"), wrap_text(_("Plot fits"),5), self)
		toolbar.addAction(self.menu_plot_fits)

		self.sim_no_gen = QAction(icon_get("forward"), wrap_text(_("Run simulation no generation"),5), self)
		toolbar.addAction(self.sim_no_gen)

		self.single_fit = QAction(icon_get("forward"), wrap_text(_("Run single fit"),5), self)
		toolbar.addAction(self.single_fit)

		self.clean_unconverged = QAction(icon_get("clean"), wrap_text(_("Clean unconverged simulation"),5), self)
		toolbar.addAction(self.clean_unconverged)

		self.clean_sim_output = QAction(icon_get("forward"), wrap_text(_("Clean simulation output"),5), self)
		toolbar.addAction(self.clean_sim_output)

		self.push_unconverged_to_hpc = QAction(icon_get("forward"), wrap_text(_("Push unconverged to hpc"),5), self)
		toolbar.addAction(self.push_unconverged_to_hpc)

		self.change_dir = QAction(icon_get("forward"), wrap_text(_("Change dir"),5), self)
		toolbar.addAction(self.change_dir)

		self.report = QAction(icon_get("office-calendar"), wrap_text(_("Report"),5), self)
		toolbar.addAction(self.report)

		return toolbar

	def ml(self):
		toolbar = QToolBar()
		toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		toolbar.setIconSize(QSize(42, 42))

		self.tb_ml_build_vectors = QAction(icon_get("ml"), wrap_text(_("Build vectors"),4), self)
		toolbar.addAction(self.tb_ml_build_vectors)


		return toolbar

	def update(self):
		print("update")
		#self.device.update()
		#self.simulations.update()
		#self.configure.update()
		#self.home.update()

	def callback_about_dialog(self):
		dlg=about_dlg()
		dlg.exec_()

	def __init__(self):
		ribbon_base.__init__(self)
		self.setMaximumHeight(130)
		#self.setStyleSheet("QWidget {	background-color:cyan; }")

		self.about = QToolButton(self)
		self.about.setText(_("About"))
		self.about.pressed.connect(self.callback_about_dialog)

		self.setCornerWidget(self.about)

		w=self.scan()
		self.addTab(w,_("Scan"))
		
		w=self.simulations()
		self.addTab(w,_("Simulations"))


		w=self.advanced()
		if enable_betafeatures()==True:
			self.addTab(w,_("Advanced"))

		w=self.nested()
		if enable_betafeatures()==True:
			self.addTab(w,_("Nested"))

		w=self.ml()
		if enable_betafeatures()==True:
			self.addTab(w,_("ML"))

		sheet=self.readStyleSheet(os.path.join(get_css_path(),"style.css"))
		if sheet!=None:
			sheet=str(sheet,'utf-8')
			self.setStyleSheet(sheet)

