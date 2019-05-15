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

## @package fxmesh
#  fx domain mesh editor
#

import os
from scan_item import scan_item_add
from gui_util import dlg_get_text
from inp import inp_save
import webbrowser
from util import fx_with_units
from icon_lib import icon_get
from scan_item import scan_remove_file

import i18n
_ = i18n.language.gettext

#inp
from inp import inp_search_token_value
from inp import inp_load_file
from inp import inp_read_next_item

#matplotlib
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QTableWidget,QAbstractItemView
from PyQt5.QtGui import QPainter,QIcon

#windows
from gui_util import tab_add
from gui_util import tab_move_down
from gui_util import tab_move_up
from gui_util import tab_remove
from gui_util import tab_get_value
from open_save_dlg import save_as_jpg

from colors import get_color
from cal_path import get_sim_path

mesh_articles = []

class tab_fxmesh(QWidget):
	lines=[]
	edit_list=[]

	line_number=[]
	save_file_name=""

	file_name=""
	name=""
	visible=1

	def save_data(self):
		file_name="fxmesh"+str(self.index)+".inp"
		scan_remove_file(file_name)

		out_text=[]

		for i in range(0,self.tab.rowCount()):
			out_text.append("#fx_segment"+str(i)+"_start")
			scan_item_add(file_name,out_text[len(out_text)-1],_("Part ")+str(i)+" "+_("start"),1)
			out_text.append(str(tab_get_value(self.tab,i, 0)))

			out_text.append("#fx_segment"+str(i)+"_stop")
			scan_item_add(file_name,out_text[len(out_text)-1],_("Part ")+str(i)+" "+_("stop"),1)
			out_text.append(str(tab_get_value(self.tab,i, 1)))

			out_text.append("#fx_segment"+str(i)+"_points")
			scan_item_add(file_name,out_text[len(out_text)-1],_("Part ")+str(i)+" "+_("points"),1)
			out_text.append(str(tab_get_value(self.tab,i, 2)))

			out_text.append("#fx_segment"+str(i)+"_mul")
			scan_item_add(file_name,out_text[len(out_text)-1],_("Part ")+str(i)+" "+_("mul"),1)
			out_text.append(str(tab_get_value(self.tab,i, 3)))

		out_text.append("#ver")
		out_text.append("1.1")
		out_text.append("#end")

		inp_save(file_name,out_text)
		self.update_scan_tokens()

	def update_scan_tokens(self):
		file_name="fxmesh"+str(self.index)+".inp"
		scan_remove_file(file_name)

		for i in range(0,len(self.list)):
			scan_item_add(file_name,"#fx_segment"+str(i)+"_start",_("Part ")+str(i)+" "+_("start"),1)
			scan_item_add(file_name,"#fx_segment"+str(i)+"_stop",_("Part ")+str(i)+" "+_("stop"),1)
			scan_item_add(file_name,"#fx_segment"+str(i)+"_points",_("Part ")+str(i)+" "+_("points"),1)
			scan_item_add(file_name,"#fx_segment"+str(i)+"_mul",_("Part ")+str(i)+" "+_("mul"),1)


	def callback_add_section(self):
		tab_add(self.tab,["0.0","0.0","0.0","0.0"])

		self.build_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def callback_remove_item(self):
		tab_remove(self.tab)

		self.build_mesh()

		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def callback_move_down(self):

		tab_move_down(self.tab)

		self.build_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def callback_move_up(self):

		tab_move_up(self.tab)

		self.build_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def update(self):
		self.build_mesh()
		self.draw_graph()
		self.fig.canvas.draw()

	def draw_graph(self):
		my_max=self.fx[0][0]
		my_min=self.fx[0][0]

		for i in range(0,len(self.fx)):
			for ii in range(0,len(self.fx[i])):
				if self.fx[i][ii]>my_max:
					my_max=self.fx[i][ii]

				if self.fx[i][ii]<my_min:
					my_min=self.fx[i][ii]
	
		if (len(self.fx)>0):
			mul,unit=fx_with_units(float(my_max-my_min))
		else:
			mul=1.0
			unit="Hz"

		fx=[]

		for i in range(0,len(self.fx)):
			local_fx=[]
			for ii in range(0,len(self.fx[i])):
				local_fx.append(self.fx[i][ii]*mul)
			fx.append(local_fx)

		self.fig.clf()
		self.fig.subplots_adjust(bottom=0.2)
		self.fig.subplots_adjust(left=0.1)
		self.ax1 = self.fig.add_subplot(111)
		self.ax1.ticklabel_format(useOffset=False)

		self.ax1.set_ylabel(_("Magnitude")+" ("+_("Volts")+" )")

		for i in range(0,len(fx)):
			frequency, = self.ax1.plot(fx[i],self.mag[i], 'ro-', color=get_color(i),linewidth=3 ,alpha=1.0)
		
		self.ax1.set_xlabel(_("Frequency")+" ("+unit+")")


	def load_data(self):
		self.tab.clear()
		self.tab.setColumnCount(4)
		self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tab.setHorizontalHeaderLabels([_("Frequency start"),_("Frequency stop"), _("points"), _("Multiply")])
		self.tab.setColumnWidth(0, 200)
		self.tab.setColumnWidth(1, 200)

		lines=[]
		self.start_fx=0.0

		file_name="fxmesh"+str(self.index)+".inp"

		lines=inp_load_file(os.path.join(get_sim_path(),file_name))
		if lines!=False:
			if inp_search_token_value(lines, "#ver")=="1.1":
				pos=0

				while(1):
					token,start,pos=inp_read_next_item(lines,pos)
					if token=="#ver" or token=="#end":
						break
					token,stop,pos=inp_read_next_item(lines,pos)
					token,points,pos=inp_read_next_item(lines,pos)
					token,mul,pos=inp_read_next_item(lines,pos)

					tab_add(self.tab,[str(start),str(stop),str(points),str(mul)])

				return True
			else:
				print("file "+file_name+"wrong version")
				exit("")
				return False
		else:
			print("file "+file_name+" not found")
			return False

		return False

	def build_mesh(self):
		self.mag=[]
		self.fx=[]

		for i in range(0,self.tab.rowCount()):
			local_mag=[]
			local_fx=[]
			start=float(tab_get_value(self.tab,i, 0))
			pos=start
			stop=float(tab_get_value(self.tab,i, 1))
			points=float(tab_get_value(self.tab,i, 2))
			mul=float(tab_get_value(self.tab,i, 3))

			if stop!=0.0 and points!=0.0 and mul!=0.0:
				dfx=(stop-start)/points
				while(pos<stop):
					local_fx.append(pos)
					local_mag.append(1.0)
					pos=pos+dfx

					dfx=dfx*mul
			self.mag.append(local_mag)
			self.fx.append(local_fx)
			local_mag=[]
			local_fx=[]



		#self.statusbar.push(0, str(len(self.fx))+_(" mesh points"))

	def on_cell_edited(self, x,y):
		print("Cell edited",x,y)
		self.build_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def save_image(self):
		file_name = save_as_jpg(self)
		if file_name !=None:
			self.fig.savefig(file_name)

	def __init__(self,index):
		QWidget.__init__(self)

		self.index=index
		self.ax1=None
		self.show_key=True
		self.edit_list=[]
		self.line_number=[]
		self.list=[]

		self.fig = Figure(figsize=(5,4), dpi=100)
		self.canvas = FigureCanvas(self.fig)
		self.canvas.figure.patch.set_facecolor('white')

		gui_pos=0

		print("index=",index)

		self.main_vbox = QVBoxLayout()

		self.main_vbox.addWidget(self.canvas)




		#toolbar 2

		toolbar2=QToolBar()
		toolbar2.setIconSize(QSize(32, 32))

		self.tb_add = QAction(icon_get("list-add"), _("Add section"), self)
		self.tb_add.triggered.connect(self.callback_add_section)
		toolbar2.addAction(self.tb_add)

		self.tb_remove = QAction(icon_get("list-remove"), _("Delete section"), self)
		self.tb_remove.triggered.connect(self.callback_remove_item)
		toolbar2.addAction(self.tb_remove)

		self.tb_move = QAction(icon_get("go-down"), _("Move down"), self)
		self.tb_move.triggered.connect(self.callback_move_down)
		toolbar2.addAction(self.tb_move)

		self.tb_move_up = QAction(icon_get("go-up"), _("Move up"), self)
		self.tb_move_up.triggered.connect(self.callback_move_up)
		toolbar2.addAction(self.tb_move_up)

		self.main_vbox.addWidget(toolbar2)

		self.tab = QTableWidget()
		self.tab.resizeColumnsToContents()

		self.tab.verticalHeader().setVisible(False)

		self.load_data()
		self.build_mesh()
		self.draw_graph()

		self.update_scan_tokens()

		self.tab.cellChanged.connect(self.on_cell_edited)

		self.main_vbox.addWidget(self.tab)

		self.setLayout(self.main_vbox)

		return




