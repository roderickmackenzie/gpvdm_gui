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

## @package tb_item_is_imps
#  An IS/IMPS simulation selector toolbar widget.
#


#inp
from inp import inp_update_token_value
from inp import inp_get_token_value

#from global_objects import global_object_get
#from global_objects import global_isobject

import i18n
_ = i18n.language.gettext

#qt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QSizePolicy,QVBoxLayout,QPushButton,QDialog,QFileDialog,QToolBar,QLabel,QComboBox
from PyQt5.QtCore import pyqtSignal

from code_ctrl import enable_betafeatures

class tb_item_is_imps(QWidget):

	changed = pyqtSignal()
	
	def call_back_mode_changed(self):
		#light_power=self.mode.currentText()
		self.changed.emit()

	def setText(self,value):
		self.mode.blockSignals(True)
		all_items  = [self.mode.itemText(i) for i in range(self.mode.count())]
		for i in range(0,len(all_items)):
		    if all_items[i] == value:
		        self.mode.setCurrentIndex(i)
		self.mode.blockSignals(False)

	def update(self):
		self.mode.blockSignals(True)
		self.mode.clear()
			
		self.mode.addItem("is")
		self.mode.addItem("imps")

		self.mode.blockSignals(False)


	def __init__(self):
		QWidget.__init__(self)

		layout=QVBoxLayout()
		label=QLabel()
		label.setText(_("Modulation type"))
		layout.addWidget(label)

		self.mode = QComboBox(self)
		self.mode.setEditable(False)

		layout.addWidget(self.mode)

		self.setLayout(layout)

		self.update()

		self.mode.currentIndexChanged.connect(self.call_back_mode_changed)



