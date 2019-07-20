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


from gl_list import gl_objects_remove_regex
from gl_list import gl_objects_add
from gl_list import gl_base_object
from gl_list import gl_objects_count_regex
from dat_file import dat_file
ray_data=dat_file()
ray_mesh_data=dat_file()

def draw_rays(ray_file):
	global ray_data
	r=1.0
	g=0.0
	b=0.0
	if ray_data.load(ray_file)==True:
		if ray_data.new_read==True:
			gl_objects_remove_regex("ray_trace_results")
			for l in ray_data.data:
				if len(l)==2:
					z=scale_m2screen_z(l[0][0])
					dz=scale_m2screen_z(l[1][0])-scale_m2screen_x(l[0][0])

					x=scale_m2screen_x(l[0][1])
					dx=scale_m2screen_x(l[1][1])-scale_m2screen_x(l[0][1])

					y=scale_m2screen_y(l[0][2])
					dy=scale_m2screen_y(l[1][2])-scale_m2screen_y(l[0][2])

					a=gl_base_object()
					a.id="ray_trace_results"
					a.type="ray"
					a.x=x
					a.y=y
					a.z=z
					a.dx=dx
					a.dy=dy
					a.dz=dz
					a.r=ray_data.r
					a.g=ray_data.g
					a.b=ray_data.b
					gl_objects_add(a)

def draw_ray_mesh(ray_file):
	global ray_mesh_data
	r=1.0
	g=0.0
	b=0.0
	if ray_mesh_data.load("triangles.dat")==True:
		if ray_mesh_data.new_read==True or gl_objects_count_regex("ray_mesh")==0:
			gl_objects_remove_regex("ray_mesh")
			for l in ray_mesh_data.data:
				pos=[[0,1],[1,2],[2,0]]
				for p in pos:
					z=scale_m2screen_z(l[p[0]][0])
					dz=scale_m2screen_z(l[p[1]][0])-scale_m2screen_x(l[p[0]][0])

					x=scale_m2screen_x(l[p[0]][1])
					dx=scale_m2screen_x(l[p[1]][1])-scale_m2screen_x(l[p[0]][1])

					y=scale_m2screen_y(l[p[0]][2])
					dy=scale_m2screen_y(l[p[1]][2])-scale_m2screen_y(l[p[0]][2])

					a=gl_base_object()
					a.id="ray_mesh"
					a.type="ray"
					a.x=x
					a.y=y
					a.z=z
					a.dx=dx
					a.dy=dy
					a.dz=dz
					a.r=r
					a.g=g
					a.b=b
					gl_objects_add(a)


