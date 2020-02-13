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
	from gl_scale import project_m2screen_x
	from gl_scale import project_m2screen_y
	from gl_scale import project_m2screen_z

except:
	pass

from PyQt5.QtCore import QTimer
from inp import inp

from epitaxy import get_epi
from mesh import get_mesh
from gl_list import gl_base_object
from gl_lib import gl_obj_id_extract_starts_with

class gl_mesh():
	def draw_mesh(self):
		x=[]
		y=[]
		z=[]
		epi=get_epi()
		device_start=epi.get_device_start()
		mesh=get_mesh()

		y,temp=mesh.y.calculate_points()
		x,temp=mesh.x.calculate_points()
		z,temp=mesh.z.calculate_points()

		old_layer=-1
		components=[]
		component=""

		for i in range(0,len(y)):
			y[i]=y[i]+device_start
			layer=epi.get_layer_by_cordinate(y[i])
			if old_layer!=layer:
				old_layer=layer
				f=inp()
				f.load(epi.layers[layer].electrical_file+".inp")
				component=f.get_token("#electrical_component")
				if component=="resistance":
					component="resistor"
			components.append(component)

		x=project_m2screen_x(x)
		y=project_m2screen_y(y)
		z=project_m2screen_z(z)



		set_color(1.0,0.0,0.0,"mesh",alpha=0.5)

		glLineWidth(3)
		if mesh.y.circuit_model==False:
			self.drift_diffusion_mesh()
		else:
			self.circuit_mesh()

	def circuit_mesh(self):
		x=[]
		y=[]
		z=[]
		epi=get_epi()
		device_start=epi.get_device_start()
		mesh=get_mesh()

		y,temp=mesh.y.calculate_points()
		x,temp=mesh.x.calculate_points()
		z,temp=mesh.z.calculate_points()

		old_layer=-1
		components=[]
		component=""

		for i in range(0,len(y)):
			y[i]=y[i]+device_start
			layer=epi.get_layer_by_cordinate(y[i])
			if old_layer!=layer:
				old_layer=layer
				f=inp()
				f.load(epi.layers[layer].electrical_file+".inp")
				component=f.get_token("#electrical_component")
				if component=="resistance":
					component="resistor"
			components.append(component)

		x=project_m2screen_x(x)
		y=project_m2screen_y(y)
		z=project_m2screen_z(z)

		set_color(1.0,0.0,0.0,"mesh",alpha=0.5)

		glLineWidth(3)

		mesh=get_mesh()
		mask=mesh.build_device_shadow()

		for zi in range(0,len(z)):
			for xi in range(0,len(x)):
				for yi in range(0,len(y)):
					name="mesh:"+str(xi)+":"+str(yi)+":"+str(zi)

					block_y=False
					block_x=False
					block_z=False

					if mask[zi][xi][yi]==False:
						block_y=True

					if xi!=len(x)-1:
						if mask[zi][xi+1][yi]==False:
							block_x=True

					if mask[zi][xi][yi]==False:
						block_x=True
						block_z=True						

					if yi!=len(y)-1 and block_y==False:
						a=gl_base_object()
						a.id=["electrical_mesh"]
						a.type=components[yi]
						a.x=x[xi]
						a.y=y[yi]
						a.z=z[zi]
						a.dx=0.0
						a.dy=y[yi+1]-y[yi]
						a.dz=0.0
						a.r=1.0
						a.g=0.0
						a.b=0.0
						a.alpha=1.0
						self.gl_objects_add(a)


					if xi!=len(x)-1 and block_x==False:
						a=gl_base_object()
						a.id=["electrical_mesh"]
						a.type="resistor"
						a.x=x[xi]
						a.y=y[yi]
						a.z=z[zi]
						a.dx=x[xi+1]-x[xi]
						a.dy=0.0
						a.dz=0.0
						a.r=1.0
						a.g=0.0
						a.b=0.0
						a.alpha=1.0
						self.gl_objects_add(a)

					if zi!=len(z)-1 and block_z==False:
						a=gl_base_object()
						a.id=["electrical_mesh"]
						a.type="resistor"
						a.x=x[xi]
						a.y=y[yi]
						a.z=z[zi]
						a.dx=0.0
						a.dy=0.0
						a.dz=z[zi+1]-z[zi]
						a.r=1.0
						a.g=0.0
						a.b=0.0
						a.alpha=1.0
						self.gl_objects_add(a)

	def drift_diffusion_mesh(self):
		x=[]
		y=[]
		z=[]
		epi=get_epi()
		device_start=epi.get_device_start()
		mesh=get_mesh()

		y,temp=mesh.y.calculate_points()
		x,temp=mesh.x.calculate_points()
		z,temp=mesh.z.calculate_points()

		for i in range(0,len(y)):
			y[i]=y[i]+device_start

		x=project_m2screen_x(x)
		y=project_m2screen_y(y)
		z=project_m2screen_z(z)

		set_color(1.0,0.0,0.0,"mesh",alpha=0.5)

		glLineWidth(3)

		for zi in range(0,len(z)):
			for xi in range(0,len(x)):
				for yi in range(0,len(y)):
					name="mesh:"+str(xi)+":"+str(yi)+":"+str(zi)
					if yi==self.dump_energy_slice_ypos and xi==self.dump_energy_slice_xpos and zi==self.dump_energy_slice_zpos:
						a=gl_base_object()
						a.id=[name]
						a.type="ball"
						a.x=x[xi]
						a.y=y[yi]
						a.z=z[zi]
						a.dx=0.08
						a.r=0.0
						a.g=1.0
						a.b=0.0
						self.gl_objects_add(a)
					elif xi==self.dump_1d_slice_xpos and zi==self.dump_1d_slice_zpos:
						a=gl_base_object()
						a.id=[name]
						a.type="ball"
						a.x=x[xi]
						a.y=y[yi]
						a.z=z[zi]
						a.dx=0.05
						a.r=0.0
						a.g=0.0
						a.b=1.0
						self.gl_objects_add(a)
					else:
						a=gl_base_object()
						a.id=[name]
						a.type="ball"
						a.x=x[xi]
						a.y=y[yi]
						a.z=z[zi]
						a.dx=0.05
						if self.dump_verbose_electrical_solver_results==False:
							a.alpha=0.5
						else:
							a.alpha=0.9
						a.r=1.0
						a.g=0.0
						a.b=0.0
						self.gl_objects_add(a)

					if yi!=len(y)-1:
						a=gl_base_object()
						a.id=["electrical_mesh"]
						a.type="line"
						a.x=x[xi]
						a.y=y[yi]
						a.z=z[zi]
						a.dx=0.0
						a.dy=y[yi+1]-y[yi]
						a.dz=0.0
						a.r=1.0
						a.g=0.0
						a.b=0.0
						self.gl_objects_add(a)


					if xi!=len(x)-1:
						a=gl_base_object()
						a.id=["electrical_mesh"]
						a.type="line"
						a.x=x[xi]
						a.y=y[yi]
						a.z=z[zi]
						a.dx=x[xi+1]-x[xi]
						a.dy=0.0
						a.dz=0.0
						a.r=1.0
						a.g=0.0
						a.b=0.0
						self.gl_objects_add(a)

					if zi!=len(z)-1:
						a=gl_base_object()
						a.id=["electrical_mesh"]
						a.type="line"
						a.x=x[xi]
						a.y=y[yi]
						a.z=z[zi]
						a.dx=0.0
						a.dy=0.0
						a.dz=z[zi+1]-z[zi]
						a.r=1.0
						a.g=0.0
						a.b=0.0
						self.gl_objects_add(a)


	def mesh_menu(self,event):
		view_menu = QMenu(self)
		

		menu = QMenu(self)

		view=menu.addMenu(_("Dump"))

		if self.dump_energy_slice_xpos==-1:
			action=view.addAction(_("Dump slice in energy space"))
		else:
			action=view.addAction(_("Don't dump slice in energy space"))

		action.triggered.connect(self.menu_energy_slice_dump)

		if self.dump_1d_slice_xpos==-1:
			action=view.addAction(_("Dump 1D slices"))
		else:
			action=view.addAction(_("Don't dump 1D slice"))

		action.triggered.connect(self.menu_1d_slice_dump)

		if self.dump_verbose_electrical_solver_results==False:
			action=view.addAction(_("Set verbose electrical solver dumping"))
		else:
			action=view.addAction(_("Unset verbose electrical solver dumping"))

		action.triggered.connect(self.menu_dump_verbose_electrical_solver_results)



		menu.exec_(event.globalPos())

	def menu_energy_slice_dump(self):
		s=gl_obj_id_extract_starts_with(self.obj,"mesh").split(":")
		x=int(s[1])
		y=int(s[2])
		z=int(s[3])

		if self.dump_energy_slice_xpos==x and self.dump_energy_slice_ypos==y and self.dump_energy_slice_zpos==z:
			self.dump_energy_slice_xpos=-1
			self.dump_energy_slice_ypos=-1
			self.dump_energy_slice_zpos=-1
		else:
			self.dump_energy_slice_xpos=x
			self.dump_energy_slice_ypos=y
			self.dump_energy_slice_zpos=z

		mesh=get_mesh()
		f=inp()
		f.load("dump.inp")
		f.replace("#dump_energy_slice_xpos",str(x))
		f.replace("#dump_energy_slice_ypos",str(len(mesh.y.points)-1-y))
		f.replace("#dump_energy_slice_zpos",str(z))
		f.save()

		self.gl_objects_remove_regex("mesh")
		self.draw_mesh()

		self.do_draw()

	def menu_1d_slice_dump(self):
		s=gl_obj_id_extract_starts_with(self.obj,"mesh").split(":")
		x=int(s[1])
		y=int(s[2])
		z=int(s[3])

		if self.dump_1d_slice_xpos==x and self.dump_1d_slice_zpos==z:
			self.dump_1d_slice_xpos=-1
			self.dump_1d_slice_zpos=-1
		else:
			self.dump_1d_slice_xpos=x
			self.dump_1d_slice_zpos=z

		f=inp()
		f.load("dump.inp")
		f.replace("#dump_1d_slice_xpos",str(self.dump_1d_slice_xpos))
		f.replace("#dump_1d_slice_zpos",str(self.dump_1d_slice_zpos))
		f.save()

		self.gl_objects_remove_regex("mesh")
		self.draw_mesh()

		self.do_draw()

	def menu_dump_verbose_electrical_solver_results(self):
		self.dump_verbose_electrical_solver_results = not self.dump_verbose_electrical_solver_results
		f=inp()
		f.load("dump.inp")
		f.replace("#dump_verbose_electrical_solver_results",str(self.dump_verbose_electrical_solver_results))
		f.save()

		self.gl_objects_remove_regex("mesh")
		self.draw_mesh()

		self.do_draw()
