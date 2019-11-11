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
from epitaxy import get_epi
from scan_item import scan_item_add

import i18n
_ = i18n.language.gettext


#contacts io
from contacts_io import segment

#qt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QSizePolicy,QHBoxLayout,QPushButton,QDialog,QFileDialog,QToolBar, QMessageBox, QVBoxLayout, QGroupBox, QTableWidget,QAbstractItemView, QTableWidgetItem, QComboBox

from PyQt5.QtCore import pyqtSignal


from str2bool import str2bool
from error_dlg import error_dlg

from global_objects import global_object_run

from QComboBoxLang import QComboBoxLang
from QComboBoxShape import QComboBoxShape

from QWidgetSavePos import QWidgetSavePos

from contacts_boundary import contacts_boundary
from gpvdm_tab import gpvdm_tab

from file_watch import get_watch

from mesh import mesh_get_zpoints
from mesh import mesh_get_xpoints

class contacts_window(QWidgetSavePos):

	visible=1
	
	changed = pyqtSignal()

	def callback_contacts_boundary(self):
		self.charge_density_window=contacts_boundary()
		self.charge_density_window.show()

	def update_contact_db(self):
		for i in range(0,self.tab.rowCount()):
			try:
				float(self.tab.get_value(i, 3))
				float(self.tab.get_value(i, 4))
				float(self.tab.get_value(i, 5))
				float(self.tab.get_value(i, 6))
				float(self.tab.get_value(i, 7))
			except:
				return False

		if self.tab.rowCount()!=len(self.contacts.contacts):
			print("don't match")
			return False

		for i in range(0,self.tab.rowCount()):
			self.contacts.contacts[i].name=self.tab.get_value(i, 0)
			self.contacts.contacts[i].position=self.tab.get_value(i, 1)
			self.contacts.contacts[i].active=str2bool(self.tab.get_value(i, 2))

			if self.contacts.contacts[i].position=="top" or self.contacts.contacts[i].position=="bottom":
				self.contacts.contacts[i].shape.x0=float(self.tab.get_value(i, 3))
				self.contacts.contacts[i].shape.dx=float(self.tab.get_value(i, 4))
			else:
				self.contacts.contacts[i].shape.y0=float(self.tab.get_value(i, 3))
				self.contacts.contacts[i].shape.dy=float(self.tab.get_value(i, 4))

			self.contacts.contacts[i].ingress=float(self.tab.get_value(i, 5))
			self.contacts.contacts[i].voltage=float(self.tab.get_value(i, 6))
			self.contacts.contacts[i].np=float(self.tab.get_value(i, 7))
			self.contacts.contacts[i].charge_type=self.tab.get_value(i, 8)

			if self.contacts.contacts[i].shape.type!=self.tab.get_value(i, 9):
				self.contacts.contacts[i].shape.type=self.tab.get_value(i, 9)
				self.contacts.contacts[i].shape.load_triangles()

		return True


	def set_row(self,pos,name,top_btm,active,start,width,ingress,voltage,np,charge_type,shape):
		self.tab.blockSignals(True)

		self.tab.set_value(pos,0,name)
		self.tab.set_value(pos,1,top_btm.lower())
		self.tab.set_value(pos,2,str(active).lower())
		self.tab.set_value(pos,3,start)
		self.tab.set_value(pos,4,width)
		self.tab.set_value(pos,5,ingress)
		self.tab.set_value(pos,6,voltage)
		self.tab.set_value(pos,7,np)
		self.tab.set_value(pos,8, charge_type.lower())
		self.tab.set_value(pos,9, shape)

		self.tab.blockSignals(False)
		

	def add_row(self):

		pos= self.tab.insert_row()

		self.tab.blockSignals(True)
		self.tab.setItem(pos,0,QTableWidgetItem(""))

		combobox = QComboBoxLang()
		combobox.addItemLang("top",_("top"))
		combobox.addItemLang("bottom",_("bottom"))
		combobox.addItemLang("right",_("right"))
		combobox.addItemLang("left",_("left"))

		self.tab.setCellWidget(pos,1, combobox)
		combobox.currentIndexChanged.connect(self.save)

		combobox = QComboBoxLang()
		combobox.addItemLang("true",_("true"))
		combobox.addItemLang("false",_("false"))
		self.tab.setCellWidget(pos,2, combobox)
		combobox.currentIndexChanged.connect(self.save)
		
		self.tab.setItem(pos,3,QTableWidgetItem(""))
		self.tab.setItem(pos,4,QTableWidgetItem(""))

		self.tab.setItem(pos,5,QTableWidgetItem(""))
		self.tab.setItem(pos,6,QTableWidgetItem(""))
		self.tab.setItem(pos,7,QTableWidgetItem(""))


		combobox = QComboBoxLang()
		combobox.addItemLang("electron",_("Electron"))
		combobox.addItemLang("hole",_("Hole"))

		self.tab.setCellWidget(pos,8, combobox)
		combobox.currentIndexChanged.connect(self.save)

		combobox = QComboBoxShape()

		self.tab.setCellWidget(pos,9, combobox)
		combobox.currentIndexChanged.connect(self.save)

		self.tab.blockSignals(False)
		
		return pos

	def on_add_clicked(self, button):

		pos=self.add_row()

		new_shape_file=get_epi().gen_new_electrical_file("shape")
		c=self.contacts.insert(pos,new_shape_file)

		self.set_row(pos,c.name,c.position,c.active,str(c.shape.x0),str(c.shape.dx),str(c.voltage),str(c.np),str(c.charge_type),c.shape.type)
		#print(pos,len(self.contacts))
		#self.save()

	def on_remove_clicked(self, button):
		items=self.tab.remove()

		if len(items)!=0:
			self.contacts.remove(items[0])
			self.save()

	def save(self):
		if self.update_contact_db()==True:
			self.contacts.save()
			self.changed.emit()
			global_object_run("gl_force_redraw")
		else:
			error_dlg(self,_("There are some non numeric values in the table"))


	def callback_help(self):
		webbrowser.open('http://www.gpvdm.com/man/index.html')

	def tab_changed(self, x,y):
		self.save()

	def update(self):
		i=0
		for c in self.contacts:
			self.set_row(i,str(c.name),c.position,str(c.active),str(c.start),str(c.width),str(c.voltage),str(c.np),str(c.charge_type), c.shape.type)
			i=i+1

	def hide_cols(self,val):
		self.tab.setColumnHidden(3,val)
		self.tab.setColumnHidden(4,val)
		self.tab.setColumnHidden(5,val)


	def load(self):
		self.contacts=get_epi().contacts
		self.tab.clear()
		self.tab.setHorizontalHeaderLabels([_("Name"),_("Top/Bottom"),_("Active contact"),_("Start")+" (m)", _("Width")+" (m)" , _("Ingress")+" (m)",_("Voltage"),_("Charge density"),_("Charge type"),_("Shape")])
		self.contacts.load()

		if mesh_get_zpoints()!=1 or mesh_get_xpoints()!=1: 
			self.hide_cols(False)
		else:
			self.hide_cols(True)

		#contacts_print()
		i=0
		for c in self.contacts.contacts:
			self.add_row()
			if c.position=="top" or c.position=="bottom":
				start=str(c.shape.x0)
				width=str(c.shape.dx)
			else:
				start=str(c.shape.y0)
				width=str(c.shape.dy)
			print(c.position,c.shape.y0,c.shape.z0)

			self.set_row(i,str(c.name),c.position,str(c.active),start,width,str(c.ingress),str(c.voltage),str(c.np),str(c.charge_type) , c.shape.type)

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

		self.tab = gpvdm_tab()
		self.tab.resizeColumnsToContents()

		self.tab.verticalHeader().setVisible(False)

		self.tab.clear()
		self.tab.setColumnCount(10)
		self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)

		self.load()

		self.tab.cellChanged.connect(self.tab_changed)

		self.main_vbox.addWidget(self.tab)


		self.setLayout(self.main_vbox)

		#get_contactsio().changed.connect(self.update)


