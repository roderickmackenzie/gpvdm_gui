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

## @package epitaxy
#  The epitaxy class.
#

import os
from inp import inp_save
from inp import inp_load_file
from util import isnumber

from cal_path import get_materials_path
from cal_path import get_default_material_path

from inp import inp_load_file
from inp import inp_search_token_array
from inp import inp_search_token_value
from inp import inp_remove_file

from inp import inp_isfile
from inp import inp_copy_file
from inp import inp_lsdir

from cal_path import get_sim_path
from util_zip import archive_merge_file
from mesh import mesh_get_ymesh
from shape import shape
from inp import inp_update_token_value

class epi_layer():
	def __init__(self):
		self.width=0
		self.mat_file=""
		self.name=""
		self.pl_file=""
		self.shapes=[]
		self.r=0
		self.g=0
		self.b=0
		self.electrical_layer="other"
		self.alpha=1.0
		self.lumo_file="none"
		self.homo_file="none"


	def set_width(self,data):
		if type(data)==float or type(data)==int:
			self.width=float(data)
		if type(data)==str:
			try:
				self.width=float(data)
			except:
				return False

		return True

	def set_mat_file(self,mat_file):
		self.mat_file=mat_file
		self.cal_rgb()

	def cal_rgb(self):
		path=os.path.join(os.path.join(get_materials_path(),self.mat_file),"mat.inp")
	
		zip_file=os.path.basename(self.mat_file)+".zip"

		mat_lines=inp_load_file(path,archive=zip_file)

		if mat_lines==False:
			return

		ret=inp_search_token_array(mat_lines, "#red_green_blue")

		if ret!=False:
			self.r=float(ret[0])
			self.g=float(ret[1])
			self.b=float(ret[2])
			self.alpha=float(inp_search_token_value(mat_lines, "#mat_alpha"))

