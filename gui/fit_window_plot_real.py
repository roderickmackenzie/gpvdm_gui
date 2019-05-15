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

## @package fit_window_plot_real
#  Another fit plotting window?
#

import os
#from numpy import *
from cal_path import get_image_file_path
from util import read_xyz_data

import i18n
_ = i18n.language.gettext

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QMenuBar,QStatusBar, QMenu, QTableWidget, QAbstractItemView
from PyQt5.QtGui import QPainter,QIcon,QCursor

#matplotlib
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from open_save_dlg import open_as_filter

mesh_articles = []

from icon_lib import icon_get
from cal_path import get_sim_path

class fit_window_plot_real(QWidget):
	lines=[]
	edit_list=[]

	line_number=[]
	save_file_name=""

	file_name=""
	name=""
	visible=1

	def update(self):
		self.draw_graph()
		self.fig.canvas.draw()

	def draw_graph(self):

		x=[]
		y=[]
		z=[]
		if read_xyz_data(x,y,z,os.path.join(get_sim_path(),"fit_data"+str(self.index)+".inp"))==True:
			self.fig.clf()
			self.fig.subplots_adjust(bottom=0.2)
			self.fig.subplots_adjust(left=0.1)
			self.ax1 = self.fig.add_subplot(111)
			self.ax1.ticklabel_format(useOffset=False)

			self.ax1.set_xlabel(_("x"))
			self.ax1.set_ylabel(_("y"))

			voltage, = self.ax1.plot(x,y, 'ro-', linewidth=3 ,alpha=1.0)


	def save_image(self,file_name):
		self.fig.savefig(file_name)

	def callback_save(self):
		file_name=save_as_filter(parent,"png (*.png);;jpg (*.jpg)")

		if file_name!=None:
			self.save_image(file_name)

	def __init__(self,index):
		QWidget.__init__(self)

		self.index=index
		self.fig = Figure(figsize=(5,4), dpi=100)
		self.ax1=None
		self.show_key=True
		
		self.hbox=QVBoxLayout()
		self.edit_list=[]
		self.line_number=[]

		self.list=[]
		print("index=",index)


		canvas = FigureCanvas(self.fig)  # a gtk.DrawingArea
		#canvas.set_background('white')
		#canvas.set_facecolor('white')
		canvas.figure.patch.set_facecolor('white')
		#canvas.set_size_request(500, 150)

		#canvas.set_size_request(700,400)

		self.draw_graph()

		#toolbar=QToolBar()
		#toolbar.setIconSize(QSize(48, 48))

		#self.tb_save = QAction(icon_get("document-save-as"), _("Save graph"), self)
		#self.tb_save.triggered.connect(self.callback_save)
		#toolbar.addAction(self.tb_save)


		#nav_bar=NavigationToolbar(canvas,self)
		#toolbar.addWidget(nav_bar)

		#self.hbox.addWidget(toolbar)
		
		self.hbox.addWidget(canvas)

		self.setLayout(self.hbox)
