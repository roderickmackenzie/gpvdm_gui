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

## @package gl_lib_ray
#  Library to draw ray
#

import sys

try:
	from OpenGL.GL import *
	from OpenGL.GLU import *
	from PyQt5 import QtOpenGL
	from PyQt5.QtOpenGL import QGLWidget
	open_gl_ok=True
except:
	print("opengl error from gl_lib",sys.exc_info()[0])
	
import random
import os
from math import sqrt
from math import fabs
from lines import lines_read
from util import wavelength_to_rgb
from epitaxy import epitaxy_get_device_start
from util import isnumber
from gl_scale import project_m2screen_x
from gl_scale import project_m2screen_y
from gl_scale import project_m2screen_z
from gl_scale import project_trianges_m2screen
from gl_scale import scale_trianges_m2screen

from gl_scale import scale_get_device_y
from gl_scale import scale_get_device_x
from gl_scale import scale_get_device_z

from gl_list import gl_base_object

from dat_file import dat_file
from epitaxy import epitaxy_get_epi
from epitaxy import get_epi

from gl_scale import scale_get_xmul
from gl_scale import scale_get_ymul
from gl_scale import scale_get_zmul
from triangle_io import triangles_mul_vec

from triangle import vec

from mesh import mesh_get_zlen
from mesh import mesh_get_xlen

from mesh import mesh_get_xmesh
from mesh import mesh_get_ymesh
from mesh import mesh_get_zmesh

from triangle_io import triangles_flip_in_box

class gl_contacts():

	def draw_contacts(self):
		epi=get_epi()
		y_mesh=mesh_get_ymesh()
		x_mesh=mesh_get_xmesh()
		z_mesh=mesh_get_zmesh()

		self.gl_objects_remove_regex("contact")

		for c in epi.contacts.contacts:

			if c.position=="left":
				if len(x_mesh.points)>1:
					sticking_out_bit=0.2
					a=gl_base_object()
					a.id=["contact"]
					a.type="solid_and_mesh"
					a.x=project_m2screen_x(0)-sticking_out_bit
					a.y=project_m2screen_y(c.shape.y0)
					a.z=project_m2screen_z(0)
					a.dx=1.0
					a.dy=scale_get_ymul()*c.shape.dy
	
					a.dz=scale_get_device_z()
					a.r=epi.layers[0].r
					a.g=epi.layers[0].g
					a.b=epi.layers[0].b
					a.alpha=1.0
					my_vec=vec()
					my_vec.x=sticking_out_bit/scale_get_xmul()+c.ingress
					my_vec.y=c.shape.dy
					my_vec.z=mesh_get_zlen()

					if c.shape.triangles!=None:
						a.triangles=scale_trianges_m2screen(triangles_mul_vec(triangles_flip_in_box(c.shape.triangles.data),my_vec))

						self.gl_objects_add(a)

			elif c.position=="top":
				if epi.layers[0].name!="air":
					box=vec()
					if len(x_mesh.points)==1 and len(z_mesh.points)==1:
						xstart=project_m2screen_x(0)
						box.x=mesh_get_xlen()
					else:
						xstart=project_m2screen_x(c.shape.x0)
						box.x=c.shape.dx

					box.y=epi.layers[0].dy+c.ingress
					box.z=mesh_get_zlen()

					a=gl_base_object()
					a.id=["layer:"+epi.layers[0].name,"contact"]
					a.type="solid_and_mesh"
					a.x=xstart
					a.y=project_m2screen_y(epi.get_layer_start(0))
					a.z=project_m2screen_z(0)
					a.dx=scale_get_xmul()*box.x
					a.dy=scale_get_ymul()*box.y
					a.dz=scale_get_device_z()
					a.r=epi.layers[0].r
					a.g=epi.layers[0].g
					a.b=epi.layers[0].b
					a.alpha=1.0

					if c.shape.triangles!=None:
						a.triangles=scale_trianges_m2screen(triangles_mul_vec(triangles_flip_in_box(c.shape.triangles.data),box))
						self.gl_objects_add(a)

			elif c.position=="bottom":
				box=vec()
				if len(x_mesh.points)==1 and len(z_mesh.points)==1:
					xstart=project_m2screen_x(0)
					box.x=mesh_get_xlen()
				else:
					xstart=project_m2screen_x(c.shape.x0)
					box.x=c.shape.dx

				box.y=epi.layers[len(epi.layers)-1].dy+c.ingress 
				box.z=mesh_get_zlen()

				a=gl_base_object()
				a.id=["layer:"+epi.layers[len(epi.layers)-1].name,"contact"]
				a.type="solid_and_mesh"
				a.x=xstart
				a.y=project_m2screen_y(epi.get_layer_start(len(epi.layers)-1))
				a.z=project_m2screen_z(0)

				a.dx=scale_get_xmul()*box.x
				a.dy=scale_get_ymul()*box.y
				a.dz=scale_get_device_z()

				a.r=epi.layers[len(epi.layers)-1].r
				a.g=epi.layers[len(epi.layers)-1].g
				a.b=epi.layers[len(epi.layers)-1].b

				a.alpha=1.0
				my_vec=vec()
				my_vec.x=c.shape.dx
				my_vec.y=epi.layers[len(epi.layers)-1].dy
				my_vec.z=mesh_get_zlen()

				a.triangles=scale_trianges_m2screen(triangles_mul_vec(triangles_flip_in_box(c.shape.triangles.data),box))

				self.gl_objects_add(a)

