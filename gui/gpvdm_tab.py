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

## @package gpvdm_tab
#  A table widget
#

import os

#qt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QSizePolicy,QHBoxLayout,QPushButton,QDialog,QFileDialog,QToolBar, QMessageBox, QVBoxLayout, QGroupBox, QTableWidget,QAbstractItemView, QTableWidgetItem, QComboBox

from QComboBoxLang import QComboBoxLang
from PyQt5.QtGui import QIcon

from gpvdm_select import gpvdm_select
from gtkswitch import gtkswitch
from leftright import leftright
from gpvdm_select_material import gpvdm_select_material

class gpvdm_tab(QTableWidget):

	def set_value(self,y,x,value):
		if type(self.cellWidget(y, x))==QComboBox:
			self.cellWidget(y, x).blockSignals(True)
			self.cellWidget(y, x).setCurrentIndex(self.cellWidget(y, x).findText(value))
			self.cellWidget(y, x).blockSignals(False)
		elif type(self.cellWidget(y, x))==QComboBoxLang:
			self.cellWidget(y, x).blockSignals(True)
			self.cellWidget(y, x).setValue_using_english(value)
			self.cellWidget(y, x).blockSignals(False)
		elif type(self.cellWidget(y,x))==gpvdm_select:
			self.cellWidget(y, x).blockSignals(True)
			self.cellWidget(y, x).setText(value)
			self.cellWidget(y, x).blockSignals(False)
		elif type(self.cellWidget(y,x))==gtkswitch:
			self.cellWidget(y, x).blockSignals(True)
			self.cellWidget(y, x).set_value(str2bool(value))
			self.cellWidget(y, x).blockSignals(False)
		else:
			item = QTableWidgetItem(str(value))
			self.setItem(y,x,item)

