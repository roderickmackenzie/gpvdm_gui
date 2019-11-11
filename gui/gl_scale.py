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

from mesh import mesh_get_xlen
from mesh import mesh_get_zlen
from epitaxy import get_epi
import math

from triangle import triangle

x_mul=1.0
y_mul=1.0
z_mul=1.0
device_x=2.0
device_y=2.0
device_z=2.0
x_start=0.0
y_start=0.0
z_start=0.0


def scale(length):
	mul=1
	while((length*mul)<5):
		mul=mul*5.0

	#print(mul)
	return mul

def set_m2screen():
	global x_mul
	global y_mul
	global z_mul
	global device_x
	global device_y
	global device_z
	global x_start
	global y_start
	global z_start



	mesh_max=30

	epi=get_epi()
	x_len= mesh_get_xlen()
	z_len= mesh_get_zlen() 

	z_mul=scale(z_len)
	x_mul=scale(x_len)

	#print(x_mul,z_mul)
	mul=x_mul
	if z_len<x_len:
		mul=z_mul

	x_mul=mul
	z_mul=mul

	#print("m",mul)
	#z_mul=mul
	#x_mul=mul

	#print(x_len*x_mul,z_len*z_mul)
	if z_len*z_mul>mesh_max:
		z_mul=mesh_max/z_len

	if x_len*x_mul>mesh_max:
		x_mul=mesh_max/x_len

	y_mul=device_y/epi.ylen()

	device_x=mesh_get_xlen()*x_mul
	device_z=mesh_get_zlen()*z_mul

	x_start=-device_x/2.0
	z_start=-device_z/2.0
	y_start=device_y


def scale_get_start_x():
	return x_start

def scale_get_start_z():
	return z_start

def scale_get_start_y():
	return 0.0

def project_m2screen_x(x):
	global x_mul
	global x_start
	return x_start+x_mul*x

def project_m2screen_y(y):
	global y_mul
	global y_start

	return y_start-y_mul*y
	
def project_m2screen_z(z):
	global z_mul
	global z_start

	return z_start+z_mul*z

def project_trianges_m2screen(triangles):
	ret=[]
	for t in triangles:
		t0=triangle()
		t0.points=t.points
		t0.xyz0.x=project_m2screen_x(t.xyz0.x)
		t0.xyz0.y=project_m2screen_y(t.xyz0.y)
		t0.xyz0.z=project_m2screen_z(t.xyz0.z)

		t0.xyz1.x=project_m2screen_x(t.xyz1.x)
		t0.xyz1.y=project_m2screen_y(t.xyz1.y)
		t0.xyz1.z=project_m2screen_z(t.xyz1.z)

		t0.xyz2.x=project_m2screen_x(t.xyz2.x)
		t0.xyz2.y=project_m2screen_y(t.xyz2.y)
		t0.xyz2.z=project_m2screen_z(t.xyz2.z)

		ret.append(t0)

	return ret

def scale_trianges_m2screen(triangles):
	global x_mul
	global y_mul
	global z_mul
	ret=[]
	for t in triangles:
		t0=triangle()
		t0.points=t.points
		t0.xyz0.x=t.xyz0.x*x_mul
		t0.xyz0.y=-t.xyz0.y*y_mul
		t0.xyz0.z=t.xyz0.z*z_mul

		t0.xyz1.x=t.xyz1.x*x_mul
		t0.xyz1.y=-t.xyz1.y*y_mul
		t0.xyz1.z=t.xyz1.z*z_mul

		t0.xyz2.x=t.xyz2.x*x_mul
		t0.xyz2.y=-t.xyz2.y*y_mul
		t0.xyz2.z=t.xyz2.z*z_mul

		ret.append(t0)

	return ret

def scale_screen_x2m(x):
	global x_mul
	global x_start
	return (x-x_start)/x_mul

def scale_screen_y2m(y):
	global y_mul
	global y_start
	return -(y-y_start)/y_mul

def scale_get_xmul():
	global x_mul
	return x_mul

def scale_get_ymul():
	global y_mul
	return y_mul

def scale_get_zmul():
	global z_mul
	return z_mul

def scale_get_device_x():
	global device_x
	return device_x

def scale_get_device_z():
	global device_z
	return device_z

def scale_get_device_y():
	global device_y
	return device_y

