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

## @package contacts
#  Window to configure the contacts
#

import os
from numpy import *
import webbrowser
from inp import inp_search_token_value
from icon_lib import icon_get

from scan_item import scan_item_add

import i18n
_ = i18n.language.gettext


#contacts io
from contacts_io import segment
from contacts_io import contacts_save
from contacts_io import contacts_get_array
from contacts_io import contacts_clear
from contacts_io import contacts_print
from contacts_io import contacts_load
from contacts_io import contacts_print
from contacts_io import contacts_append

#qt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QSizePolicy,QHBoxLayout,QPushButton,QDialog,QFileDialog,QToolBar, QMessageBox, QVBoxLayout, QGroupBox, QTableWidget,QAbstractItemView, QTableWidgetItem, QComboBox

from PyQt5.QtCore import pyqtSignal

from gui_util import tab_get_value
from gui_util import tab_set_value
from gui_util import tab_insert_row
from gui_util import tab_remove

from util import str2bool
from error_dlg import error_dlg

from global_objects import global_object_run

from QComboBoxLang import QComboBoxLang
from QWidgetSavePos import QWidgetSavePos

from contacts_boundary import contacts_boundary

class contacts_window(QWidgetSavePos):

	visible=1
	
	changed = pyqtSignal()

	def callback_contacts_boundary(self):
		self.charge_density_window=contacts_boundary()
		self.charge_density_window.show()

	def update_contact_db(self):
		for i in range(0,self.tab.rowCount()):
			try:
				float(tab_get_value(self.tab,i, 3))
				float(tab_get_value(self.tab,i, 4))
				float(tab_get_value(self.tab,i, 5))
				float(tab_get_value(self.tab,i, 6))
			except:
				return False

		contacts_clear()
		for i in range(0,self.tab.rowCount()):
			contacts_append(tab_get_value(self.tab,i, 0),tab_get_value(self.tab,i, 1),str2bool(tab_get_value(self.tab,i, 2)),float(tab_get_value(self.tab,i, 3)),float(tab_get_value(self.tab,i, 4)),float(tab_get_value(self.tab,i, 5)),float(tab_get_value(self.tab,i, 6)),float(tab_get_value(self.tab,i, 7)),tab_get_value(self.tab,i, 8))
		return True
	
	def add_row(self,pos,name,top_btm,active,start,width,depth,voltage,np,charge_type):

		pos= tab_insert_row(self.tab)

		self.tab.blockSignals(True)
		self.tab.setItem(pos,0,QTableWidgetItem(name))

		combobox = QComboBoxLang()
		combobox.addItemLang("top",_("top"))
		combobox.addItemLang("bottom",_("bottom"))

		self.tab.setCellWidget(pos,1, combobox)
		combobox.setValue_using_english(top_btm.lower())
		#combobox.setCurrentIndex(combobox.findText(top_btm.lower()))
		combobox.currentIndexChanged.connect(self.save)

		combobox = QComboBoxLang()
		combobox.addItemLang("true",_("true"))
		combobox.addItemLang("false",_("false"))

		self.tab.setCellWidget(pos,2, combobox)
		combobox.setValue_using_english(active.lower()) #setCurrentIndex(combobox.findText(active.lower()))
		combobox.currentIndexChanged.connect(self.save)
		
		self.tab.setItem(pos,3,QTableWidgetItem(start))
		self.tab.setItem(pos,4,QTableWidgetItem(width))
		self.tab.setItem(pos,5,QTableWidgetItem(depth))
		self.tab.setItem(pos,6,QTableWidgetItem(voltage))
		self.tab.setItem(pos,7,QTableWidgetItem(np))


		combobox = QComboBoxLang()
		combobox.addItemLang("electron",_("Electron"))
		combobox.addItemLang("hole",_("Hole"))

		self.tab.setCellWidget(pos,8, combobox)
		combobox.setValue_using_english(charge_type.lower())
		combobox.currentIndexChanged.connect(self.save)




		self.tab.blockSignals(False)
		
	def on_add_clicked(self, button):
		index = self.tab.selectionModel().selectedRows()

		if len(index)>0:
			pos=index[0].row()+1
		else:
			pos = self.tab.rowCount()

		self.add_row(pos,"","top","false","0.0","0.0","0.0","0.0","0.0","electron")
 
		self.save()

	def on_remove_clicked(self, button):
		tab_remove(self.tab)
		self.save()

	def save(self):
		if self.update_contact_db()==True:
			contacts_save()
			self.changed.emit()
			global_object_run("gl_force_redraw")
		else:
			error_dlg(self,_("There are some non numeric values in the table"))


	def callback_help(self):
		webbrowser.open('http://www.gpvdm.com/man/index.html')

	def tab_changed(self, x,y):
		self.save()

	def load(self):
		self.tab.clear()
		self.tab.setHorizontalHeaderLabels([_("Name"),_("Top/Bottom"),_("Active contact"),_("Start")+" (m)", _("Width")+" (m)",_("Depth")+" (m)",_("Voltage"),_("Charge density"),_("Charge type")])
		contacts_load()
		#contacts_print()
		contacts=contacts_get_array()
		i=0
		for c in contacts_get_array():
			self.add_row(i,str(c.name),str(c.position),str(c.active),str(c.start),str(c.width),str(c.depth),str(c.voltage),str(c.np),str(c.charge_type))

			i=i+1


	def __init__(self):
		QWidgetSavePos.__init__(self,"contacts")
		self.setMinimumSize(1000, 400)

		self.setWindowIcon(icon_get("contact"))

		self.setWindowTitle(_("Edit contacts")+" (www.gpvdm.com)") 
		
		self.main_vbox = QVBoxLayout()

		toolbar=QToolBar()
		toolbar.setIconSize(QSize(48, 48))

		add = QAction(icon_get("list-add"),  _("Add contact"), self)
		add.triggered.connect(self.on_add_clicked)
		toolbar.addAction(add)

		remove = QAction(icon_get("list-remove"),  _("Remove contacts"), self)
		remove.triggered.connect(self.on_remove_clicked)
		toolbar.addAction(remove)

		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		toolbar.addWidget(spacer)

		self.charge_density = QAction(icon_get("preferences-system"), _("Charge density"), self)
		self.charge_density.triggered.connect(self.callback_contacts_boundary)
		toolbar.addAction(self.charge_density)

		self.help = QAction(icon_get("help"), _("Help"), self)
		self.help.setStatusTip(_("Close"))
		self.help.triggered.connect(self.callback_help)
		toolbar.addAction(self.help)

		self.main_vbox.addWidget(toolbar)

		self.tab = QTableWidget()
		self.tab.resizeColumnsToContents()

		self.tab.verticalHeader().setVisible(False)

		self.tab.clear()
		self.tab.setColumnCount(9)
		self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)

		self.load()

		self.tab.cellChanged.connect(self.tab_changed)

		self.main_vbox.addWidget(self.tab)


		self.setLayout(self.main_vbox)

