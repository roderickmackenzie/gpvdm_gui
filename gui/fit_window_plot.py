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

## @package fit_window_plot
#  Widget to plot the results of the fit.
#

import os
from numpy import *
from scan_item import scan_item_add
from plot_widget import plot_widget
import i18n
_ = i18n.language.gettext


#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QTabWidget
from PyQt5.QtGui import QPainter,QIcon

#from matplotlib_toolbar import NavigationToolbar
#matplotlib
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from open_save_dlg import save_as_jpg

from cal_path import get_sim_path

class fit_window_plot(QWidget):
	lines=[]
	edit_list=[]

	line_number=[]
	save_file_name=""

	file_name=""
	name=""
	visible=1

	def update(self):
		self.draw_graph()

	def draw_graph(self):

		self.plot_widget.set_labels(["Simulation","Experiment","Delta"])
		error_sim=os.path.join(get_sim_path(),"fit_error_sim"+str(self.index)+".dat")
		error_exp=os.path.join(get_sim_path(),"fit_error_exp"+str(self.index)+".dat")
		delta=os.path.join(get_sim_path(),"fit_error_delta"+str(self.index)+".dat")
		oplot_file=os.path.join(get_sim_path(),"fit_error_sim"+str(self.index)+".oplot")
		self.plot_widget.load_data([error_sim,error_exp,delta])

		self.plot_widget.do_plot()


	def save_image(self,file_name):
		self.fig.savefig(file_name)

	def callback_save(self, widget, data=None):
		file_name = save_as_jpg(self)
		if file_name !=None:
			self.save_image(file_name)

	def __init__(self,index):
		QWidget.__init__(self)
		self.vbox=QVBoxLayout()
		self.index=index

		self.plot_widget=plot_widget(enable_toolbar=False)
		self.vbox.addWidget(self.plot_widget)
		
		self.setLayout(self.vbox)
		
		self.draw_graph()
