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


## @package tab_homo
#  A tab to draw the analytical HOMO/LUMO.
#

import os
from inp import inp_isfile
from inp import inp_load_file
from inp import inp_save
from numpy import *
from scan_item import scan_item_add
from tab_base import tab_base

from open_save_dlg import save_as_image

#matplotlib
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QTableWidget,QAbstractItemView, QMenuBar,QGroupBox,QHBoxLayout
from PyQt5.QtGui import QPainter,QIcon

from PyQt5.QtCore import pyqtSignal

from icon_lib import icon_get

from gui_util import tab_add
from gui_util import tab_remove
from gui_util import tab_get_value

from ribbon_complex_dos import ribbon_complex_dos 

class equation_editor(QGroupBox):

	changed = pyqtSignal()

	def load(self):
		lines=[]
		self.tab.clear()
		self.tab.setHorizontalHeaderLabels([_("Function"), _("Enabled"), _("a"), _("b"), _("c")])

		lines=inp_load_file(self.file_name)
		pos=0

		while True:
			if lines[pos]=="#end":
				break
			if lines[pos]=="#ver":
				break

			tag=lines[pos]
			pos=pos+1	#skip hash tag

			function=lines[pos]	#read label
			pos=pos+1

			tag=lines[pos]
			pos=pos+1	#skip hash tag

			enabled=lines[pos] 	#read value
			pos=pos+1

			tag=lines[pos]
			pos=pos+1	#skip hash tag

			a=lines[pos] 	#read value
			pos=pos+1

			tag=lines[pos]
			pos=pos+1	#skip hash tag

			b=lines[pos] 	#read value
			pos=pos+1

			tag=lines[pos]
			pos=pos+1	#skip hash tag
			c=lines[pos] 	#read value
			pos=pos+1

			tab_add(self.tab,[ str(function), str(enabled), str(a), str(b), str(c)])

	def __init__(self,file_name,name):
		QGroupBox.__init__(self)
		self.file_name=file_name
		self.name=name
		self.setTitle(name)
		self.setStyleSheet("QGroupBox {  border: 1px solid gray;}")
		vbox=QVBoxLayout()
		self.setLayout(vbox)

		toolbar=QToolBar()
		toolbar.setIconSize(QSize(48, 48))

		add = QAction(icon_get("list-add",size=16),  _("Add "+self.name+" mesh layer"), self)
		add.triggered.connect(self.add_item_clicked)
		toolbar.addAction(add)

		remove = QAction(icon_get("list-remove",size=16),  _("Remove "+self.name+" mesh layer"), self)
		remove.triggered.connect(self.on_remove_click)
		toolbar.addAction(remove)

		vbox.addWidget(toolbar)

		self.tab = QTableWidget()

		self.tab.resizeColumnsToContents()

		self.tab.verticalHeader().setVisible(False)

		self.tab.clear()
		self.tab.setColumnCount(5)
		self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)

		self.load()

		self.tab.cellChanged.connect(self.tab_changed)

		vbox.addWidget(self.tab)

	def tab_changed(self):
		self.save()
		self.changed.emit()
		
	def add_item_clicked(self):
		tab_add(self.tab,[ "exp", "true", "a", "b", "c"])
		self.save()
		self.changed.emit()

	def on_remove_click(self):
		tab_remove(self.tab)
		self.save()
		self.changed.emit()
		
	def save(self):
		lines=[]
		for i in range(0,self.tab.rowCount()):
			lines.append("#function_"+str(i))
			lines.append(tab_get_value(self.tab,i, 0))
			lines.append("#function_enable_"+str(i))
			lines.append(tab_get_value(self.tab,i, 1))
			lines.append("#function_a_"+str(i))
			lines.append(tab_get_value(self.tab,i, 2))
			lines.append("#function_b_"+str(i))
			lines.append(tab_get_value(self.tab,i, 3))
			lines.append("#function_c_"+str(i))
			lines.append(tab_get_value(self.tab,i, 4))
		lines.append("#ver")
		lines.append("#1.0")
		lines.append("#end")
		inp_save(self.file_name,lines)

		
