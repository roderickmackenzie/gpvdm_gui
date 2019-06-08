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

## @package snapshot_slider
#  A slider to scroll through simulation snapshots.
#
import os
from tab import tab_class

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QSlider,QHBoxLayout,QLabel,QComboBox
from PyQt5.QtGui import QPainter,QIcon
from PyQt5.QtCore import pyqtSignal

from help import help_window

from dat_file import dat_file
from dat_file_math import dat_file_max_min
from PyQt5.QtCore import QTimer
from icon_lib import icon_get
from util import wrap_text

class snapshot_slider(QWidget):

	changed = pyqtSignal()

	def timer_toggle(self):
		if self.timer==None:
			self.timer=QTimer()
			self.timer.timeout.connect(self.slider_auto_incroment)
			self.timer.start(1)
			self.tb_play.setIcon(icon_get("media-playback-pause"))
		else:
			self.anim_stop()

	def anim_stop(self):
		if self.timer!=None:
			self.timer.stop()
			self.timer=None
			self.tb_play.setIcon(icon_get("media-playback-start"))

	def slider_auto_incroment(self):
		val=self.slider0.value()
		val=val+1
		if val>self.slider0.maximum():
			val=0
		self.slider0.setValue(val)

	def cal_min_max(self):

		self.z_max=-1e40
		self.z_min=1e40
		
		for i in range(0,len(self.dirs)):
			fname=os.path.join(self.dirs[i],self.files_combo.currentText())

			my_data=dat_file()
			if my_data.load(fname) == True:
				#print(z)
				temp_max,temp_min=dat_file_max_min(my_data)

				if temp_max>self.z_max:
					self.z_max=temp_max

				if temp_min<self.z_min:
					self.z_min=temp_min

				if my_data.data_max!=None and my_data.data_min!=None:
					return
		
	def update(self):
		self.dirs=[]
		if os.path.isdir(self.path)==True:
			for name in os.listdir(self.path):
				if name!="." and name!= "..":
					full_path=os.path.join(self.path, name)
					if os.path.isdir(full_path):
						self.dirs.append(name)

		self.dirs.sort(key=int)

		for i in range(0,len(self.dirs)):
			self.dirs[i]=os.path.join(self.path, self.dirs[i])

		self.slider_max=len(self.dirs)-1
		self.slider0.setMaximum(self.slider_max)
		self.update_file_combo()

	def slider0_change(self):
		value = self.slider0.value()
		self.label0.setText(str(value))
		self.changed.emit()

	def get_file_name(self):
		if self.slider_dir_exists()==False:
			return None

		file_path=None
		val=self.slider0.value()

		file_path=os.path.join(self.path,self.dirs[val],self.files_combo.currentText())
		if os.path.isfile(file_path)==False:
			file_path=None

		return file_path

	def set_path(self,path):
		self.path=path
		self.update()
		print("a")
		self.cal_min_max()

		
	def __init__(self):
		QWidget.__init__(self)
		self.dirs=[]
		self.path=""
		self.timer=None

		self.tb_play = QAction(icon_get("media-playback-start"), wrap_text(_("Play"),2), self)
		self.tb_play.triggered.connect(self.timer_toggle)

		self.setWindowTitle(_("Snapshot slider")) 
		
		self.main_vbox = QVBoxLayout()

		self.slider_hbox0= QHBoxLayout()
		self.slider_max=30
		
		self.slider0 = QSlider(Qt.Horizontal)
		self.slider0.setMinimum(0)
		self.slider0.setMaximum(self.slider_max)

		self.slider0.setTickPosition(QSlider.TicksBelow)
		self.slider0.setTickInterval(5)
		self.slider0.valueChanged.connect(self.slider0_change)
		self.slider0.setMinimumSize(300, 80)

		self.slider_hbox0.addWidget(self.slider0)

		self.label0 = QLabel()
		self.label0.setText("")

		self.slider0.setValue(1)

		self.slider_hbox0.addWidget(self.label0)

		self.widget0=QWidget()
		self.widget0.setLayout(self.slider_hbox0)

		self.main_vbox.addWidget(self.widget0)


################
		self.slider_hbox1= QHBoxLayout()
		self.label1 = QLabel()
		self.label1.setText(_("File"))
		self.slider_hbox1.addWidget(self.label1)

		self.files_combo=QComboBox()
		self.slider_hbox1.addWidget(self.files_combo)

		self.files_combo.currentIndexChanged.connect(self.files_combo_changed)

		self.widget1=QWidget()
		self.widget1.setLayout(self.slider_hbox1)

		self.main_vbox.addWidget(self.widget1)

###############

		self.setLayout(self.main_vbox)

	def slider_dir_exists(self):
		if self.slider0.value()==-1:
			return False
		if self.slider0.value()>=len(self.dirs):
			return False
		
		return True

	def update_file_combo(self):
		if self.slider_dir_exists()==False:
			return False
		self.files_combo.blockSignals(True)
		self.files_combo.clear()
		path=os.path.join(self.path,self.dirs[self.slider0.value()])

		if os.path.isdir(path)==True:
			for name in os.listdir(path):
				full_path=os.path.join(path, name)
				if os.path.isfile(full_path):
					if name!="snapshot_info.dat":
						self.files_combo.addItem(name)

		all_items  = [self.files_combo.itemText(i) for i in range(self.files_combo.count())]

		for i in range(0,len(all_items)):
			if all_items[i] == "Jn.dat":
				self.files_combo.setCurrentIndex(i)
		self.files_combo.blockSignals(False)
		return True

		
	def files_combo_changed(self):
		self.cal_min_max()
		self.changed.emit()


