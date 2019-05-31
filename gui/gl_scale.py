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

x_mul=1.0
y_mul=1.0
z_mul=1.0
device_x=2.0
device_y=2.0
device_z=2.0
x_start=0.0
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

def scale_get_start_x():
	return x_start

def scale_get_start_z():
	return z_start

def scale_get_start_y():
	return 0.0

def scale_m2screen_x(x):
	global x_mul
	return x_start+x_mul*x

def scale_m2screen_y(y):
	global y_mul
	return 0.0+y_mul*y


def scale_m2screen_z(z):
	global z_mul
	return z_start+z_mul*z
	

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

