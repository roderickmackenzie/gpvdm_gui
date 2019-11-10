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
from PyQt5.QtWidgets import QTextEdit, QAction
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QPushButton,QToolBar, QVBoxLayout, QTableWidget,QAbstractItemView, QTableWidgetItem, QComboBox

from QComboBoxLang import QComboBoxLang
from QComboBoxShape import QComboBoxShape
from icon_lib import icon_get

from gpvdm_select import gpvdm_select
from gtkswitch import gtkswitch
from leftright import leftright
from gpvdm_select_material import gpvdm_select_material
from PyQt5.QtCore import QPersistentModelIndex


class gpvdm_tab(QTableWidget):

	def __init__(self,toolbar=None):
		QTableWidget.__init__(self)
		self.toolbar=toolbar
		if self.toolbar!=None:
			self.toolbar.setIconSize(QSize(32, 32))
			self.tb_add = QAction(icon_get("list-add"), _("Add"), self)
			self.toolbar.addAction(self.tb_add)

			self.tb_remove = QAction(icon_get("list-remove"), _("Remove"), self)
			self.toolbar.addAction(self.tb_remove)

			self.tb_down= QAction(icon_get("go-down"), _("Move down"), self)
			self.toolbar.addAction(self.tb_down)

			self.tb_up= QAction(icon_get("go-up"), _("Move up"), self)
			self.toolbar.addAction(self.tb_up)


	def set_value(self,y,x,value):
		if type(self.cellWidget(y, x))==QComboBox:
			self.cellWidget(y, x).blockSignals(True)
			self.cellWidget(y, x).setCurrentIndex(self.cellWidget(y, x).findText(value))
			self.cellWidget(y, x).blockSignals(False)
		elif type(self.cellWidget(y, x))==QComboBoxLang:
			self.cellWidget(y, x).blockSignals(True)
			self.cellWidget(y, x).setValue_using_english(value)
			self.cellWidget(y, x).blockSignals(False)
		elif type(self.cellWidget(y, x))==QComboBoxShape:
			self.cellWidget(y, x).blockSignals(True)
			self.cellWidget(y, x).setValue(value)
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

	def move_down(self):
		ret=-1

		if self.rowCount()==0:
			return -1

		self.blockSignals(True)
		a=self.selectionModel().selectedRows()

		if len(a)>0:
			a=a[0].row()

			b=a+1
			if b>self.rowCount()-1:
				return -1

			ret=a

			av=[]
			for i in range(0,self.columnCount()):
				av.append(str(self.get_value(a,i)))

			bv=[]
			for i in range(0,self.columnCount()):
				bv.append(str(self.get_value(b,i)))

			for i in range(0,self.columnCount()):
				self.set_value(b,i,str(av[i]))
				self.set_value(a,i,str(bv[i]))

			self.selectRow(b)
			self.blockSignals(False)
			return ret
		else:
			return -1

	def get_value(self,y,x):
		if type(self.cellWidget(y, x))==QComboBox:
			return self.cellWidget(y, x).currentText()
		elif type(self.cellWidget(y, x))==QComboBoxLang:
			return self.cellWidget(y, x).currentText_english()
		elif type(self.cellWidget(y,x))==gpvdm_select:
			return self.cellWidget(y, x).text()
		elif type(self.cellWidget(y,x))==leftright:
			return self.cellWidget(y, x).get_value()
		elif type(self.cellWidget(y,x))==gtkswitch:
			return self.cellWidget(y, x).get_value()
		elif type(self.cellWidget(y,x))==gpvdm_select_material:
			return self.cellWidget(y, x).text()
		elif type(self.cellWidget(y, x))==QComboBoxShape:
			return self.cellWidget(y, x).currentText()
		else:
			return self.item(y, x).text()


	def add(self,data):
		self.blockSignals(True)
		index = self.selectionModel().selectedRows()

		if len(index)>0:
			pos=index[0].row()+1
		else:
			pos = self.rowCount()

		if self.columnCount()==len(data):
			self.insertRow(pos)
			for i in range(0,len(data)):
				self.setItem(pos,i,QTableWidgetItem(data[i]))

		if len(data)>self.columnCount():
			rows=int(len(data)/self.columnCount())
			for ii in range(0,rows):
				self.insertRow(pos)
				for i in range(0,self.columnCount()):
					self.setItem(pos,i,QTableWidgetItem(data[ii*tab.columnCount()+i]))
				pos=pos+1
					
		self.blockSignals(False)

	def insert_row(self):
		self.blockSignals(True)
		index = self.selectionModel().selectedRows()

		if len(index)>0:
			pos=index[0].row()+1
		else:
			pos = self.rowCount()

		self.insertRow(pos)
		self.blockSignals(False)
		return pos

	def move_up(self):
		ret=-1
		if self.rowCount()==0:
			return ret

		self.blockSignals(True)
		a=self.selectionModel().selectedRows()

		if len(a)==1:
			a=a[0].row()	

			b=a-1
			if b<0:
				return -1
				#b=tab.rowCount()-1

			ret=a

			av=[]
			for i in range(0,self.columnCount()):
				av.append(str(self.get_value(a,i)))

			bv=[]
			for i in range(0,self.columnCount()):
				bv.append(str(self.get_value(b,i)))

			for i in range(0,self.columnCount()):
				self.set_value(b,i,str(av[i]))
				self.set_value(a,i,str(bv[i]))

			self.selectRow(b)
			self.blockSignals(False)
			return ret

		else:
			return ret

	def get_selected(self):
		a=self.selectionModel().selectedRows()

		if len(a)<=0:
			return False

		ret=[]
		
		for ii in range(0,len(a)):
			y=a[ii].row()
			for i in range(0,self.columnCount()):
				ret.append(str(self.get_value(y,i)))

		return ret

	def remove(self):
		self.blockSignals(True)
		ret=[]
		index = self.selectionModel().selectedRows()
		if len(index)>0:
			for i in range(0,len(index)):
				ret.append(index[i].row())

		index_list = []                                                          
		for model_index in self.selectionModel().selectedRows():       
			index = QPersistentModelIndex(model_index)         
			index_list.append(index)                                             

		for index in index_list:                                      
			self.removeRow(index.row()) 
			
		self.blockSignals(False)

		print("index>>",ret)
		return ret
