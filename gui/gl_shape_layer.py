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

## @package gl_lib
#  general backend for the OpenGL viewer.
#

import sys
from gl_save import gl_save_list
from gl_save import gl_save_add

try:
	from OpenGL.GL import *
	from OpenGL.GLU import *
	from PyQt5 import QtOpenGL
	from PyQt5.QtOpenGL import QGLWidget
	from gl_color import set_color
	from gl_shapes import pyrmid
	open_gl_ok=True
except:
	print("opengl error from gl_lib",sys.exc_info()[0])

import random
import numpy as np
from math import pi,acos,sin,cos

from gl_scale import scale_get_xmul
from gl_scale import scale_get_ymul
from gl_scale import scale_get_zmul

from gl_list import gl_base_object
from triangle import vec
from triangle_io import triangles_mul_vec
from triangle_io import triangles_print
from triangle_io import triangles_add_vec
from gl_scale import project_trianges_m2screen
from triangle_io import triangles_flip
					
class shape_layer():
	def shape_layer(self,epi_layer,shape_list,y_padding=0.0, name="name"):
		self.gl_objects_remove_regex(name)
		for s in shape_list:
			#print(">>>>",s.name)
			for x in range(0,s.shape_nx):
				for y in range(0,s.shape_ny):
					for z in range(0,s.shape_nz):
						if s.shape_enabled==True:
							pos=vec()
							if s.shape_flip_y==True:
								pos.x=(s.x0+(s.dx+s.dx_padding)*x)
								pos.y=epi_layer.end-(s.y0+(s.dy+s.dy_padding)*y)
								pos.z=(s.z0+(s.dz+s.dz_padding)*z)
							else:
								pos.x=(s.x0+(s.dx+s.dx_padding)*x)
								pos.y=(s.y0+(s.dy+s.dy_padding)*y)+epi_layer.start
								pos.z=(s.z0+(s.dz+s.dz_padding)*z)

							a=gl_base_object()
							a.id=[name]
							a.type="solid_and_mesh"
							a.x=pos.x
							a.y=pos.y
							a.z=pos.z
							a.r=s.r
							a.g=s.g
							a.b=s.b
							a.allow_cut_view=True
							v=vec()
							v.x=s.dx
							v.y=s.dy
							v.z=s.dz
							#resize the shape to the mesh
							if s.triangles!=None:
								a.triangles=triangles_mul_vec(s.triangles.data,v)

								#flip
								#print(">>>>>>>>>",s.shape_flip_y)
								if s.shape_flip_y==True:
									a.triangles=triangles_flip(a.triangles)

								#move to correct place
								a.triangles=triangles_add_vec(a.triangles,pos)


								#scale to the screen
								a.triangles=project_trianges_m2screen(a.triangles)

							self.gl_objects_add(a)


