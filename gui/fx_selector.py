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

## @package fx_selector
#  Select which wavelenght to display
#

import os
from inp import inp_update_token_value
from inp import inp_get_token_value
import zipfile
import glob
from tab import tab_class

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QSystemTrayIcon,QMenu, QComboBox, QMenuBar, QLabel
from PyQt5.QtGui import QIcon

from cal_path import get_sim_path

class fx_selector(QWidget):

	def __init__(self):
		QWidget.__init__(self)
		self.dump_dir=os.path.join(get_sim_path(),"light_dump")

		self.layout=QVBoxLayout()
		label=QLabel(_("Wavelengths")+":")
		self.layout.addWidget(label)

		self.cb = QComboBox()
		self.layout.addWidget(self.cb)
		self.setLayout(self.layout)
		self.show()
		self.start=""
		self.end=""
		self.show_all=False

	def get_text(self):
		out=self.cb.currentText()
		out=out.split(" ")[0]
		return out

	def file_name_set_start(self,start):
		self.start=start

	def file_name_set_end(self,end):
		self.end=end
		
	def find_modes(self,path):
		result = []
		lines=[]
		dump_dir=os.path.join(get_sim_path(),"light_dump")
		path=os.path.join(dump_dir,"wavelengths.dat")

		if os.path.isfile(path)==True:

			f = open(path, "r")
			lines = f.readlines()
			f.close()
			
			for l in range(0, len(lines)):
				txt=lines[l].rstrip()
				if txt!="":
					result.append(txt)

		
		if os.path.isdir(dump_dir)==True:
			files=os.listdir(dump_dir)
			for f in files:
				if f.startswith("light_ray_"):
					f=f[:-4]
					f=f[10:]
					#print(f)
					result.append(f)

		return result

	def update(self):
		self.cb.blockSignals(True)

		thefiles=self.find_modes(self.dump_dir)
		thefiles.sort()

		if len(thefiles)==0:
			self.setEnabled(False)
		else:
			self.setEnabled(True)

		self.cb.clear()
		if self.show_all==True:
			self.cb.addItem("all")
		for i in range(0, len(thefiles)):
			path=os.path.join(self.dump_dir,self.start+str(thefiles[i])+self.end)
			#print(path)
			if os.path.isfile(path):
				self.cb.addItem(str(thefiles[i])+" nm")
		self.cb.setCurrentIndex(0)
		self.cb.blockSignals(False)

