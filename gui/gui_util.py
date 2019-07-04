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
	from PyQt5.QtCore import QPersistentModelIndex
	from QComboBoxLang import QComboBoxLang
	from PyQt5.QtGui import QIcon

	from gpvdm_select import gpvdm_select
	from gtkswitch import gtkswitch
	from leftright import leftright
	from gpvdm_select_material import gpvdm_select_material

#windows
from cal_path import get_ui_path

from icon_lib import icon_get


from util import str2bool

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


def tab_get_value(tab,y,x):
	if type(tab.cellWidget(y, x))==QComboBox:
		return tab.cellWidget(y, x).currentText()
	elif type(tab.cellWidget(y, x))==QComboBoxLang:
		return tab.cellWidget(y, x).currentText_english()
	elif type(tab.cellWidget(y,x))==gpvdm_select:
		return tab.cellWidget(y, x).text()
	elif type(tab.cellWidget(y,x))==leftright:
		return tab.cellWidget(y, x).get_value()
	elif type(tab.cellWidget(y,x))==gtkswitch:
		return tab.cellWidget(y, x).get_value()
	elif type(tab.cellWidget(y,x))==gpvdm_select_material:
		return tab.cellWidget(y, x).text()
	else:
		return tab.item(y, x).text()


def tab_get_selected(tab):
	a=tab.selectionModel().selectedRows()

	if len(a)<=0:
		return False

	ret=[]
	
	for ii in range(0,len(a)):
		y=a[ii].row()
		for i in range(0,tab.columnCount()):
			ret.append(str(tab_get_value(tab,y,i)))

	return ret


def tab_move_up(tab):
	ret=-1
	if tab.rowCount()==0:
		return ret

	tab.blockSignals(True)
	a=tab.selectionModel().selectedRows()

	if len(a)==1:
		a=a[0].row()	

		b=a-1
		if b<0:
			return -1
			#b=tab.rowCount()-1

		ret=a

		av=[]
		for i in range(0,tab.columnCount()):
			av.append(str(tab_get_value(tab,a,i)))

		bv=[]
		for i in range(0,tab.columnCount()):
			bv.append(str(tab_get_value(tab,b,i)))

		for i in range(0,tab.columnCount()):
			tab.set_value(b,i,str(av[i]))
			tab.set_value(a,i,str(bv[i]))

		tab.selectRow(b)
		tab.blockSignals(False)
		return ret

	else:
		return ret
	
def tab_insert_row(tab):
	tab.blockSignals(True)
	index = tab.selectionModel().selectedRows()

	if len(index)>0:
		pos=index[0].row()+1
	else:
		pos = tab.rowCount()

	tab.insertRow(pos)
	tab.blockSignals(False)
	return pos


def tab_remove(tab):
	tab.blockSignals(True)
	ret=-1
	index = tab.selectionModel().selectedRows()

	if len(index)>0:
	#	for i in range(0,len(index)):
		ret=index[0].row()
	#		tab.removeRow(pos)
	index_list = []                                                          
	for model_index in tab.selectionModel().selectedRows():       
		index = QPersistentModelIndex(model_index)         
		index_list.append(index)                                             

	for index in index_list:                                      
		tab.removeRow(index.row()) 
		
	tab.blockSignals(False)

	return ret

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
