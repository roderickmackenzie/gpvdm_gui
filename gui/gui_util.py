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

## @package gui_util
#  GUI utilities.
#


from cal_path import get_image_file_path
import os

#qt
from gui_enable import gui_get

if gui_get()==True:
	from PyQt5.QtWidgets import QTextEdit, QAction,QTableWidgetItem,QComboBox, QMessageBox, QDialog, QDialogButtonBox
	from PyQt5.QtWidgets import QListWidgetItem,QListView,QLineEdit,QWidget,QHBoxLayout,QPushButton
	from PyQt5.uic import loadUi
	from PyQt5.QtGui import QPixmap
	from PyQt5.QtCore import QSize, Qt, QTimer
	from QComboBoxLang import QComboBoxLang
	from PyQt5.QtGui import QIcon

#windows
from cal_path import get_ui_path

from icon_lib import icon_get


from str2bool import str2bool

class dlg_get_text():
	def __init__(self,text,default,image):
		#QDialog.__init__(self)
		self.ui = loadUi(os.path.join(get_ui_path(),"question.ui"))
		self.ui.label.setText(text)
		self.ui.text.setText(default)
		#pixmap = QPixmap(os.path.join(get_image_file_path(),image))
		icon=icon_get(image)
		self.ui.setWindowIcon(icon)
		self.ui.image.setPixmap(icon.pixmap(icon.actualSize(QSize(64, 64))))
		ret=self.ui.exec_()
		if ret==True:
			self.ret=self.ui.text.text()
		else:
			self.ret=None


def yes_no_dlg(parent,text):
	msgBox = QMessageBox(parent)
	msgBox.setIcon(QMessageBox.Question)
	msgBox.setText("Question")
	msgBox.setInformativeText(text)
	msgBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No )
	msgBox.setDefaultButton(QMessageBox.No)
	reply = msgBox.exec_()
	if reply == QMessageBox.Yes:
		return True
	else:
		return False

def yes_no_cancel_dlg(parent,text):
	msgBox = QMessageBox(parent)
	msgBox.setIcon(QMessageBox.Question)
	msgBox.setText("Question")
	msgBox.setInformativeText(text)
	msgBox.setStandardButtons(QMessageBox.Yes| QMessageBox.No| QMessageBox.Cancel  )
	msgBox.setDefaultButton(QMessageBox.No)
	reply = msgBox.exec_()
	if reply == QMessageBox.Yes:
		return "yes"
	elif reply == QMessageBox.No:
		return "no"
	else:
		return "cancel"
