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

## @package dat_file
#  Load and dump a dat file into a dat class
#

import os
import shutil
import re
import hashlib
import glob
from util_zip import zip_get_data_file
from dat_file_class import dat_file
from inp import inp_load_file

#search first 40 lines for dims
def dat_file_load_info(output,lines):
	if len(lines)>1:
		if lines[0]=="#gpvdm":
			max_lines=len(lines)
			if max_lines>40:
				max_lines=40

			found_xyz=False
			for i in range(0, max_lines):
				if (len(lines[i])>0):
					if (lines[i][0]!="#"):
						break
					else:
						command=lines[i].split(" ",1)
						if len(command)<2:
							command.append("")
						if (command[0]=="#x_mul"):
							output.x_mul=float(command[1])
						if (command[0]=="#y_mul"):
							output.y_mul=float(command[1])
						if (command[0]=="#z_mul"):
							output.z_mul=float(command[1])
						if (command[0]=="#data_mul"):
							output.data_mul=float(command[1])
						if (command[0]=="#x_label"):
							output.x_label=command[1]
						if (command[0]=="#y_label"):
							output.y_label=command[1]
						if (command[0]=="#z_label"):
							output.z_label=command[1]
						if (command[0]=="#data_label"):
							output.data_label=command[1]
						if (command[0]=="#x_units"):
							output.x_units=command[1]
						if (command[0]=="#y_units"):
							output.y_units=command[1]
						if (command[0]=="#z_units"):
							output.z_units=command[1]
						if (command[0]=="#data_units"):
							output.data_units=command[1]
						if (command[0]=="#logscale_x"):
							output.logx=bool(int(command[1]))
						if (command[0]=="#logscale_y"):
							output.logy=bool(int(command[1]))
						if (command[0]=="#logscale_z"):
							output.logz=bool(int(command[1]))
						if (command[0]=="#logscale_data"):
							output.logdata=bool(int(command[1]))
						if (command[0]=="#type"):
							output.type=command[1]
						if (command[0]=="#title"):
							output.title=command[1]
						if (command[0]=="#section_one"):
							output.section_one=command[1]
						if (command[0]=="#section_two"):
							output.section_two=command[1]
						if (command[0]=="#time"):
							output.time=float(command[1])
						if (command[0]=="#Vexternal"):
							output.Vexternal=float(command[1])
						if (command[0]=="#data_max"):
							output.data_max=float(command[1])
						if (command[0]=="#data_min"):
							output.data_min=float(command[1])
						if (command[0]=="#x"):
							output.x_len=int(command[1])
							found_xyz=True
						if (command[0]=="#y"):
							output.y_len=int(command[1])
							found_xyz=True
						if (command[0]=="#z"):
							output.z_len=int(command[1])
							found_xyz=True
			if found_xyz==True and output.x_len != -1 and output.y_len != -1 and output.z_len != -1:
				return True
			else:
				return False
				
	return False

def guess_dim(lines):
	x=0
	y=0
	z=0
	data_started=False
	for i in range(0, len(lines)):
		temp=lines[i]
		temp=re.sub(' +',' ',temp)
		temp=re.sub("\t"," ",temp)
		temp=re.sub("\r","",temp)

		if len(temp)>0:
			if is_number(temp)==True:
				s=temp.split()
				l=len(s)
				if l>0:
					if len(s[l-1])>0:
						if s[l-1][0]=="#":
							l=l-1
				if l==1:
					print("I can't do this file type yet")
					return False,False,False
				if l==2:
					y=y+1
				if l==3:
					print("I can't do this file type yet")
					return False,False,False
	return 1,y,1

def is_number(data_in):
	if type(data_in)==str:
		if len(data_in)>0:
			s=data_in
			s=re.sub(' ','',s)
			s=re.sub("\+",'',s)
			s=re.sub('-','',s)
			s=re.sub('\t','',s)
	
			if len(s)>0:
				if s[0].isdigit()==True:
					return True
				else:
					return False

	return False