class epitaxy():

	def __init__(self):
		self.layers=[]

	def dump(self):
		lines=self.gen_output()
		for l in lines:
			print(l)

	def get_new_material_name(self):
		count=0
		while(1):
			found=False
			name="newlayer"+str(count)
			for l in self.layers:
				if name==l.name:
					found=True
					break

			if found==False:
				break
			count=count+1

		return name

	def get_all_dos_files(self):
		tab=[]
		for l in self.layers:
			if l.electrical_layer.startswith("dos"):
				tab.append(l.electrical_layer)

		for l in self.layers:
			if len(l.shapes)!=0:
				for s in l.shapes:
					if s.shape_dos!="none":
						tab.append(s.shape_dos)
		return tab

	def clean_unused_files(self):
		files=inp_lsdir("sim.gpvdm")
		tab=self.get_all_dos_files()

		#dos files


		for i in range(0,len(files)):
			if files[i].startswith("dos") and files[i].endswith(".inp"):
				disk_file=files[i][:-4]
				if disk_file not in tab:
					inp_remove_file(disk_file)

		#pl files
		for l in self.layers:
			tab.append(l.pl_file+".inp")

		for i in range(0,len(files)):
			if files[i].startswith("pl") and files[i].endswith(".inp"):
				disk_file=files[i]
				if disk_file not in tab:
					inp_remove_file(disk_file)

		#shape files
		for l in self.layers:
			for s in l.shapes:
				tab.append(s+".inp")

		for i in range(0,len(files)):
			if files[i].startswith("shape") and files[i].endswith(".inp"):
				disk_file=files[i]
				if disk_file not in tab:
					inp_remove_file(disk_file)

		#lumo files
		for l in self.layers:
			tab.append(l.lumo_file+".inp")

		for i in range(0,len(files)):
			if files[i].startswith("lumo") and files[i].endswith(".inp"):
				disk_file=files[i]
				if disk_file not in tab:
					inp_remove_file(disk_file)

		#homo files
		for l in self.layers:
			tab.append(l.homo_file+".inp")

		for i in range(0,len(files)):
			if files[i].startswith("homo") and files[i].endswith(".inp"):
				disk_file=files[i]
				if disk_file not in tab:
					inp_remove_file(disk_file)


	def layer_to_index(self,index):
		if type(index)==int:
			return index
		else:
			for i in range(0,len(self.layers)):
				if self.layers[i].name==index:
					return i
		return -1

	def add_layer(self,pos=-1):
		if pos!=-1:
			pos=self.layer_to_index(pos)

		a=epi_layer()
		a.width=100e-9
		a.mat_file="blends/p3htpcbm"
		a.name=self.get_new_material_name()
		a.pl_file="none"
		a.shapes=[]
		a.lumo_file="none"
		a.homo_file="none"
		self.electrical_layer="other"
		a.r=1.0
		a.g=0
		a.b=0
		a.alpha=0.5
		if pos==-1:
			self.layers.append(a)
		else:
			self.layers.insert(pos, a)
		return a

	def rename_layer(self,pos,name):
		if pos!=-1:
			pos=self.layer_to_index(pos)

		self.layers[pos].name=name

	def remove_layer(self,pos):
		pos=self.layer_to_index(pos)
		self.layers.pop(pos)


	def move_up(self,pos):
		pos=self.layer_to_index(pos)
		if pos<1:
			return

		self.layers.insert(pos-1, self.layers.pop(pos))

	def move_down(self,pos):
		pos=self.layer_to_index(pos)
		print(pos)
		if pos>len(self.layers)-1 or pos<0:
			return

		self.layers.insert(pos+1, self.layers.pop(pos))

	def gen_output(self):
		lines=[]
		lines.append("#layers")
		lines.append(str(len(epi.layers)))

		layer=0
		for i in range(0,len(epi.layers)):
			lines.append("#layer_name"+str(layer))
			lines.append(str(epi.layers[i].name))
			lines.append("#layer_width"+str(layer))
			lines.append(str(epi.layers[i].width))
			lines.append("#layer_material_file"+str(layer))
			lines.append(epi.layers[i].mat_file)
			lines.append("#layer_dos_file"+str(layer))
			lines.append(epi.layers[i].electrical_layer)
			lines.append("#layer_pl_file"+str(layer))
			lines.append(epi.layers[i].pl_file)
			lines.append("#layer_shape"+str(layer))
			if len(epi.layers[i].shapes)==0:
				lines.append("none")
			else:
				build=""
				for s in epi.layers[i].shapes:
					build=build+s.file_name+","
				build=build[:-1]
				lines.append(build)

			lines.append("#layer_lumo"+str(layer))
			lines.append(epi.layers[i].lumo_file)
			lines.append("#layer_homo"+str(layer))
			lines.append(epi.layers[i].homo_file)
			layer=layer+1

		lines.append("#ver")
		lines.append("1.42")
		lines.append("#end")
		return lines

	def save(self):
		lines=self.gen_output()

		inp_save(os.path.join(get_sim_path(),"epitaxy.inp"),lines,id="epitaxy")

		ymesh=mesh_get_ymesh()
		ymesh.do_remesh(self.ylen_active())

	def update_layer_type(self,layer,data):
		l=self.layers[layer]

		if data=="active layer" and l.electrical_layer.startswith("dos")==False:

			l.electrical_layer=self.new_dos_file()

			mat_dir=os.path.join(get_materials_path(),l.mat_file)

			new_dos_file=l.electrical_layer+".inp"
			
			if inp_isfile(new_dos_file)==False:
				dos_path_generic=os.path.join(get_default_material_path(),"dos.inp")
				inp_copy_file(new_dos_file,dos_path_generic)

				dos_path_material=os.path.join(mat_dir,"dos.inp")
				if os.path.isfile(dos_path_material)==True:
					archive_merge_file(os.path.join(get_sim_path(),"sim.gpvdm"),os.path.join(mat_dir,"sim.gpvdm"),new_dos_file,"dos.inp")


		if data=="active layer" and l.pl_file.startswith("pl")==False:

			l.pl_file=self.new_pl_file()

			mat_dir=os.path.join(get_materials_path(),l.pl_file)

			new_pl_file=l.pl_file+".inp"
			if inp_isfile(new_pl_file)==False:
				pl_path=os.path.join(mat_dir,"pl.inp")
				if os.path.isfile(pl_path)==False:
					pl_path=os.path.join(get_default_material_path(),"pl.inp")

				inp_copy_file(new_pl_file,pl_path)

		if data=="active layer" and l.lumo_file.startswith("lumo")==False:

			l.lumo_file=self.new_lumo_file()

			mat_dir=os.path.join(get_materials_path(),l.lumo_file)

			new_lumo_file=l.lumo_file+".inp"
			if inp_isfile(new_lumo_file)==False:
				lumo_path=os.path.join(mat_dir,"lumo.inp")
				if os.path.isfile(lumo_path)==False:
					lumo_path=os.path.join(get_default_material_path(),"lumo.inp")

				inp_copy_file(new_lumo_file,lumo_path)

		if data=="active layer" and l.homo_file.startswith("homo")==False:

			l.homo_file=self.new_homo_file()

			mat_dir=os.path.join(get_materials_path(),l.homo_file)

			new_homo_file=l.homo_file+".inp"
			if inp_isfile(new_homo_file)==False:
				homo_path=os.path.join(mat_dir,"homo.inp")
				if os.path.isfile(homo_path)==False:
					homo_path=os.path.join(get_default_material_path(),"homo.inp")

				inp_copy_file(new_homo_file,homo_path)

		if data!="active layer":
			l.electrical_layer=data
			l.pl_file="none"
			l.lumo_file="none"
			l.homo_file="none"


		self.clean_unused_files()

		#self.dump()

	def find_shape_by_file_name(self,shape_file):
		if shape_file.endswith(".inp"):
			shape_file=shape_file[:-4]

		for l in self.layers:
			for s in l.shapes:
				if s.file_name==shape_file:
					return s
		return None

	def del_dos_shape(self,shape_file):
		s=self.find_shape_by_file_name(shape_file)
		s.shape_dos="none"
		inp_update_token_value(s.file_name,"#shape_dos",s.shape_dos)

	def add_new_dos_to_shape(self,shape_file):
		s=self.find_shape_by_file_name(shape_file)

		if s.shape_dos!="none":
			return s.shape_dos

		new_file=self.new_dos_file()

		s.shape_dos=new_file

		inp_update_token_value(s.file_name,"#shape_dos",s.shape_dos)

		new_dos_file=new_file+".inp"
			
		if inp_isfile(new_dos_file)==False:
			dos_path_generic=os.path.join(get_default_material_path(),"dos.inp")
			inp_copy_file(new_dos_file,dos_path_generic)

		return new_file

	def new_dos_file(self):
		files=self.get_all_dos_files()

		for i in range(0,20):
			name="dos"+str(i)

			if name not in files:
				return "dos"+str(i)

	def new_pl_file(self):
		global epi
		for i in range(0,20):
			name="pl"+str(i)
			found=False
			for a in epi.layers:
				if a.pl_file==name:
					found=True

			if found==False:
				return name

	def new_lumo_file(self):
		global epi
		for i in range(0,20):
			name="lumo"+str(i)
			found=False
			for a in epi.layers:
				if a.lumo_file==name:
					found=True

			if found==False:
				return name

	def new_homo_file(self):
		global epi
		for i in range(0,20):
			name="homo"+str(i)
			found=False
			for a in epi.layers:
				if a.homo_file==name:
					found=True

			if found==False:
				return name

	def new_shape_file(self):
		all_shape_files=[]
		for l in self.layers:
			for s in l.shapes:
				all_shape_files.append(s.file_name)
		for i in range(0,20):
			name="shape"+str(i)
			found=False
			if name not in all_shape_files:
				return name
				
	def get_shapes(self,layer):
		return epi.layers[layer].shapes

	def ylen(self):
		tot=0
		for a in epi.layers:
			tot=tot+a.width

		return tot

	def ylen_active(self):
		tot=0
		for a in epi.layers:
			if a.electrical_layer.startswith("dos")==True:
				tot=tot+a.width

		return tot

	def reload_shapes(self):
		for a in epi.layers:
			for s in a.shapes:
				print(s.file_name)
				s.load(s.file_name)

	def load(self,path):
		self.layers=[]

		lines=[]

		lines=inp_load_file(os.path.join(path,"epitaxy.inp"))


		if lines!=False:
			#compat layer for 
			ver=float(inp_search_token_value(lines,"#ver"))

			pos=0
			pos=pos+1

			for i in range(0, int(lines[pos])):
				a=epi_layer()
				pos=pos+1		#token
				pos=pos+1
				a.name=lines[pos]

				pos=pos+1		#token
				pos=pos+1
				a.width=float(lines[pos])

				pos=pos+1		#token
				pos=pos+1
				lines[pos]=lines[pos].replace("\\", "/")
				a.set_mat_file(lines[pos])

				pos=pos+1		#token
				pos=pos+1
				a.electrical_layer=lines[pos]		#value

				pos=pos+1		#token
				pos=pos+1
				a.pl_file=lines[pos]		#value


				pos=pos+1		#token
				pos=pos+1
				temp=lines[pos]		#value
				if temp=="none":
					a.shapes=[]
				else:
					files=temp.split(",")
					for s in files:
						my_shape=shape()
						my_shape.load(s)
						a.shapes.append(my_shape)

				pos=pos+1		#token
				pos=pos+1
				a.lumo_file=lines[pos]		#value

				pos=pos+1		#token
				pos=pos+1
				a.homo_file=lines[pos]		#value

				epi.layers.append(a)


