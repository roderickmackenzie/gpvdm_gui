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
from gl_scale import scale_m2screen_x
from gl_scale import scale_m2screen_y
from gl_scale import scale_m2screen_z
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

class gl_contacts():

	def draw_contacts(self):
		self.gl_objects_remove_regex("contacts")

		y=0

		l=0
		btm_layer=len(epitaxy_get_epi())-1

		for obj in epitaxy_get_epi():
			y_len=obj.dy*scale_get_ymul()
			dy_shrink=y_len*0.1

			name=obj.name
			layer_name="layer:"+name
			display_name=name
			alpha=obj.alpha
			if len(obj.shapes)>0:
				alpha=0.5

			if obj.electrical_layer=="contact":

				for c in get_epi().contacts.contacts:

					if (c.position=="top" and l==0) or (c.position=="bottom" and l==btm_layer):
						if len(self.x_mesh.points)==1 and len(self.z_mesh.points)==1:
							xstart=0
							xwidth=scale_get_device_x()
						else:
							xstart=scale_get_xmul()*c.shape.x0
							xwidth=scale_get_xmul()*c.shape.dx

						if name!="air":
							a=gl_base_object()
							a.id="contacts"
							a.type="solid"
							a.x=xstart
							a.y=y+dy_shrink/2
							a.z=0
							a.dx=xwidth
							a.dy=y_len-dy_shrink
							a.dz=scale_get_device_z()
							a.r=obj.r
							a.g=obj.g
							a.b=obj.b
							a.alpha=1.0
							my_vec=vec()
							my_vec.x=c.shape.dx
							my_vec.y=obj.dy
							my_vec.z=mesh_get_zlen()

							a.triangles=scale_trianges_m2screen(triangles_mul_vec(c.shape.triangles.data,my_vec))

							self.gl_objects_add(a)

			l=l+1
			y=y-y_len

