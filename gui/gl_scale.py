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


def set_m2screen():
	global x_mul
	global y_mul
	global z_mul
	global device_x
	global device_y
	global device_z

	epi=get_epi()
	x_log= mesh_get_xlen()

	if x_log<1e-3:
		x_mul=1e5

	if x_log<1e-4:
		x_mul=1e6

	if x_log<1e-5:
		x_mul=1e7

	if x_log<1e-6:
		x_mul=1e8

	z_log= mesh_get_zlen() 
	if z_log<1e-3:
		z_mul=1e5

	if z_log<1e-4:
		z_mul=1e6

	if z_log<1e-5:
		z_mul=1e7

	if z_log<1e-6:
		z_mul=1e8

	y_mul=device_y/epi.ylen()

	device_x=mesh_get_xlen()*scale_get_xmul()
	device_z=mesh_get_zlen()*scale_get_zmul()

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

