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

## @package icon_lib
#  An icon cache.
#

import sys
import os
from cal_path import get_icon_path
from win_lin import running_on_linux
from inp import inp_get_token_value
from util import str2bool
from inp import inp_load_file
from cal_path import get_inp_file_path

try:
	from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction,QApplication,QTableWidgetItem,QComboBox, QMessageBox, QDialog, QDialogButtonBox, QFileDialog
	from PyQt5.QtWidgets import QGraphicsScene,QListWidgetItem,QListView,QLineEdit,QWidget,QHBoxLayout,QPushButton
	from PyQt5.QtWidgets import QFileDialog
	from PyQt5.uic import loadUi
	from PyQt5.QtGui import QPixmap
	from PyQt5.QtCore import QSize, Qt, QTimer
	from PyQt5.QtCore import QPersistentModelIndex
	from QComboBoxLang import QComboBoxLang
	from PyQt5.QtGui import QIcon
except:
	pass


icon_db=[]

use_theme=None

def save_db():
	global icon_db
	f=open('icons.inp', 'w')
	for i in range(0,len(icon_db)):
		f.write(icon_db[i][0]+'\n'+icon_db[i][1]+'\n')

	f.write('#end\n')
	f.close()

def icon_find(token):
	global icon_db
	for i in range(0,len(icon_db)):
		if icon_db[i][0]==token:
			return icon_db[i][2]

	return False

def add_to_db(name,save=False):
	global icon_db
	found=False
	for i in range(0,len(icon_db)):
		if icon_db[i][1]==name:
			found=True
			break
	if found==False:
		icon_db.append(["#"+name,name])

		if save==True:
			save_db()

def QIcon_load(name,size=-1,save=True):
	global use_theme
	if use_theme==None:
		use_theme=inp_get_token_value(os.path.join(os.getcwd(),"config.inp") , "#gui_use_icon_theme")
		if use_theme==None:
			use_theme=False
		else:
			use_theme=str2bool(use_theme)

	if running_on_linux()==True and use_theme==True:
		image=QIcon()
		if image.hasThemeIcon(name)==True:
			return image.fromTheme(name)

	icon_path=get_icon_path(name,size=size)
	if os.path.isfile(icon_path)==True:
		ret=QIcon(icon_path)
	else:
		ret=False
	return ret

def icons_load():
	lines=inp_load_file(os.path.join(get_inp_file_path(),"icons.inp"),archive="base.gpvdm")
	if lines==False:
		lines=inp_load_file(os.path.join(get_inp_file_path(),"icons.inp"),archive="sim.gpvdm")

	pos=0
	global icon_db
	while(1):
		file_type=lines[pos]
		if file_type=="#end":
			break
		token=file_type
		pos=pos+1
		icon_name=lines[pos]
		pos=pos+1
		icon=QIcon_load(icon_name,save=False)
		if icon!=False:
			icon_db.append([token[1:],icon_name,icon])
		else:
			print("Icon not found:"+icon_name)
			sys.exit(0)

def icon_get(token,size=-1):

	if token!=".png" and token.endswith(".png")==True:
		token=token[:-4]

	if size!=-1:
		return QIcon_load(token,size=size)

	icon=icon_find(token)
	
	if icon!=False:
		return icon
	else:
		return False
