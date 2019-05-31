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

class fast_data():
	date=0
	m=0
	std=0
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
				#print(d.out)
				d.date=age

				d.m=0
				s=0
				for i in range(0,len(d.out)):
					d.m=d.m+d.out[i].x
				d.m=d.m/len(d.out)

				for i in range(0,len(d.out)):
					s=s+(d.out[i].x-d.m)*(d.out[i].x-d.m)
				d.std=sqrt(s/len(d.out))
				
				return True
			else:
				return False
		
	return True

def draw_rays(x0,y0,z0,ray_file,top,width,y_mul,w):
	global ray_fast
	d=ray_fast
	
	if fast_load(d,ray_file)==True:
		if len(d.out)>2:
			head, tail = os.path.split(ray_file)
			out=d.out
			m=d.m
			std=d.std

			#for i in range(0,len(out)):
			#	print(out[i].x,out[i].x)
			#print(ray_file)
			glLineWidth(2)
			num=tail[10:-4]
			if isnumber(num)==False:
				#print("not a number")
				return

			if std==0.0:
				#print("std is zero")
				return

			wavelength=float(num)
			r,g,b=wavelength_to_rgb(wavelength)

			glColor4f(r, g, b,0.5)
			glBegin(GL_QUADS)

			sub=epitaxy_get_device_start()
			s=0
			mm=0

			std_mul=0.05
			#print(len(d.out))
			#print(d.m)
			#print(d.std)
			x_mul=width/(std*std_mul)
			i=0
			#step=((int)(len(out)/6000))*2
			#if step<2:
			step=2
				
			while(i<len(out)-2):
				if fabs(out[i].x-m)<std*std_mul:
					if fabs(out[i+1].x-m)<std*std_mul:
						#print(sub)
						glVertex3f(x0+width/2+(out[i].x-m)*x_mul, y0+top-(out[i].y+sub)*y_mul, z0+0)
						glVertex3f(x0+width/2+(out[i+1].x-m)*x_mul, y0+top-(out[i+1].y+sub)*y_mul, z0+0)

						glVertex3f(x0+width/2+(out[i+1].x-m)*x_mul, y0+top-(out[i+1].y+sub)*y_mul, z0+w)
						glVertex3f(x0+width/2+(out[i].x-m)*x_mul, y0+top-(out[i].y+sub)*y_mul, z0+w)



				i=i+step

			glEnd()
