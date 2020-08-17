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
	from gl_lib import val_to_rgb
	from PyQt5.QtWidgets import QMenu
	from gl_scale import gl_scale

except:
	pass

from PyQt5.QtCore import QTimer
from inp import inp

from epitaxy import get_epi
from mesh import get_mesh
from gl_base_object import gl_base_object
from gl_scale import scale_get_xmul
from gl_scale import scale_get_ymul
from gl_scale import scale_get_zmul

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

		x=gl_scale.project_m2screen_x(x)
		y=gl_scale.project_m2screen_y(y)
		z=gl_scale.project_m2screen_z(z)

		glLineWidth(3)
		if mesh.y.circuit_model==False:
			self.drift_diffusion_mesh()
		else:
			self.circuit_mesh()

	def curciut_mesh_add_links(self,z):
		epi=get_epi()
		mesh=get_mesh()
		for zi in range(0,len(z)):

			for x_sub_mesh_index in range(0,len(mesh.x.layers)):

				xl=mesh.x.layers[x_sub_mesh_index]
				if xl.points==0:			#if there is a gap in the mesh
					if x_sub_mesh_index!=0 and x_sub_mesh_index!=len(mesh.x.layers)-1:		#get left and right points to the gap
						xl_l=mesh.x.layers[x_sub_mesh_index-1]
						xl_r=mesh.x.layers[x_sub_mesh_index+1]

						x0=xl_l.mesh[-1]
						x1=xl_r.mesh[0]							#look for a shape which fills the gap
						
						shapes=epi.get_shapes_between_x(x0,x1)
						for s in shapes:
							if s.shape_electrical!="none":
								f=inp()
								f.load(s.shape_electrical+".inp")
								component=f.get_token("#electrical_component")
								nl=epi.find_layer_by_id(s.id)
								y0=epi.layers[nl].start
								if component=="link":
									a=gl_base_object()
									a.id=["electrical_mesh"]
									a.type="line"
									a.xyz.x=gl_scale.project_m2screen_x(x0)
									a.xyz.y=gl_scale.project_m2screen_y(y0+s.dy)
									a.xyz.z=z[zi]
									a.dxyz.x=(x1-x0)*scale_get_xmul()
									a.dxyz.y=s.dy*scale_get_ymul()*0.9
									a.dxyz.z=0.0
									a.r=1.0
									a.g=0.0
									a.b=0.0
									a.alpha=1.0
									self.gl_objects_add(a)
									#print(">>>>>>>",component,,x1,y0+s.y0,y0+s.y0+s.dy)

					#print(s.name)
					#sys.exit(0)

	def circuit_mesh(self):
		x=[]
		y=[]
		z=[]
		epi=get_epi()
		mesh=get_mesh()

		y,temp=mesh.y.calculate_points()
		x,temp=mesh.x.calculate_points()
		z,temp=mesh.z.calculate_points()

		old_layer=-1
		components=[]
		component=""

		for l in epi.layers:
			f=inp()
			f.load(l.electrical_file+".inp")
			component=f.get_token("#electrical_component")
			if component=="resistance":
				component="resistor"
			if component=="resistor":
				components.append("resistor")
				components.append("resistor")

			if component=="diode":
				components.append("resistor")
				components.append("diode")

		x=gl_scale.project_m2screen_x(x)
		y=gl_scale.project_m2screen_y(y)
		z=gl_scale.project_m2screen_z(z)

		glLineWidth(3)

		mask=mesh.build_device_shadow()
		
		for zi in range(0,len(z)):
			xi=0
			for x_sub_mesh_index in range(0,len(mesh.x.layers)):
				#print(len(xl.mesh))
				xl=mesh.x.layers[x_sub_mesh_index]

				for x_point in range(0,len(xl.mesh)):
					mid_point=0

					for yi in range(0,len(y)):
						name="mesh:"+str(xi)+":"+str(yi)+":"+str(zi)

						block_y=False
						block_x=False
						block_z=False

						#layer=epi.get_layer_by_cordinate(y[yi])
						#l=epi.layers[layer]

						if x_point==len(xl.mesh)-1:		#if we are at the end of the submesh
							if x_sub_mesh_index!=len(mesh.x.layers)-1:
								if mesh.x.layers[x_sub_mesh_index+1].points==0:
									block_x=True

						if mask[zi][xi][yi]==False:
							block_y=True

						if xi!=len(x)-1:
							if mask[zi][xi+1][yi]==False:
								block_x=True

						if yi!=len(y)-1:
							if mask[zi][xi][yi+1]==False:
								block_y=True

						if mask[zi][xi][yi]==False:
							block_x=True
							block_z=True						

						if mid_point==0:
							block_x=True

						if yi!=len(y)-1 and block_y==False:
							a=gl_base_object()
							a.id=["electrical_mesh"]
							a.type=components[yi]
							a.xyz.x=x[xi]
							a.xyz.y=y[yi]
							a.xyz.z=z[zi]
							a.dxyz.x=0.0
							a.dxyz.y=y[yi+1]-y[yi]
							a.dxyz.z=0.0
							a.r=1.0
							a.g=0.0
							a.b=0.0
							a.alpha=1.0
							self.gl_objects_add(a)


						if xi!=len(x)-1 and block_x==False:
							#print(yi,y[yi],mid_point,block_x)

							a=gl_base_object()
							a.id=["electrical_mesh"]
							a.type="resistor"
							a.xyz.x=x[xi]
							a.xyz.y=y[yi]
							a.xyz.z=z[zi]
							a.dxyz.x=x[xi+1]-x[xi]
							a.dxyz.y=0.0
							a.dxyz.z=0.0
							a.r=1.0
							a.g=0.0
							a.b=0.0
							a.alpha=1.0
							self.gl_objects_add(a)

						if zi!=len(z)-1 and block_z==False:
							a=gl_base_object()
							a.id=["electrical_mesh"]
							a.type="resistor"
							a.xyz.x=x[xi]
							a.xyz.y=y[yi]
							a.xyz.z=z[zi]
							a.dxyz.x=0.0
							a.dxyz.y=0.0
							a.dxyz.z=z[zi+1]-z[zi]
							a.r=1.0
							a.g=0.0
							a.b=0.0
							a.alpha=1.0
							self.gl_objects_add(a)

						mid_point=mid_point+1
						if mid_point==2:
							mid_point=0

					xi=xi+1

		self.curciut_mesh_add_links(z)

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

		x=gl_scale.project_m2screen_x(x)
		y=gl_scale.project_m2screen_y(y)
		z=gl_scale.project_m2screen_z(z)


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
		obj=self.gl_objects_get_first_selected()
		if obj!=None:
			s=obj.id_starts_with("mesh").split(":")

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
		obj=self.gl_objects_get_first_selected()
		if obj!=None:
			s=obj.id_starts_with("mesh").split(":")

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

	def project_object_through_electrical_mesh(self,o):
		mesh=get_mesh()
		mesh_with_gaps=False
		for l in mesh.x.layers:
			if l.points==0:
				mesh_with_gaps=True
				break 

		if mesh_with_gaps==False:
			self.gl_objects_add(o)
		else:
			for l in mesh.x.layers:
				if l.points!=0:
					new_obj=gl_base_object()
					new_obj.copy(o)
					#print(layer,l.start,l.end-l.start)
					new_obj.xyz.x=gl_scale.project_m2screen_x(l.start)
					new_obj.dxyz.x=(l.end-l.start)*scale_get_xmul()
					#print(layer,o.xyz.x,o.dxyz.x)
					self.gl_objects_add(new_obj)

