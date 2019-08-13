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

## @package triangle
#  A base triangle class
#

import os
from triangle import vec

def triangles_get_min(data):
	if len(data)==0:
		return None

	x=data[0].min_x()
	y=data[0].min_y()
	z=data[0].min_z()

	for t in data:
		if t.min_x()<x:
			x=t.min_x()

		if t.min_y()<y:
			y=t.min_y()

		if t.min_z()<z:
			z=t.min_z()

	ret=vec()
	ret.x=x
	ret.y=y
	ret.z=z

	return ret

def triangles_get_max(data):
	if len(data)==0:
		return None

	x=data[0].max_x()
	y=data[0].max_y()
	z=data[0].max_z()

	for t in data:
		if t.min_x()>x:
			x=t.min_x()

		if t.min_y()>y:
			y=t.min_y()

		if t.min_z()>z:
			z=t.min_z()

	ret=vec()
	ret.x=x
	ret.y=y
	ret.z=z

	return ret

def triangles_sub_vec(data,vec):
	if len(data)==0:
		return None

	for i in range(0,len(data)):
		data[i]=data[i]-vec

def triangles_div_vec(data,vec):
	if len(data)==0:
		return None

	for i in range(0,len(data)):
		data[i]=data[i]/vec

def triangles_mul_vec(data,vec):
	if len(data)==0:
		return None

	for i in range(0,len(data)):
		data[i]=data[i]*vec

