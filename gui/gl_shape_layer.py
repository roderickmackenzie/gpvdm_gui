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
	from gl_shapes import dome
	from gl_shapes import half_cyl
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

class shape_layer():
	def shape_layer(self,obj,s,ix,iy,iz, name="name"):
		self.gl_objects_remove_regex(name)
		x_pos=ix+s.x0*scale_get_xmul()#+s.shape_x0*scale_get_xmul()
		y_pos=iy+s.y0*scale_get_ymul()
		z_pos=iz+s.z0*scale_get_zmul()#+s.shape_z0*scale_get_zmul()

		height=1.0
		dx=s.dx*scale_get_xmul()
		dz=s.dz*scale_get_zmul()
		dy=s.dy*scale_get_ymul()

		dx_tot=(s.dx+s.dx_padding)*scale_get_xmul()
		dz_tot=(s.dz+s.dz_padding)*scale_get_zmul()
		dy_tot=(s.dy+s.dy_padding)*scale_get_ymul()

		for x in range(0,s.shape_nx):
			z_pos=iz+s.z0*scale_get_zmul()
			for z in range(0,s.shape_nz):
				if s.type=="dome":
					a=gl_base_object()
					a.id=name
					a.type="dome"
					a.x=x_pos
					a.y=y_pos
					a.z=z_pos
					a.dx=dx
					a.dy=dy
					a.dz=dz
					a.r=s.r
					a.g=s.g
					a.b=s.b
					a.triangles=s.triangles
					self.gl_objects_add(a)
					#dome(x_pos,y_pos,z_pos,dx,dy,dz,name=name)
				elif s.type=="pyrmid":
					a=gl_base_object()
					a.id=name
					a.type="pyrmid"
					a.x=x_pos
					a.y=y_pos
					a.z=z_pos
					a.dx=dx
					a.dy=dy
					a.dz=dz
					a.r=s.r
					a.g=s.g
					a.b=s.b
					self.gl_objects_add(a)
					#pyrmid(x_pos,y_pos,z_pos,dx,dy,dz, name=name)
				elif s.type=="box":
					a=gl_base_object()
					a.id=name
					a.type="box"
					a.x=x_pos
					a.y=y_pos
					a.z=z_pos
					a.dx=dx
					a.dy=dy
					a.dz=dz
					a.r=s.r
					a.g=s.g
					a.b=s.b
					a.triangles=s.triangles
					self.gl_objects_add(a)
					#box(x_pos,y_pos,z_pos,dx, dy,dx, s.r, s.g, s.b, obj.alpha, name=name)
				elif s.type=="tube":
					a=gl_base_object()
					a.id=name
					a.type="half_cyl"
					a.x=x_pos
					a.y=y_pos
					a.z=z_pos
					a.dx=dx
					a.dy=dy
					a.dz=dz
					a.r=s.r
					a.g=s.g
					a.b=s.b
					self.gl_objects_add(a)
					#half_cyl(x_pos,y_pos,z_pos,dx,dy,dz, name=name)
				z_pos=z_pos+dz_tot
			x_pos=x_pos+dx_tot