############
class dos_editor(QWidget,tab_base):

	def update_graph(self):
		self.LUMO_fig.clf()
		self.draw_graph_lumo()
		self.LUMO_fig.canvas.draw()

	def draw_graph_lumo(self):

		ax1 = self.LUMO_fig.add_subplot(111)

		ax1.set_ylabel('$DoS (m^{-3} eV^{-1})$')
		ax1.set_xlabel('Energy (eV)')

		#ax2 = ax1.twinx()
		#x_pos=0.0
		#layer=0
		color =['r','g','b','y','o','r','g','b','y','o']
		ax1.set_yscale('log')
		ax1.set_ylim(ymin=1e17,ymax=1e28)
		pos=0
		Eg=2.0
		ax1.set_xlim([0,-Eg])
		x = linspace(0, -Eg, num=40)
		for i in range(0,self.lumo.tab.rowCount()):
			try:
				a=float(tab_get_value(self.lumo.tab,i,2))
				b=float(tab_get_value(self.lumo.tab,i,3))
				c=float(tab_get_value(self.lumo.tab,i,4))
			except:
				a=0.0
				b=0.0
				c=0.0
				
			if tab_get_value(self.lumo.tab,i,0)=="exp":
				y = a*exp(x/b)
				line, = ax1.plot(x,y , '-', linewidth=3)
				
			if tab_get_value(self.lumo.tab,i,0)=="gaus":
				y = a*exp(-pow(((b+x)/(sqrt(2.0)*c*1.0)),2.0))
				line, = ax1.plot(x,y , color[pos], linewidth=3)
				pos=pos+1

		pos=0

		x_homo = linspace(-Eg, 0, num=40)
		for i in range(0,self.homo.tab.rowCount()):
			try:
				a=float(tab_get_value(self.homo.tab,i,2))
				b=float(tab_get_value(self.homo.tab,i,3))
				c=float(tab_get_value(self.homo.tab,i,4))
			except:
				a=0.0
				b=0.0
				c=0.0
				
			if tab_get_value(self.homo.tab,i,0)=="exp":
				y = a*exp(x/b)
				line, = ax1.plot(x_homo,y , '-', linewidth=3)
			if tab_get_value(self.homo.tab,i,0)=="gaus":
				y = a*exp(-pow(((b+x)/(sqrt(2.0)*c*1.0)),2.0))

				line, = ax1.plot(x_homo,y , color[pos], linewidth=3)
				pos=pos+1
 

	def callback_save(self):
		file_name=save_as_image(self)
		if file_name!=False:
			self.canvas_lumo.figure.savefig(file_name)

	def __init__(self):
		QWidget.__init__(self)

		self.setWindowTitle(_("Complex Density of states editor - gpvdm"))
		self.setWindowIcon(icon_get("electrical"))
		self.setMinimumSize(1200,500)

		edit_boxes=QWidget()
		vbox=QVBoxLayout()

		self.lumo=equation_editor("lumo0.inp","LUMO")
		vbox.addWidget(self.lumo)
		
		self.homo=equation_editor("homo0.inp","HOMO")
		vbox.addWidget(self.homo)
		
		
		edit_boxes.setLayout(vbox)

		hbox=QHBoxLayout()


		self.LUMO_fig = Figure(figsize=(5,4), dpi=100)


		self.draw_graph_lumo()
		self.canvas_lumo = FigureCanvas(self.LUMO_fig)
		self.canvas_lumo.figure.patch.set_facecolor('white')

		self.LUMO_fig.tight_layout(pad=0.5)

		hbox.addWidget(self.canvas_lumo)


		hbox.addWidget(edit_boxes)
		
		self.ribbon=ribbon_complex_dos()
		self.ribbon.tb_save.triggered.connect(self.callback_save)

		self.main_layout_widget=QWidget()
		self.main_layout_widget.setLayout(hbox)

		self.big_vbox=QVBoxLayout()

		self.big_vbox.addWidget(self.ribbon)
		self.big_vbox.addWidget(self.main_layout_widget)

		self.setLayout(self.big_vbox)
		
		self.lumo.changed.connect(self.update_graph)
		self.homo.changed.connect(self.update_graph)
		
	

