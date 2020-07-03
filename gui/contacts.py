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

import i18n
_ = i18n.language.gettext


#qt
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QSizePolicy,QDialog,QFileDialog,QToolBar, QMessageBox, QVBoxLayout, QGroupBox, QTableWidget,QAbstractItemView, QTableWidgetItem, QComboBox

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

from mesh import get_mesh
from energy_to_charge import energy_to_charge

from gpvdm_select_material import gpvdm_select_material
from gpvdm_applied_voltage import gpvdm_applied_voltage

class contacts_window(QWidgetSavePos):


	changed = pyqtSignal()

	def callback_contacts_boundary(self):
		self.charge_density_window=contacts_boundary()
		self.charge_density_window.show()

	def update_contact_db(self):
		#first_contact
		#print("oh")
		for i in range(0,self.tab.rowCount()):
			try:
				float(self.tab.get_value(i, 3))
				float(self.tab.get_value(i, 4))
				float(self.tab.get_value(i, 5))
				#float(self.tab.get_value(i, 6))
				float(self.tab.get_value(i, 7))
			except:
				return False

		if self.tab.rowCount()!=len(self.contacts.contacts):
			print("don't match")
			return False

		for i in range(0,self.tab.rowCount()):
			self.contacts.contacts[i].shape.name=self.tab.get_value(i, 0)
			self.contacts.contacts[i].position=self.tab.get_value(i, 1)
			self.contacts.contacts[i].applied_voltage_type=self.tab.get_value(i, 2).split(":")[0]
			self.contacts.contacts[i].applied_voltage=self.tab.get_value(i, 2).split(":")[1]
			#print(self.tab.get_value(i, 2))

			if self.contacts.contacts[i].position=="top" or self.contacts.contacts[i].position=="bottom":
				self.contacts.contacts[i].shape.x0=float(self.tab.get_value(i, 3))
				self.contacts.contacts[i].shape.dx=float(self.tab.get_value(i, 4))
			else:
				self.contacts.contacts[i].shape.y0=float(self.tab.get_value(i, 3))
				self.contacts.contacts[i].shape.dy=float(self.tab.get_value(i, 4))

			self.contacts.contacts[i].contact_resistance_sq=self.tab.get_value(i, 5)
			self.contacts.contacts[i].shunt_resistance_sq=self.tab.get_value(i, 6)
			self.contacts.contacts[i].np=float(self.tab.get_value(i, 7))
			self.contacts.contacts[i].charge_type=self.tab.get_value(i, 8)


			self.contacts.contacts[i].ve0=self.tab.get_value(i, 9)
			self.contacts.contacts[i].vh0=self.tab.get_value(i, 10)
			self.contacts.contacts[i].physical_model=self.tab.get_value(i, 11)

			if self.contacts.contacts[i].shape.type!=self.tab.get_value(i, 12):
				self.contacts.contacts[i].shape.type=self.tab.get_value(i, 12)
				self.contacts.contacts[i].shape.load_triangles()

			self.contacts.contacts[i].shape.optical_material=self.tab.get_value(i, 13)

		return True


	def set_row(self,pos,name,position,applied_voltage_type, applied_voltage, start, width, contact_resistance_sq, shunt_resistance_sq, np, charge_type,ve0,vh0,type,shape,material):
		self.tab.blockSignals(True)

		self.tab.set_value(pos,0,name)
		self.tab.set_value(pos,1,position.lower())
		self.tab.set_value(pos,2,applied_voltage_type+":"+applied_voltage)
		self.tab.set_value(pos,3,start)
		self.tab.set_value(pos,4,width)
		self.tab.set_value(pos,5,contact_resistance_sq)
		self.tab.set_value(pos,6,shunt_resistance_sq)
		self.tab.set_value(pos,7,np)
		self.tab.set_value(pos,8, charge_type.lower())
		self.tab.set_value(pos,9,ve0)
		self.tab.set_value(pos,10,vh0)
		self.tab.set_value(pos,11,type)
		self.tab.set_value(pos,12, shape)
		self.tab.set_value(pos,13, material)


		self.tab.blockSignals(False)
		

	def add_row(self):

		pos= self.tab.insert_row()

		#name
		self.tab.blockSignals(True)
		self.tab.setItem(pos,0,QTableWidgetItem(""))

		#position
		combobox = QComboBoxLang()
		combobox.addItemLang("top",_("top"))
		combobox.addItemLang("bottom",_("bottom"))
		combobox.addItemLang("right",_("right"))
		combobox.addItemLang("left",_("left"))

		self.tab.setCellWidget(pos,1, combobox)
		combobox.currentIndexChanged.connect(self.save_and_redraw)


		#combobox = QComboBoxLang()
		#combobox.addItemLang("true",_("true"))
		#combobox.addItemLang("false",_("false"))
		#self.tab.setCellWidget(pos,2, combobox)
		#combobox.currentIndexChanged.connect(self.save_and_redraw)
		#applied_voltage
		#self.tab.setItem(pos,2,QTableWidgetItem(""))
		applied_voltage=gpvdm_applied_voltage()
		self.tab.setCellWidget(pos,2, applied_voltage)
		applied_voltage.changed.connect(self.save)
		self.tab.setColumnWidth(2, 200)

		self.tab.setItem(pos,3,QTableWidgetItem(""))
		self.tab.setItem(pos,4,QTableWidgetItem(""))

		self.tab.setItem(pos,5,QTableWidgetItem(""))
		self.tab.setColumnWidth(5, 140)

		self.tab.setItem(pos,6,QTableWidgetItem(""))
		self.tab.setColumnWidth(6, 110)

		energy_to_charge_box=energy_to_charge()
		self.tab.setCellWidget(pos,7, energy_to_charge_box)
		self.tab.setColumnWidth(7, 150)
		energy_to_charge_box.changed.connect(self.save)

		#self.tab.setItem(pos,7,QTableWidgetItem(""))		

		combobox = QComboBoxLang()
		combobox.addItemLang("electron",_("Electron"))
		combobox.addItemLang("hole",_("Hole"))

		self.tab.setCellWidget(pos,8, combobox)
		combobox.currentIndexChanged.connect(self.save)
		self.tab.setColumnWidth(8, 120)

		self.tab.setItem(pos,9,QTableWidgetItem(""))
		self.tab.setItem(pos,10,QTableWidgetItem(""))

		combobox = QComboBoxLang()
		combobox.addItemLang("ohmic",_("Ohmic"))
		combobox.addItemLang("schottky",_("Schottky"))

		self.tab.setCellWidget(pos,11, combobox)
		combobox.currentIndexChanged.connect(self.save)



		combobox = QComboBoxShape()

		self.tab.setCellWidget(pos,12, combobox)
		combobox.currentIndexChanged.connect(self.save_and_redraw)

		combobox = gpvdm_select_material()
		combobox.changed.connect(self.save)
		self.tab.setCellWidget(pos,13, combobox)

		self.tab.blockSignals(False)
		
		return pos

	def on_add_clicked(self, button):

		pos=self.add_row()

		new_shape_file=get_epi().gen_new_electrical_file("shape")
		c=self.contacts.insert(pos,new_shape_file)

		self.set_row(pos,c.shape.name,c.position,c.applied_voltage_type,c.applied_voltage,str(c.shape.x0),str(c.shape.dx),str(c.contact_resistance_sq),c.shunt_resistance_sq,str(c.np),str(c.charge_type),str(c.ve0),str(c.vh0),str(c.physical_model),c.shape.type,c.shape.optical_material)
		#print(pos,len(self.contacts))
		self.save_and_redraw()

	def on_remove_clicked(self, button):
		items=self.tab.remove()

		if len(items)!=0:
			self.contacts.remove(items[0])
			self.save_and_redraw()

	def show_hide_cols(self):
		schottky=False
		for i in range(0,self.tab.rowCount()):
			if self.tab.get_value(i, 11)=="schottky":
				schottky=True
				break

		if schottky==True:
			self.tab.setColumnHidden(9,False)
			self.tab.setColumnHidden(10,False)
		else:
			self.tab.setColumnHidden(9,True)
			self.tab.setColumnHidden(10,True)

	def save_and_redraw(self):
		print("save and redraw called")
		self.save()
		self.changed.emit()
		global_object_run("gl_force_redraw")

	def save(self):
		print("save now")
		if self.update_contact_db()==True:
			for i in range(0,self.tab.rowCount()):
				self.tab.cellWidget(i,7).position=self.tab.get_value(i, 1)
				self.tab.cellWidget(i,7).charge_type=self.tab.get_value(i, 8)

			self.show_hide_cols()
			self.contacts.save()


	def callback_help(self):
		webbrowser.open('http://www.gpvdm.com/man/index.html')

	def tab_changed(self, x,y):
		self.save_and_redraw()

	def update(self):
		i=0
		for c in self.contacts:
			self.set_row(i,str(c.shape.name),c.position,c.applied_voltage_type, c.applied_voltage, str(c.start), str(c.width), str(c.np), str(c.charge_type), c.shape.type)
			i=i+1

	def hide_cols(self,val):
		self.tab.setColumnHidden(3,val)
		self.tab.setColumnHidden(4,val)
		#self.tab.setColumnHidden(5,val)


	def load(self):
		self.contacts=get_epi().contacts
		self.tab.clear()
		self.tab.setHorizontalHeaderLabels([_("Name"),_("Top/Bottom"),_("Applied\nvoltage"),_("Start")+" (m)", _("Width")+" (m)" , _("Contact resistance\n")+" (Ohms m^2)",_("Shunt resistance")+"\n(Ohms m^2)",_("Charge density/\nFermi-offset"),_("Majority\ncarrier"),_("ve0 (m/s)"),_("vh0 (m/s)"),_("Physical\nmodel"),_("Shape"),_("Material")])
		self.tab.setColumnHidden(5,True)
		self.tab.setColumnHidden(6,True)

		self.tab.horizontalHeader().setFixedHeight(60)
		self.contacts.load()

		if get_mesh().get_zpoints()!=1 or get_mesh().get_xpoints()!=1: 
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

			self.set_row(i,str(c.shape.name),c.position,c.applied_voltage_type,c.applied_voltage,start,width,str(c.contact_resistance_sq),c.shunt_resistance_sq,str(c.np),str(c.charge_type),str(c.ve0),str(c.vh0),str(c.physical_model), c.shape.type,c.shape.optical_material)

			i=i+1

		self.show_hide_cols()

	def __init__(self):
		QWidgetSavePos.__init__(self,"contacts")
		self.setMinimumSize(1200, 400)

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
		self.tab.setColumnCount(14)
		self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)

		self.load()

		self.tab.cellChanged.connect(self.tab_changed)

		self.main_vbox.addWidget(self.tab)


		self.setLayout(self.main_vbox)

		self.epi=get_epi()

		#get_contactsio().changed.connect(self.update)


