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

from gl_base_object import gl_base_object
from gl_scale import project_trianges_m2screen
from gl_scale import gl_scale

from gl import glWidget

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
		data_type="xy"

		if len(input_files)==1:
			data=dat_file()
			data.load(input_files[0])

			data_type=data.type

		three_d=False
		if data_type=="gobj":
			three_d=True

		if data_type=="zxy-d":
			three_d=True

		if three_d==True:
			self.setWindowTitle(_("3D object viewer")+" https://www.gpvdm.com")
			self.setWindowIcon(icon_get("shape"))

			self.plot=glWidget(self)
			self.main_vbox.addWidget(self.plot)
			self.setLayout(self.main_vbox)

			#self.plot.triangle_file=input_files[0]

			self.plot.draw_electrical_mesh=False
			self.plot.view.draw_device=False
			self.plot.enable_draw_ray_mesh=False
			self.plot.enable_draw_light_source=False
			self.plot.enable_draw_rays=False
			self.plot.view.render_photons=False
			if data_type=="zxy-d":
				self.plot.plot_graph=True
				self.plot.graph_data.load(input_files[0])
				self.show()
			if data_type=="gobj":
				self.plot.pre_built_scene=gl_scale.project_base_objects_from_m_2_screen(data.data)
				self.show()
				self.plot.force_redraw()
				#self.plot.render()
				#self.plot.gl_objects_load(ret)
			#print(self.plot.graph_data.data)
				
		elif data_type=="circuit":
			self.setWindowTitle(_("3D object viewer")+" https://www.gpvdm.com")
			self.setWindowIcon(icon_get("shape"))

			self.plot=glWidget(self)
			self.main_vbox.addWidget(self.plot)
			self.setLayout(self.main_vbox)

			self.plot.draw_electrical_mesh=False
			self.plot.view.draw_device=False
			self.plot.enable_draw_ray_mesh=False
			self.plot.enable_draw_light_source=False
			self.plot.enable_draw_rays=False
			self.plot.plot_graph=False
			self.plot.plot_circuit=True
			self.plot.view.render_photons=False
			self.plot.graph_data.load(input_files[0])
			self.show()

		elif data_type=="poly":
			self.setWindowTitle(_("3D object viewer")+" https://www.gpvdm.com")
			self.setWindowIcon(icon_get("shape"))

			self.plot=glWidget(self)
			self.main_vbox.addWidget(self.plot)
			self.setLayout(self.main_vbox)

			#self.plot.triangle_file=input_files[0]

			self.plot.draw_electrical_mesh=False
			self.plot.view.draw_device=False
			self.plot.enable_draw_ray_mesh=True
			self.plot.enable_draw_light_source=False
			self.plot.enable_draw_rays=False
			self.plot.scene_built=True
			self.plot.view.render_photons=False
			data=dat_file()

			if data.load(input_files[0])==True:
				a=gl_base_object()
				a.id=["bing"]
				a.type="open_triangles"
				a.r=data.r
				a.g=data.g
				a.b=data.b
				a.triangles=project_trianges_m2screen(data.data)
				self.plot.gl_objects_add(a)
			self.show()
		else:
			self.shown=True

			self.plot=plot_widget()

			if len(plot_labels)==0:
				for i in range(0,len(input_files)):
					plot_labels.append(os.path.basename(input_files[i]).replace("_","\_"))

			#print plot_labels
			for i in range(0,len(plot_labels)):
				if len(plot_labels[i])>0:
					if plot_labels[i][0]=="\\":
						plot_labels[i]=plot_labels[i][1:]
				plot_labels[i].replace("\\","/")

			self.plot.load_data(input_files)
			self.plot.set_labels(plot_labels)

			self.plot.do_plot()
			self.plot.show()	
		