epi=epitaxy()



def epitay_get_next_dos_layer(layer):
	global epi
	layer=layer+1
	for i in range(layer,len(epi.layers)):
		if epi.layers[i].electrical_layer.startswith("dos")==True:
			return i


def epitaxy_get_layer(i):
	global epi
	return epi.layers[i]

def get_epi():
	global epi
	return epi

def epitaxy_get_epi():
	global epi
	return epi.layers

def epitaxy_dos_file_to_layer_name(dos_file):
	global epi
	if dos_file.endswith(".inp")==True:
		dos_file=dos_file[:-4]

	for i in range(0,len(epi.layers)):
		if epi.layers[i].electrical_layer==dos_file:
			return epi.layers[i].name

	return False

def epitaxy_get_dos_files():
	global epi
	dos_file=[]
	for i in range(0,len(epi.layers)):
		if epi.layers[i].electrical_layer.startswith("dos")==True:
			dos_file.append(epi.layers[i].electrical_layer)

	return dos_file

def epitaxy_get_device_start():
	global epi

	pos=0.0
	for i in range(0, len(epi.layers)):
		if epi.layers[i].electrical_layer.startswith("dos")==True:
			return pos

		pos=pos+epi.layers[i].width
			
def epitaxy_get_layers():
	global epi
	return len(epi.layers)

def epitaxy_get_width(i):
	global epi
	return epi.layers[i].width

def epitaxy_get_electrical_layer(i):
	global epi
	return epi.layers[i].electrical_layer

def epitaxy_get_mat_file(i):
	global epi
	return epi.layers[i].mat_file

def epitaxy_get_pl_file(i):
	global epi
	return epi.layers[i].pl_file

def epitaxy_get_dos_file(i):
	global epi
	return epi.layers[i].electrical_layer

def epitaxy_get_name(i):
	global epi
	return epi.layers[i].name

