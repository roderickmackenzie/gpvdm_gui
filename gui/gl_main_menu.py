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

## @package gl_view_point
#  The gl_view_point class for the OpenGL display.
#

import sys
from math import fabs

try:
	from OpenGL.GL import *
	from OpenGL.GLU import *
	from PyQt5 import QtOpenGL
	from PyQt5.QtOpenGL import QGLWidget
	from gl_color import set_color
	from gl_lib import val_to_rgb
	from PyQt5.QtWidgets import QMenu
	from gl_scale import scale_get_xmul
	from gl_scale import scale_get_ymul
	from gl_scale import scale_get_zmul
	from gl_scale import scale_get_start_x
	from gl_scale import scale_get_start_z

except:
	pass

from PyQt5.QtCore import QTimer
from inp import inp_update_token_value
from gpvdm_open import gpvdm_open
from cal_path import get_sim_path
from PyQt5.QtWidgets import QDialog
from dat_file_math import dat_file_max_min


class gl_main_menu():
	def menu(self,event):
		view_menu = QMenu(self)
		

		menu = QMenu(self)

		action=menu.addAction(_("Save image"))
		action.triggered.connect(self.save_image_as)


		view=menu.addMenu(_("View"))

		action=view.addAction(_("Mesh view"))
		action.triggered.connect(self.menu_toggle_view)

		action=view.addAction(_("Device view"))
		action.triggered.connect(self.menu_toggle_view)

		plot=menu.addMenu(_("Plot"))

		action=plot.addAction(_("Open"))
		action.triggered.connect(self.menu_plot_open)


		show=menu.addMenu(_("Show"))
		action=show.addAction(_("Grid"))
		action.triggered.connect(self.menu_toggle_grid)

		action=show.addAction(_("Backgroud color"))
		action.triggered.connect(self.menu_background_color)

		action=show.addAction(_("Stars"))
		action.triggered.connect(self.menu_stars)

		action=show.addAction(_("Device"))
		action.triggered.connect(self.menu_draw_device)


		#menu.exec_(self.emailbtn.mapToGlobal(QtCore.QPoint(0,0)))
		menu.exec_(event.globalPos())


	def save_image_as(self):
		#self.random_device()
		#return
		ret=save_as_filter(self,"png (*.png)")
		#print(ret)
		if ret!=False:
			self.grabFrameBuffer().save(ret)
			#gl_save_save(ret)

	def menu_background_color(self):
		col = QColorDialog.getColor(Qt.white, self)
		if col.isValid():
			self.view.bg_color=[col.red()/255,col.green()/255,col.blue()/255]
			self.force_redraw()

	def menu_toggle_view(self):
		self.draw_electrical_mesh=not self.draw_electrical_mesh
		self.force_redraw()

	def menu_toggle_grid(self):
		self.view.render_grid=not self.view.render_grid
		self.force_redraw()

	def menu_draw_device(self):
		self.enable_draw_device = not self.enable_draw_device
		self.force_redraw()

	def menu_stars(self):
		if self.view.stars_distance==60:
			self.view.stars_distance=0.0
		else:
			self.view.stars_distance=60

		self.force_redraw()

	def menu_plot_open(self):
		dialog=gpvdm_open(get_sim_path(),show_inp_files=False,act_as_browser=False)
		ret=dialog.exec_()
		if ret==QDialog.Accepted:
			self.graph_path=dialog.get_filename()
			if self.graph_data.load(self.graph_path)==True:
				#print(self.graph_path)
				self.graph_data.data_max,self.graph_data.data_min=dat_file_max_min(self.graph_data)
				#print(self.graph_z_max,self.graph_z_min)

