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
from gl_shapes import paint_from_array
from gl_shapes import paint_open_triangles_from_array
from gl_shapes import pyrmid
from gl_lib import box_lines
from gl_lib import plane
from gl_lib import raw_ray
from gl_lib import paint_ball
from gl_scale import scale_screen_x2m
from gl_scale import scale_screen_y2m

from gl_lib import gl_obj_id_starts_with
from gl_lib import paint_line
from gl_lib import paint_resistor
from gl_lib import paint_diode
from OpenGL.GLU import *
from OpenGL.GL import *

class gl_base_object():
	def __init__(self,x=0.0,y=0.0,z=0.0,dx=0.0,dy=0.0,dz=0.0,r=1.0,g=1.0,b=1.0):
		self.id=[]
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
		self.triangles=[]

	def dump(self):
		print(self.id)
		print(self.type)
		print(self.x)
		print(self.y)
		print(self.z)
		print(self.dx)
		print(self.dy)
		print(self.dz)
		print(self.dx)
		print(self.dy)
		print(self.dz)
		print(self.r)
		print(self.g)
		print(self.b)
		print(self.alpha)
		print(self.selected)
		print(self.selectable)
		print(self.moveable)
		print(self.triangles)

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
		if type(my_object.id)==str:
			print("id should be an array not a string")
			adsasddsa

		self.objects.append(my_object)

	def gl_objects_dump(self):
		for o in self.objects:
			print(o.type)
		print(len(self.objects))

	def gl_objects_move(obj,dx,dy):
		obj.x=obj.x+dx
		obj.y=obj.y+dy

	def gl_objects_count_regex(self,in_id):
		count=0
		for i in range(0,len(self.objects)):
			for id in self.objects[i].id: 	
				if id.startswith(in_id)==False:
					counnt=count+1

		return count


	def gl_objects_remove_regex(self,in_id):
		new_objects=[]
		for i in range(0,len(self.objects)):
			if gl_obj_id_starts_with(self.objects[i].id,in_id)==False:
				new_objects.append(self.objects[i])

		self.objects=new_objects


	def gl_objects_remove(self,in_id):
		for i in range(0,len(self.objects)):
			if in_id in self.objects[i].id:
				self.objects.pop(i)
				break

	def gl_objects_select(self,in_id):
		for i in range(0,len(self.objects)):
			if gl_obj_id_starts_with(self.objects[i].id,in_id)==True:
				self.objects[i].selected = not self.objects[i].selected
			else:
				self.objects[i].selected =False

	def gl_objects_render(self):
		#self.gl_objects_dump()
		for o in self.objects:
			if o.type=="plane":
				plane(o)
			if o.type=="ball":
				paint_ball(o)
			elif o.type=="ray":
				raw_ray(o)
			elif o.type=="line":
				paint_line(o)
			elif o.type=="resistor":
				paint_resistor(o)
			elif o.type=="diode":
				paint_diode(o)
			elif o.type=="open_triangles":
				paint_open_triangles_from_array(o)
			elif o.type=="solid":
				paint_from_array(o)
			elif o.type=="solid_and_mesh":
				paint_from_array(o)
				paint_open_triangles_from_array(o)
			elif o.type=="box":
				box(o.x,o.y,o.z,o.dx,o.dy,o.dz,o.r,o.g,o.b,o.alpha,name=o.id)
			else:
				paint_from_array(o)
				paint_open_triangles_from_array(o)
			if o.selected==True:
				if o.selectable==True:
					box_lines(o.x,o.y,o.z,o.dx,o.dy,o.dz)

