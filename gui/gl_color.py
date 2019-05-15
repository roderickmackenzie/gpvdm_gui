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

## @package gl_color
#  Handle colors for the OpenGL display, can also do false color for color picking.
#

import sys
from OpenGL.GL import *

class color():
	def __init__(self,r,g,b,alpha=-1,name=""):
		self.r=r
		self.g=g
		self.b=b
		self.alpha=alpha
		self.name=name

	def __str__(self):
		return "name="+self.name+" r="+str(self.r)+" g="+str(self.g)+" b="+str(self.b)

	def __eq__(self, other):
		if other.r==self.r and other.g==self.g and other.b==self.b:
			return True
		return False

color_list=[]
false_color=False

def search_color(input_color):
	global color_list
	my_min=1000.0
	for i in range(0,len(color_list)):
		if input_color==color_list[i]:
			return color_list[i].name

		#print("r=",r,"g=",g,"b=",b,"r=",color_list[i].r,"g=",color_list[i].g,"b=",color_list[i].b,color_list[n].name)
	return "none"

def set_false_color(value):
	global false_color
	false_color=value

def set_color(r,g,b,name,alpha=-1):
	global color_list
	global false_color

	if false_color==True:
		rgb_int=len(color_list)+1
		r =  rgb_int & 255
		g = (rgb_int >> 8) & 255
		b =   (rgb_int >> 16) & 255
		alpha=255

		a=color(r,g,b,alpha=alpha,name=name)

		color_list.append(a)

	if type(r)==int:
		r=r/255
		g=g/255
		b=b/255
		alpha=alpha/255

	if alpha==-1:
		glColor3f(r,g,b)
	else:
		glColor4f(r,g,b, alpha)

def clear_color():
	global color_list
	color_list=[]


def print_color():
	global color_list
	for i in range(0,len(color_list)):
		print(color_list[i])

