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
class save_object():
	def __init__(self):
		id=""
		x=0.0
		y=0.0
		z=0.0
		vec=[]
		
save_list=[]

def gl_save_clear():
	global save_list
	save_list=[]

def gl_save_add(string,x,y,z,vector):
	a=save_object()
	a.x=x
	a.y=y
	a.z=z
	a.id=string
	a.vec=' '.join(map(str, vector))
	save_list.append(a)

def gl_save_print():
	global save_list
	print(save_list)

def gl_save_list():
	global save_list
	return save_list

def gl_save_save(file_name):
	global save_list
	text_file = open(file_name, "w")
	for item in save_list:
		text_file.write(item.id+" "+str(item.x)+" "+str(item.y)+" "+str(item.z)+" "+item.vec+"\n")
	text_file.close()

def gl_save_load():
	global save_list
	save_list=[]
	mul=4.0
	files=glob.glob("*.3d")
	start=mul*len(files)
	for i in range(0,len(files)):
		dx=i*mul-start
		f = open(files[i], "r")
		lines = f.readlines()
		f.close()
		for line in lines:
			split=line.split()
			v=[]
			for ii in range(4,len(split)):
				v.append(float(split[ii]))
			gl_save_add(split[0],float(split[1])+dx,float(split[2]),float(split[3]),v)