def dat_file_import_filter(out,file_name,x_col=0,y_col=1):
	"""This is an import filter for xy data"""
	lines=[]
	lines=inp_load_file(file_name)
	if lines==False:
		return False

	out.x_scale=[]
	out.y_scale=[]
	out.z_scale=[]
	out.data=[]
	data_started=False
	out.data=[[[0.0 for k in range(0)] for j in range(1)] for i in range(1)]

	for i in range(0, len(lines)):
		s,label=decode_line(lines[i])
		l=len(s)
		if l>0:

			if data_started==False:
				if is_number(s[0])==True:
					data_started=True

			if s[0]=="#end":
				break

			if data_started==True:
				if max(x_col,y_col)<l:
					out.y_scale.append(float(s[x_col]))
					out.data[0][0].append(float(s[y_col]))

	out.x_len=1
	out.y_len=len(out.data[0][0])
	out.z_len=1

	return True

def decode_line(line):
	label=False

	line=re.sub(' +',' ',line)
	line=re.sub('\t',' ',line)

	#check for labels at the end of the line
	if len(line)>0:
		if line[0]!="#":
			if line.count("#")>0:
				label=line.split("#")[1]
				line=line.split("#")[0]
				labels=True

	line=line.replace(',', '.')	#Remove European commas
	s=line.split()

	return s,label

def dat_file_read(out,file_name,guess=True):
	out.valid_data=False
	
	if file_name==None:
		return False
	
	found,lines=zip_get_data_file(file_name)
	if found==False:
		return False

	out.x_scale=[]
	out.y_scale=[]
	out.z_scale=[]
	out.data=[]

	if dat_file_load_info(out,lines)==False:
		if guess==True:
			out.x_len, out.y_len, out.z_len = guess_dim(lines)
		else:
			return False
		if out.x_len==False:
			print("No idea what to do with this file!",file_name)
			return False

	out.data=[[[0.0 for k in range(out.y_len)] for j in range(out.x_len)] for i in range(out.z_len)]
			
	out.x_scale= [0.0]*out.x_len
	out.y_scale= [0.0]*out.y_len
	out.z_scale= [0.0]*out.z_len
	out.labels=[]

	data_started=False

	x=0
	y=0
	z=0
	dim=0
	label=""
	labels=False
	#print(file_name)
	#print(lines)
	for line in lines:
		s,label=decode_line(line)
		l=len(s)
		if l>0:
							

			if data_started==False:
				if is_number(s[0])==True:
					data_started=True

			if s[0]=="#end":
				break

			if data_started==True:

				if line.count("nan")>0:
					#print("Warning nan found in data file",file_name)
					return False

				line_found=False
				if l==4:
					line_found=True
					out.data[z][x][y]=float(s[3])
					a0=s[0]
					a1=s[1]
					a2=s[2]

				if l==3:
					line_found=True
					out.data[z][x][y]=float(s[2])
					a0=s[0]
					a1=s[1]
					a2=0.0

				elif l==2:
					line_found=True
					out.data[z][x][y]=float(s[1])
					a0=s[0]
					a1=0.0
					a2=0.0

#				else:
#					print("skip")

				if line_found==True:
					if l==2:
						if x==0 and z==0:
							out.y_scale[y]=float(a0)

					if l==3:
						if x==0 and z==0:
							out.y_scale[y]=float(a1)
							
						if z==0 and y==0:
							out.x_scale[x]=float(a0)

					if l==4:
						if x==0 and z==0:
							out.y_scale[y]=float(a1)
							
						if z==0 and y==0:
							out.x_scale[x]=float(a0)

						if x==0 and y==0:
							out.z_scale[z]=float(a2)
					#if z==y:
					#	out.z_scale[y]=float(a0)
					if label!=False:
						out.labels.append(label)
					y=y+1
					if y==out.y_len:
						y=0
						x=x+1
					if x==out.x_len:
						x=0
						z=z+1

			if s[0]=="#data":
				data_started=True

	if data_started==False:
		return False

	out.valid_data=True
	return True
			

