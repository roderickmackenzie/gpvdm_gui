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

## @package gl_save
#  Save the OpenGL scene.
#

import sys
import glob

from gl_shapes import box
from gl_shapes import dome
from gl_shapes import pyrmid
from gl_lib import box_lines
from gl_lib import plane
from gl_lib import raw_ray

from gl_scale import scale_screen_x2m
from gl_scale import scale_screen_y2m

from epitaxy import epitaxy_get_device_start


class gl_base_object():
	def __init__(self,x=0.0,y=0.0,z=0.0,dx=0.0,dy=0.0,dz=0.0,r=1.0,g=1.0,b=1.0):
		self.id=""
		self.type=""
		self.x=x
		self.y=y
		self.z=z
		self.dx=dx
		self.dy=dy
		self.dz=dz
		self.r=r
		self.g=g
		self.b=b
		self.alpha=0.5
		self.selected=False
		self.selectable=False
		self.moveable=False

class gl_objects():

	def __init__(self):
		self.objects=[]

	def gl_objects_clear(self):
		self.objects=[]

	def gl_object_deselect(self):
		changed=False
		for i in range(0,len(self.objects)):
			if self.objects[i].selected==True:
				self.objects[i].selected=False
				return self.objects[i]
		return False

	def gl_objects_is_selected(self):
		for i in range(0,len(self.objects)):
			if self.objects[i].selected==True:
				return self.objects[i]
		return False

	def gl_objects_add(self,my_object):
		self.objects.append(my_object)

	def gl_objects_move(obj,dx,dy):
		obj.x=obj.x+dx
		obj.y=obj.y+dy

	def gl_objects_count_regex(self,id):
		count=0
		for i in range(0,len(self.objects)):
			if self.objects[i].id.startswith(id)==False:
				counnt=count+1

		return count


	def gl_objects_remove_regex(self,id):
		new_objects=[]
		for i in range(0,len(self.objects)):
			if self.objects[i].id.startswith(id)==False:
				new_objects.append(self.objects[i])

		self.objects=new_objects


	def gl_objects_remove(self,id):
		for i in range(0,len(self.objects)):
			if id==self.objects[i].id:
				self.objects.pop(i)
				break

	def gl_objects_select(self,id):
		for i in range(0,len(self.objects)):
			if id==self.objects[i].id:
				self.objects[i].selected= not self.objects[i].selected
			else:
				self.objects[i].selected =False

	def gl_objects_render(self):
		for o in self.objects:
			if o.type=="box":
				box(o.x,o.y,o.z,o.dx,o.dy,o.dz,o.r,o.g,o.b,0.5,name=o.id)
			elif o.type=="plane":
				plane(o.x,o.y,o.z,o.dx,o.dy,o.dz,o.r,o.g,o.b)
			elif o.type=="ray":
				raw_ray(o.x,o.y,o.z,o.dx,o.dy,o.dz,o.r,o.g,o.b)
			elif o.type=="dome":
				dome(o)
			elif o.type=="pyrmid":
				pyrmid(o)
			if o.selected==True:
				if o.selectable==True:
					box_lines(o.x,o.y,o.z,o.dx,o.dy,o.dz)

