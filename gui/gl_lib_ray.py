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

from gl_list import gl_objects_remove_regex
from gl_list import gl_objects_add
from gl_list import gl_base_object

class fast_data():
	date=0
	out=[]

def fast_reset(d):
	d.date=0
	d.out=[]

ray_fast=fast_data()
fast_reset(ray_fast)

def fast_load(d,file_name):

	if os.path.isfile(file_name)==True:
		age = os.path.getmtime(file_name)

		if d.date!=age:
			d.out=[]
			if lines_read(d.out,file_name)==True:
				if len(d.out)==0:
					return False

				d.date=age
				
				return "reload"
			else:
				return False
		
	return True

def draw_rays(z0,ray_file,w):
	global ray_fast
	d=ray_fast

	if fast_load(d,ray_file)=="reload":
		if len(d.out)>2:
			head, tail = os.path.split(ray_file)
			out=d.out

			glLineWidth(2)
			num=tail[10:-4]

			wavelength=float(num)
			r,g,b=wavelength_to_rgb(wavelength)

			i=0
			step=2

			gl_objects_remove_regex("ray_trace_results")

			while(i<len(out)-2):
				x=scale_m2screen_x(out[i].x)
				dx=scale_m2screen_x(out[i+1].x)-scale_m2screen_x(out[i].x)

				y=scale_m2screen_y(out[i].y)
				dy=scale_m2screen_y(out[i+1].y)-scale_m2screen_y(out[i].y)

				z=z0
				dz=w

				a=gl_base_object()
				a.id="ray_trace_results"
				a.type="plane"
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
				
				i=i+step