def read_data_2d(x_scale,y_scale,z,file_name):
	if file_name==None:
		return False
	
	found,lines=zip_get_data_file(file_name)
	if found==True:
		x_max=0
		y_max=0
		y_pos=0
		z_store=[]
		for i in range(0, len(lines)):
			if len(lines[i])>0:
				if lines[i][0]!="#" and lines[i]!="\n":
					temp=lines[i]
					temp=re.sub(' +',' ',temp)
					temp=re.sub('\t',' ',temp)
					temp=temp.rstrip()
					sline=temp.split(" ")

					if len(sline)==3:
						if x_max==0:
							y_scale.append(float(lines[i].split(" ")[1]))
						if y_pos==0:
							x_scale.append(float(lines[i].split(" ")[0]))

						z_store.append(float(lines[i].split(" ")[2]))
					y_pos=y_pos+1

					if x_max==0:
						y_max=y_max+1

			if lines[i]=="":
				x_max=x_max+1
				y_pos=0

		if  lines[len(lines)-1]!="\n":
			x_max=x_max+1

		x_max=len(x_scale)
		y_max=len(y_scale)

		pos=0
		for x in range(0, x_max):
			z.append([])
			for y in range(0, y_max):
				z[x].append(z_store[pos])
				pos=pos+1
		return True
	else:
		return False

def dat_file_print(dat):
	print("valid_data",dat.valid_data)
	print("grid",dat.grid)
	print("show_pointer",dat.show_pointer)
	print("logy",dat.logy)
	print("logx",dat.logx)
	print("logz",dat.logz)
	print("logdata",dat.logdata)
	print("label_data",dat.label_data)
	print("invert_y",dat.invert_y)
	print("normalize",dat.normalize)
	print("norm_to_peak_of_all_data",dat.norm_to_peak_of_all_data)
	print("subtract_first_point",dat.subtract_first_point)
	print("add_min",dat.add_min)
	print("legend_pos",dat.legend_pos)
	print("ymax",dat.ymax)
	print("ymin",dat.ymin)
	print("x_label",dat.x_label)
	print("y_label",dat.y_label)
	print("z_label",dat.z_label)
	print("data_label",dat.data_label)
	print("x_units",dat.x_units)
	print("y_units",dat.y_units)
	print("z_units",dat.z_units)
	print("data_units",dat.data_units)
	print("x_mul",dat.x_mul)
	print("y_mul",dat.y_mul)
	print("z_mul",dat.z_mul)
	print("data_mul",dat.data_mul)
	print("key_units",dat.key_units)
	print("file0",dat.file0)
	print("tag0",dat.tag0)
	print("file1",dat.file1)
	print("tag1",dat.tag1)
	print("file2",dat.file2)
	print("tag2",dat.tag2)
	print("example_file0",dat.example_file0)
	print("example_file1",dat.example_file1)
	print("example_file2",dat.example_file2)
	print("time",dat.time)
	print("Vexternal",dat.Vexternal)
	print("file_name",dat.file_name)
	print("other_file",dat.other_file)
	print("title",dat.title)
	print("type",dat.type)
	print("section_one",dat.section_one)
	print("section_two",dat.section_two)

	print("x_start",dat.x_start)
	print("x_stop",dat.x_stop)
	print("x_points",dat.x_points)
	print("y_start",dat.y_start)
	print("y_stop",dat.y_stop)
	print("y_points",dat.y_points)
	print("x_len",dat.x_len)
	print("y_len",dat.y_len)
	print("z_len",dat.z_len)
	
	print("x_scale",dat.x_scale)
	print("y_scale",dat.y_scale)
	print("z_scale",dat.z_scale)
	print("data",dat.data)
	print("labels",dat.labels)
