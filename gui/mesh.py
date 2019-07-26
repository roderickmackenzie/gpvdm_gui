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

## @package mesh
#  The underlying mesh class.
#


#import sys
import os
#import shutil
from inp import inp_save
from inp import inp_load_file
from code_ctrl import enable_betafeatures

from cal_path import get_sim_path
from str2bool import str2bool

class mlayer():
	def __init__(self):
		self.thick=0.0
		self.points=0
		self.mul=1.0
		self.left_right="left"

class mesh:
	def __init__(self,direction):
		self.direction=direction
		self.layers=[]
		self.remesh=False
		self.points=[]

	def calculate_points(self):
		total_pos=0.0
		out_x=[]
		out_y=[]

		for i in range(0,len(self.layers)):
			l=self.layers[i]
			layer_length=l.thick
			layer_points=l.points
			layer_mul=l.mul
			layer_left_right=l.left_right
			dx=layer_length/layer_points
			pos=dx/2
			ii=0
			temp_x=[]
			temp_mag=[]
			while(pos<layer_length):
				temp_x.append(pos)
				temp_mag.append(1.0)

				pos=pos+dx*pow(layer_mul,ii)

				ii=ii+1
				#dx=dx*layer_mul
			for i in range(0,len(temp_x)):
				if layer_left_right=="left":
					out_x.append((temp_x[i]+total_pos))
				else:
					out_x.append((layer_length-temp_x[i]+total_pos))

				out_y.append(temp_mag[i])
			total_pos=total_pos+layer_length
		
		out_x.sort()

		self.points=out_x
		return out_x,out_y

	def load(self):
		file_name=os.path.join(get_sim_path(),"mesh_"+self.direction+".inp")

		self.clear()

		my_list=[]
		pos=0
		lines=inp_load_file(file_name)

		if lines!=False:
			if lines[pos]!="#remesh_enable":			#Check we are not trying to open an old version
				return False

			pos=pos+1	#first comment
			remesh=str2bool(lines[pos])
			pos=pos+1	#remesh

			self.remesh=remesh

			pos=pos+1	#first comment
			mesh_layers=int(lines[pos])
			for i in range(0, mesh_layers):
				#thick
				pos=pos+1			#token
				token=lines[pos]
				pos=pos+1
				thick=lines[pos]	#length

				pos=pos+1			#token
				token=lines[pos]
				pos=pos+1
				points=lines[pos] 	#points
			
				pos=pos+1			#token
				token=lines[pos]
				pos=pos+1
				mul=lines[pos] 		#mul

				pos=pos+1			#token
				token=lines[pos]
				pos=pos+1
				left_right=lines[pos] 		#left_right

				self.add_layer(thick,points,mul,left_right)

		self.update()
		return True

	def clear(self):
		self.remesh=True
		self.layers=[]


	def add_layer(self,thick,points,mul,left_right):
		a=mlayer()
		a.thick=float(thick)
		a.points=float(points)
		a.mul=float(mul)
		a.left_right=left_right
		self.layers.append(a)

	def update(self):
		self.calculate_points()

	def save(self):
		file_name=os.path.join(get_sim_path(),"mesh_"+self.direction+".inp")
		lines=[]
		lines.append("#remesh_enable")
		lines.append(str(self.remesh))	
		lines.append("#mesh_layers")
		lines.append(str(len(self.layers)))
		i=0
		for item in self.layers:
			lines.append("#mesh_layer_length"+str(i))
			lines.append(str(item.thick))
			lines.append("#mesh_layer_points"+str(i))
			lines.append(str(item.points))
			lines.append("#mesh_layer_mul"+str(i))
			lines.append(str(item.mul))
			lines.append("#mesh_layer_left_right"+str(i))
			lines.append(str(item.left_right))
			i=i+1
		lines.append("#ver")
		lines.append("1.0")
		lines.append("#end")
		inp_save(file_name,lines,id="mesh")

	def do_remesh(self,to_size):
		if len(self.layers)!=1:
			return

		if self.layers[0].thick!=to_size:
			print("changing ",self.layers[0].thick,to_size)

			self.layers[0].thick=to_size
			self.save()

xlist=mesh("x")
ylist=mesh("y")
zlist=mesh("z")

		
def mesh_save_all():
	global xlist
	global ylist
	global zlist
	xlist.save()
	ylist.save()
	zlist.save()
	

def mesh_load_all():
	global xlist
	global ylist
	global zlist

	ret=True

	r=xlist.load()
	ret=ret and r
	r=ylist.load()
	ret=ret and r
	r=zlist.load()
	ret=ret and r
	return ret
	
def mesh_set_xlen(value):
	global xlist
	if len(xlist.layers)==1:
		xlist.layers[0].thick=value
		return True
	else:
		return False

def mesh_set_zlen(value):
	global zlist
	if len(zlist.layers)==1:
		zlist.layers[0].thick=value
		return True
	else:
		return False


def mesh_get_xlen():
	global xlist
	tot=0.0
	for a in xlist.layers:
		tot=tot+a.thick
	return tot

def mesh_get_ylen():
	global ylist
	tot=0.0
	for a in ylist.layers:
		tot=tot+a.thick
	return tot

def mesh_get_zlen():
	global zlist
	tot=0.0
	for a in zlist.layers:
		tot=tot+a.thick
	return tot

def mesh_get_xpoints():
	global xlist
	tot=0.0
	for a in xlist.layers:
		tot=tot+a.points
	return tot

def mesh_get_ypoints():
	global ylist
	tot=0.0
	for a in ylist.layers:
		tot=tot+a.points
	return tot

def mesh_get_zpoints():
	global zlist
	tot=0.0
	for a in zlist.layers:
		tot=tot+a.points
	return tot

def mesh_get_xlayers():
	global xlist
	return len(xlist.layers)

def mesh_get_ylayers():
	global ylist
	return len(ylist.layers)

def mesh_get_zlayers():
	global zlist
	return len(zlist.layers)

def mesh_get_xmesh():
	global xlist
	return xlist

def mesh_get_ymesh():
	global ylist
	return ylist

def mesh_get_zmesh():
	global zlist
	return zlist
	
def mesh_clear():
	global xlist
	global ylist
	global zlist
	xlist.clear()
	ylist.clear()
	zlist.clear()



