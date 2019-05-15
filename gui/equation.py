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

## @package equation
#  An equation editor, not sure if this is needed any more.
#

import os
import sys
from scan_item import scan_item_add
from gui_util import dlg_get_text
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
from PyQt5.QtWidgets import QWidget,QDialog,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QTableWidget,QAbstractItemView
from PyQt5.QtGui import QPainter,QIcon

#windows
from gui_util import tab_add
from gui_util import tab_move_down
from gui_util import tab_move_up
from gui_util import tab_remove
from gui_util import tab_get_value
from gui_util import tab_set_value
from open_save_dlg import save_as_filter

from dat_file import dat_file
from dat_file import dat_file_read

from error_dlg import error_dlg

from ref import ref_window
from ref import get_ref_text
from ref_io import ref
from tb_item_mat_file import tb_item_mat_file

from import_data import import_data
from fit_poly import fit_poly

from gui_util import tab_get_selected
#window

from code_ctrl import enable_betafeatures
from solar_main import solar_main
from help import help_window

mesh_articles = []

class equation(QWidget):


	def save_data(self):

		out_text=[]
		out_text.append("#points")
		out_text.append(str(self.points))
		out_text.append("#equations")
		out_text.append(str(self.tab.rowCount()))

		for i in range(0,self.tab.rowCount()):
			out_text.append("#start"+str(i))
			out_text.append(str(tab_get_value(self.tab,i, 0)))

			out_text.append("#stop"+str(i))
			out_text.append(str(tab_get_value(self.tab,i, 1)))

			out_text.append("#equation"+str(i))
			out_text.append(str(tab_get_value(self.tab,i, 2)))

		out_text.append("#ver")
		out_text.append("1.0")
		out_text.append("#end")
		
		dump=""
		for item in out_text:
			dump=dump+item+"\n"

		dump=dump.rstrip("\n")

		f=open(os.path.join(self.path,self.file_name), mode='wb')
		lines = f.write(str.encode(dump))
		f.close()


	def callback_add_section(self):

		tab_add(self.tab,["100e-9","1000e-9",self.default_value])

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
		self.fig.clf()
		self.fig.subplots_adjust(bottom=0.2)
		self.fig.subplots_adjust(left=0.1)
		self.ax1 = self.fig.add_subplot(111)
		self.ax1.ticklabel_format(useOffset=False)

		self.ax1.set_ylabel(self.ylabel)
		if self.x!=None:
			x_nm= [x * 1e9 for x in self.x]
			frequency, = self.ax1.plot(x_nm,self.y, 'ro-', linewidth=3 ,alpha=1.0)

		if os.path.isfile(os.path.join(self.path,self.exp_file))==True:

			dat_file_read(self.data,os.path.join(self.path,self.exp_file))
			title=get_ref_text(os.path.join(self.path,self.exp_file), html=False)

			if title!=None:
				self.fig.suptitle(title)

			x_nm= [x * 1e9 for x in self.data.y_scale]
			frequency, = self.ax1.plot(x_nm,self.data.data[0][0], 'bo-', linewidth=3 ,alpha=1.0)

		self.ax1.set_xlabel(_("Wavelength")+" (nm)")

	def save_image(self,file_name):
		self.fig.savefig(file_name)

	def callback_save(self):
		file_name = save_as_filter(self,"png (*.png)")
		if file_name !=None:
			self.save_image(file_name)

	def callback_help(self):
		webbrowser.open("https://www.gpvdm.com/man/index.html")

	def load_data(self):
		self.tab.clear()
		self.tab.setColumnCount(3)
		self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tab.setHorizontalHeaderLabels([_("start")+" (m)", _("stop")+" (m)", _("Python Equation")])
		self.tab.setColumnWidth(2, 500)
		lines=[]
		pos=0
		lines=inp_load_file(os.path.join(self.path,self.file_name))
		if lines!=False:
			token,self.points,pos=inp_read_next_item(lines,pos)		
			token,equations,pos=inp_read_next_item(lines,pos)
			equations=int(equations)
			self.points=int(self.points)
			for i in range(0, equations):
				token,start,pos=inp_read_next_item(lines,pos)
				token,stop,pos=inp_read_next_item(lines,pos)
				token,equation,pos=inp_read_next_item(lines,pos)
				tab_add(self.tab,[str(start),str(stop),str(equation)])

	def build_mesh(self):
		self.x=[]
		self.y=[]

		data_min=100.0
		if self.tab.rowCount()!=0:
			for i in range(0,self.tab.rowCount()):
				val=float(tab_get_value(self.tab,i, 0))
				if val<data_min:
					data_min=val

			#find max
			data_max=0.0
			for i in range(0,self.tab.rowCount()):
				val=float(tab_get_value(self.tab,i, 1))
				if val>data_max:
					data_max=val

			w=data_min
			dx=(data_max-data_min)/(float(self.points))

			for i in range(0,self.points):
				val=0.0
				for ii in range(0,self.tab.rowCount()):
					range_min=float(tab_get_value(self.tab,ii, 0))
					range_max=float(tab_get_value(self.tab,ii, 1))
					command=tab_get_value(self.tab,ii, 2)
					try:
						equ=eval(command)
					except:
						print(sys.exc_info())
						error_dlg(self,_("You've made a mistake in the equation, use w for wavelength. " + command))
						equ=-1
						return
					
					if w>=range_min and w <=range_max:
						val=val+equ
				if val<0.0:
					val=1.0
					
				self.x.append(w)
				self.y.append(val)
				w=w+dx

			f_name=os.path.join(self.path,self.out_file)

			try:
				a = open(f_name, "w")
				for i in range(0,len(self.y)):
					a.write(str(self.x[i])+" "+str(self.y[i])+"\n")
				a.close()
			except IOError:
				print("Could not read file:", f_name)


	def on_cell_edited(self, x,y):
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def set_default_value(self,value):
		self.default_value=value

	def callback_import(self):
		output_file=os.path.join(self.path,self.exp_file)
		config_file=os.path.join(self.path,self.exp_file+"import.inp")
		self.im=import_data(output_file,config_file)
		self.im.run()
		self.update()

	def callback_solar_spectra(self):
		if self.solar_spectrum_window==None:
			self.solar_spectrum_window=solar_main(self.path)
			self.solar_spectrum_window.update.connect(self.update)

			#self.solar_spectrum_window.changed.connect(self.mode.update)

		help_window().help_set_help(["weather-few-clouds.png",_("<big><b>Solar spectrum editor</b></big><br> Use this tool to generate custom solar spectra.")])
		if self.solar_spectrum_window.isVisible()==True:
			self.solar_spectrum_window.hide()
		else:
			self.solar_spectrum_window.show()


	def set_ylabel(self,value):
		self.ylabel=value

	def callback_ref(self):
		self.ref_window=ref_window(os.path.join(self.path,self.exp_file))
		self.ref_window.show()
	
	def callback_fit(self):
		data=tab_get_selected(self.tab)
		if data==False:
			error_dlg(self,_("No items selected"))
			return

		d=fit_poly(float(data[0]),float(data[1]),self.data)
		d.run()
		if d.ret_math!=None:
			a=self.tab.selectionModel().selectedRows()

			if len(a)>0:
				a=a[0].row()
			tab_set_value(self.tab,a,2,d.ret_math)
			print(d.ret_math)

	def init(self):
		self.data=dat_file()
		self.fig = Figure(figsize=(5,4), dpi=100)
		self.canvas = FigureCanvas(self.fig)
		self.canvas.figure.patch.set_facecolor('white')

		self.main_vbox = QVBoxLayout()

		if self.toolbar==False:
			self.toolbar=toolbar=QToolBar()
			self.toolbar.setIconSize(QSize(48, 48))
			self.main_vbox.addWidget(self.toolbar)

		self.tb_save = QAction(icon_get("document-save-as"), _("Save image"), self)
		self.tb_save.triggered.connect(self.callback_save)
		self.toolbar.addAction(self.tb_save)

		self.tb_ref= QAction(icon_get("ref"), _("Insert reference information"), self)
		self.tb_ref.triggered.connect(self.callback_ref)
		self.toolbar.addAction(self.tb_ref)

		self.import_data= QAction(icon_get("import"), _("Import data"), self)
		self.import_data.triggered.connect(self.callback_import)
		self.toolbar.addAction(self.import_data)

		if self.show_solar_spectra==True:
			if enable_betafeatures()==True:
				self.solar_spectra= QAction(icon_get("weather-few-clouds"), _("Solar spectra"), self)
				self.solar_spectra.triggered.connect(self.callback_solar_spectra)
				self.toolbar.addAction(self.solar_spectra)

		self.file_select=tb_item_mat_file(self.path,self.token)
		#self.file_select.changed.connect(self.callback_sun)
		self.toolbar.addWidget(self.file_select)
		




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

		self.tb_play = QAction(icon_get("media-playback-start"), _("Calculate"), self)
		self.tb_play.triggered.connect(self.callback_play)
		toolbar2.addAction(self.tb_play)

		self.tb_fit = QAction(icon_get("fit"), _("Fit data"), self)
		self.tb_fit.triggered.connect(self.callback_fit)
		toolbar2.addAction(self.tb_fit)

		self.main_vbox.addWidget(toolbar2)

		self.tab = QTableWidget()
		self.tab.resizeColumnsToContents()

		self.tab.verticalHeader().setVisible(False)

		self.main_vbox.addWidget(self.tab)

		self.setLayout(self.main_vbox)

		self.load_data()


		self.build_mesh()
		self.draw_graph()

		self.tab.cellChanged.connect(self.on_cell_edited)
	
	def callback_play(self):
		self.build_mesh()
		self.draw_graph()
		self.fig.canvas.draw()

	def __init__(self,path,file_name,out_file,exp_file,token,toolbar=False):
		self.x=None
		self.y=None
		QWidget.__init__(self)
		self.points=4000
		self.default_value="3.0"
		self.path=path
		self.file_name=file_name
		self.token=token
		self.out_file=out_file
		self.exp_file=exp_file
		self.show_solar_spectra=False
		self.solar_spectrum_window=None
		self.toolbar=toolbar



