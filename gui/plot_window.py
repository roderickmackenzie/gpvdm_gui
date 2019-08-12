# -*- coding: utf-8 -*-
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

## @package plot_window
#  A plot window which uses the plot widget.
#


import os
#import shutil
#from token_lib import tokens
from plot_widget import plot_widget
from PyQt5.QtWidgets import QWidget,QVBoxLayout
from dat_file import dat_file
from icon_lib import icon_get

class plot_window(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		self.main_vbox=QVBoxLayout()
		self.setMinimumSize(800,800)
		self.shown=False

	def destroy(self):
		self.shown=False
		self.window.destroy()

	def callback_destroy(self,widget):
		self.destroy()

	def init(self,input_files,plot_labels,config_file):
		three_d=False

		if len(input_files)==1:
			data=dat_file()
			data.load(input_files[0])

			if data.type=="poly":
				three_d=True

		if three_d==False:
			self.shown=True

			self.plot=plot_widget()
			self.plot.init()

			if len(plot_labels)==0:
				for i in range(0,len(input_files)):
					plot_labels.append(os.path.basename(input_files[i]).replace("_","\_"))

			#print plot_labels
			for i in range(0,len(plot_labels)):
				if len(plot_labels[i])>0:
					if plot_labels[i][0]=="\\":
						plot_labels[i]=plot_labels[i][1:]
				plot_labels[i].replace("\\","/")

			self.plot.set_labels(plot_labels)
			self.plot.load_data(input_files)

			self.plot.do_plot()
			self.plot.show()
		else:
			self.setWindowTitle(_("3D object viewer")+" https://www.gpvdm.com")
			self.setWindowIcon(icon_get("shape"))


			from gl import glWidget
			self.plot=glWidget(self)
			self.main_vbox.addWidget(self.plot)
			self.setLayout(self.main_vbox)

			self.plot.triangle_file=input_files[0]

			self.plot.draw_electrical_mesh=False
			self.plot.enable_draw_device=False
			self.plot.enable_draw_ray_mesh=True
			self.plot.enable_draw_light_source=False
			self.plot.enable_draw_rays=False
			self.show()


