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

## @package update
#  Check for updates.
#

import os
from win_lin import running_on_linux
from threading import Thread
from gpvdm_http import get_data_from_web
import hashlib
from sim_warnings import sim_warnings
from code_ctrl import enable_webupdates
import i18n

_ = i18n.language.gettext
from ver import ver

#qt
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QSizePolicy,QToolBar,QAction,QTableWidget,QAbstractItemView,QTableWidgetItem,QStatusBar,QDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from gui_util import yes_no_dlg

from PyQt5.QtCore import QTimer

from disk_speed import get_disk_speed
from icon_lib import icon_get

from update_io import update_cache

from progress import progress_class
from process_events import process_events
from msg_dlg import msg_dlg


checked_web=False

my_update_class=None

def sizeof_fmt(num):
	suffix='B'
	for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
		if abs(num) < 1024.0:
			return "%3.1f%s%s" % (num, unit, suffix)
		num /= 1024.0
	return "%.1f %s%s" % (num, 'Yi', suffix)

class update_window(QWidget):
	got_updates = pyqtSignal()

	def __init__(self):
		QWidget.__init__(self)
		self.setMinimumWidth(1000)
		self.setMinimumHeight(800)

		self.vbox=QVBoxLayout()

		self.setWindowTitle(_("Download extra materials")+" (https://www.gpvdm.com)")

		toolbar=QToolBar()

		toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		toolbar.setIconSize(QSize(42, 42))

		self.tb_update = QAction_lock("update", _("Download extra\nmaterials"), self,locked=True)
		self.tb_update.secure_click.connect(self.download_updates)
		toolbar.addAction(self.tb_update)

		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		toolbar.addWidget(spacer)

		self.progress=progress_class()
		self.progress.spinner.stop()
		self.progress.spinner.hide()
		self.progress.set_text(_("Connecting to server"))
		self.progress.hide_time()
		toolbar.addWidget(self.progress)

	
		self.vbox.addWidget(toolbar)

		self.tab = QTableWidget()
		self.tab.resizeColumnsToContents()

		self.tab.verticalHeader().setVisible(False)


		
		self.tab.setColumnCount(6)
		self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)
		#self.tab.setColumnWidth(3, 200)

		self.tab.verticalHeader().setVisible(False)
		
		#self.select_param_window=select_param(self.tab)
		#self.select_param_window.set_save_function(self.save_combo)

		#self.create_model()

		#self.tab.cellChanged.connect(self.tab_changed)

		self.vbox.addWidget(self.tab)

		self.status_bar=QStatusBar()
		self.vbox.addWidget(self.status_bar)		

		self.setLayout(self.vbox)
		self.update=update_cache()
		self.show_updates()
		self.update.update_progress.connect(self.update_progress)
		self.got_updates.connect(self.show_updates)
		self.update_check()
		self.setWindowIcon(icon_get("update"))

		self.timer=QTimer()
		self.timer.setSingleShot(False)
		self.timer.timeout.connect(self.update_ui)
		self.timer.start(500)
		
	def update_progress(self,line,percent):
		if self.isVisible()==True:
			if line!=-1:
				self.tab.setItem(line,5,QTableWidgetItem(str(self.update.file_list[line].get_status())))
				self.tab.setItem(line,4,QTableWidgetItem(str(self.update.file_list[line].md5_disk)))
				self.tab.selectRow( line );

		self.progress.set_fraction(percent)
		self.progress.set_text(self.update.get_progress_text())
		process_events()

	def update_ui(self):
		if self.isVisible()==True:
			if self.update.updates_avaliable()==True:
				self.tb_update.setEnabled(True)
			else:
				self.tb_update.setEnabled(False)

			#print("write")

	def show_updates(self):
		self.tab.blockSignals(True)
		self.tab.clear()
		self.tab.setRowCount(0)
		self.tab.setColumnWidth(0, 50)
		self.tab.setColumnWidth(1, 200)
		self.tab.setColumnWidth(2, 200)
		self.tab.setColumnWidth(5, 300)
		self.tab.setHorizontalHeaderLabels([_("ID"),_("File"),_("Description"), _("Size"), _("md5"), _("status")])

		for i in range(0,len(self.update.file_list)):
			pos = self.tab.rowCount()
			self.tab.insertRow(pos)
			self.tab.setItem(pos,0,QTableWidgetItem(str(i)))
			self.tab.setItem(pos,1,QTableWidgetItem(self.update.file_list[i].file_name))
			self.tab.setItem(pos,2,QTableWidgetItem(str(self.update.file_list[i].text)))
			self.tab.setItem(pos,3,QTableWidgetItem(sizeof_fmt(self.update.file_list[i].size)))
			self.tab.setItem(pos,4,QTableWidgetItem(str(self.update.file_list[i].md5_disk)))
			self.tab.setItem(pos,5,QTableWidgetItem(str(self.update.file_list[i].get_status())))
			self.tab.setItem(pos,6,QTableWidgetItem(str(self.update.file_list[i].md5_disk)))
			#self.tab.setItem(pos,4,QTableWidgetItem(str(self.update.file_list[i].get_status())))
			#self.tab.setItem(pos,5,QTableWidgetItem(str(self.update.file_list[i].ver)))


		self.tab.blockSignals(False)
		self.status_bar.showMessage("")

	def thread_get_updates(self):
		self.update.updates_get()
		self.got_updates.emit()

	def thread_download_updates(self):
		self.update.updates_get()
		self.update.updates_download()
		self.update.updates_install()
		self.got_updates.emit()


	def update_check(self):
		self.status_bar.showMessage("Checking for updates.....")
		self.update_check_thread = Thread(target=self.thread_get_updates)
		self.update_check_thread.daemon = True
		self.update_check_thread.start()

	def download_updates(self):

		self.status_bar.showMessage("Downloading updates.....")
		p = Thread(target=self.thread_download_updates)
		p.daemon = True
		p.start()

	#def callback_download(self):
	#	self.update.updates_download()
		#updates_download(self.update)
		#updates_install(self.update)
		#self.show_updates()


		#adsad

def update_init():
	global my_update_class
	if my_update_class==None:
		my_update_class=update_window()

def update_window_show():
	global my_update_class
	my_update_class.show()


