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


## @package mobility_widget
#  A widget to adjust mobility
#


import os

#qt
from PyQt5.QtWidgets import QMainWindow,QLabel, QFrame,QTextEdit, QAction,QApplication,QTableWidgetItem,QComboBox, QMessageBox, QDialog, QDialogButtonBox, QFileDialog
from PyQt5.QtWidgets import QGraphicsScene,QListWidgetItem,QListView,QLineEdit,QWidget,QHBoxLayout,QPushButton,QSizePolicy
from PyQt5.QtWidgets import QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtCore import QPersistentModelIndex
from QComboBoxLang import QComboBoxLang
from PyQt5.QtGui import QIcon


#cal_path
from cal_path import get_ui_path
from PyQt5.QtCore import pyqtSignal

from epitaxy import get_epi
from inp import inp
from dos_io import gen_fermi_from_np
from dos_io import gen_np_from_fermi
import decimal

import i18n
_ = i18n.language.gettext


class mobility_widget(QWidget):

	changed = pyqtSignal()

	def __init__(self,electrons=True):
		QWidget.__init__(self)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.raw_value="ground"
		self.hbox=QHBoxLayout()
		self.combobox = QComboBoxLang()
		self.combobox.setMaximumWidth( 100 )
		self.combobox.addItemLang("symmetric",_("Symmetric"))
		self.combobox.addItemLang("asymmetric",_("Asymmetric"))


		self.edit_z=QLineEdit()
		self.edit_z.setMaximumWidth( 90 )
		self.label_z=QLabel("z: ")
		self.label_z.setStyleSheet("QLabel { border: 0px; padding: 0px; }");
		self.label_z.setMaximumWidth( 10 )

		self.edit_x=QLineEdit()
		self.edit_x.setMaximumWidth( 90 )
		self.label_x=QLabel("x: ")
		self.label_x.setStyleSheet("QLabel { border: 0px; padding: 0px; }");
		self.label_x.setMaximumWidth( 10 )

		self.edit_y=QLineEdit()
		self.edit_y.setMaximumWidth( 90 )
		self.label_y=QLabel("y: ")
		self.label_y.setStyleSheet("QLabel { border: 0px; padding: 0px; }");
		self.label_y.setMaximumWidth( 10 )

		#self.button=QPushButton()
		#self.button.setFixedSize(25, 25)
		#self.button.setText("...")
		self.hbox.addWidget(self.label_z,Qt.AlignLeft)
		self.hbox.addWidget(self.edit_z,Qt.AlignLeft)
		self.hbox.addWidget(self.label_x,Qt.AlignLeft)
		self.hbox.addWidget(self.edit_x,Qt.AlignLeft)
		self.hbox.addWidget(self.label_y,Qt.AlignLeft)
		self.hbox.addWidget(self.edit_y,Qt.AlignLeft)
		self.hbox.addStretch()
		self.hbox.addWidget(self.combobox)

		self.hbox.setSpacing(0)
		#self.hbox.addWidget(self.button)

		self.edit_z.textChanged.connect(self.callback_edit)
		self.edit_x.textChanged.connect(self.callback_edit)
		self.edit_y.textChanged.connect(self.callback_edit)

		self.hbox.setContentsMargins(0, 0, 0, 0)
		self.edit_z.setStyleSheet("QLineEdit { border: none }");
		self.edit_x.setStyleSheet("QLineEdit { border: none }");
		self.edit_y.setStyleSheet("QLineEdit { border: none }");


		#self.button.clicked.connect(self.callback_button_click)
		self.combobox.currentIndexChanged.connect(self.callback_combobox)
		#self.edit.textChanged.connect(self.callback_edit)
		#self.setStyleSheet("background-color:black;");
		self.setLayout(self.hbox)

	def update(self):
		if self.combobox.currentText_english()=="symmetric":
			self.edit_z.setVisible(False)
			self.label_z.setVisible(False)

			self.edit_x.setVisible(False)
			self.label_x.setVisible(False)

			self.label_y.setVisible(False)
			self.edit_y.setMaximumWidth( 120 )

		else:
			self.edit_z.setVisible(True)
			self.label_z.setVisible(True)

			self.edit_x.setVisible(True)
			self.label_x.setVisible(True)

			self.label_y.setVisible(True)
			self.edit_x.setMaximumWidth( 90 )
			self.edit_y.setMaximumWidth( 90 )
			self.edit_z.setMaximumWidth( 90 )

	def callback_edit(self):
		self.changed.emit()

	def callback_combobox(self):
		#self.applied_voltage_type=self.combobox.currentText_english()
		self.update()
		self.changed.emit()

	def set_values(self,values):
		self.combobox.setValue_using_english(values[0])
		self.edit_z.setText(values[1])
		self.edit_x.setText(values[2])
		self.edit_y.setText(values[3])
		self.update()
	
	def get_values(self):
		return [self.combobox.currentText_english(),self.edit_z.text(),self.edit_x.text(),self.edit_y.text()]
		
