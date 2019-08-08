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

## @package scan_tree
#  Logic to itterate though a scan tree.
#
import os
import shutil
import glob
import random
from random import randint

from inp import inp_update_token_value
from scan_item import scan_items_index_item
from inp import inp_get_token_value
from inp import inp_get_token_array
from str2bool import str2bool
from util import get_cache_path
from cal_path import get_materials_path
from scan_item import scan_items_get_file
from scan_item import scan_items_get_token
from clone import gpvdm_clone
#windows
import codecs
from util_zip import archive_decompress
from util_zip import archive_compress

from cal_path import subtract_paths

from progress import progress_class
from process_events import process_events


def tree_load_flat_list(sim_dir):
	config=[]
	file_name=os.path.join(sim_dir,'flat_list.inp')

	if os.path.isfile(file_name)==False:
		return False

	f = open(file_name)
	lines = f.readlines()
	f.close()

	for i in range(0, len(lines)):
		lines[i]=lines[i].rstrip()

	number=int(lines[0])

	for i in range(1,number+1):
		lines[i]=os.path.join(sim_dir,lines[i])
		if os.path.isdir(lines[i]):
			config.append(lines[i])

	return config

def tree_save_flat_list(sim_dir,flat_list):
	config=[]
	file_name=os.path.join(sim_dir,'flat_list.inp')

	a = open(file_name, "w")
	a.write(str(len(flat_list))+"\n")
	for i in range(0,len(flat_list)):
		rel_dir=subtract_paths(sim_dir,flat_list[i])
		a.write(rel_dir+"\n")

	a.close()

	return config

def tree_gen_flat_list(dir_to_search,level=0):
	found_dirs=[]
	for root, dirs, files in os.walk(dir_to_search):
		for name in files:

			if name=="sim.gpvdm":
				full_name=os.path.join(root, name)
				f=subtract_paths(dir_to_search,full_name)
				f=os.path.dirname(f)
				if len(f.split("/"))>level:
					found_dirs.append(f)
	return found_dirs

def tree_load_program(sim_dir):

	program_list=[]

	file_name=os.path.join(sim_dir,'gpvdm_gui_config.inp')

	if os.path.isfile(file_name)==True:
		f=open(file_name)
		config = f.readlines()
		f.close()

		for ii in range(0, len(config)):
			config[ii]=config[ii].rstrip()

		pos=0
		mylen=int(config[0])
		pos=pos+1

		for i in range(0, mylen):
			program_list.append([config[pos],config[pos+1],config[pos+3], config[pos+4]])
			pos=pos+6
	return program_list

def tree_load_config(sim_dir):
	return


def build_scan_tree(program_list):
	tree_items=[[],[],[]]	#file,token,values,opp
	for i in range(0,len(program_list)):
		#print(i,program_list[i][0],program_list[i][1],program_list[i][2],program_list[i][3])
		if program_list[i][3]=="scan":
			tree_items[0].append(program_list[i][0])
			tree_items[1].append(program_list[i][1])
			values=program_list[i][2]
			#This expands a [ start stop step ] command.
			if len(values)>0:
				if values[0]=='[' and values[len(values)-1]==']':
					values=values[1:len(values)-1]
					data=values.split()
					if len(data)==3:
						a=float(data[0])
						b=float(data[1])
						c=float(data[2])
						values=""
						pos=a
						while pos<b:
							values=values+str(pos)+" "
							pos=pos+c
						values=values[0:len(values)-1]

			tree_items[2].append(values)

	return tree_items

def tree_gen(flat_simulation_list,program_list,base_dir,sim_dir):
	sim_dir=os.path.abspath(sim_dir)	# we are about to traverse the directory structure better to have the abs path
	#print("here",program_list)
	found_scan=False
	found_random=False
	for i in range(0,len(program_list)):
		if program_list[i][3]=="scan":
			found_scan=True

		if program_list[i][3]=="random_file_name":
			found_random=True

	if found_scan==True and found_random==True:
		return False

	if found_random==True:
		tree_gen_random_files(sim_dir,flat_simulation_list,program_list,base_dir)
		return

	tree_items=build_scan_tree(program_list)			#tree_items[3].append(program_list[i][3])

	ret=tree(flat_simulation_list,program_list,tree_items,base_dir,0,sim_dir,"","")

	return ret

def tree_apply_duplicate(directory,program_list):
	for i in range(0, len(program_list)):
		#print(program_list[i])
		if program_list[i][2]=="duplicate":
			print(program_list[i])
			f=scan_items_get_file(program_list[i][3])
			t=scan_items_get_token(program_list[i][3])

			print(os.path.join(directory,f), t)
			src_value=inp_get_token_value(os.path.join(directory,f), t)
			print(os.path.join(directory,program_list[i][0]), program_list[i][1], src_value)
			inp_update_token_value(os.path.join(directory,program_list[i][0]), program_list[i][1], src_value)
			#print("duplicate to",os.path.join(directory,program_list[i][0]), program_list[i][1])
	return True

def tree_apply_constant(directory,program_list):
	for i in range(0, len(program_list)):
		if program_list[i][3]=="constant":
			inp_update_token_value(os.path.join(directory,program_list[i][0]), program_list[i][1], program_list[i][2])

	return True

def tree_apply_python_script(directory,program_list):
	for i in range(0, len(program_list)):
		if program_list[i][3]=="python_code":

			ret=""
			command=program_list[i][2]
			ret=eval(command)
			file_path=os.path.join(directory,program_list[i][0])
			#print("EXEC=",command,">",ret,"<")
			error_status=inp_update_token_value(file_path, program_list[i][1], ret)
			if error_status==False:
				return False

	return True

def copy_simulation(base_dir,cur_dir):
	gpvdm_clone(cur_dir,src_archive=os.path.join(base_dir, "sim.gpvdm"),dest="file")
	


def tree_gen_random_files(sim_path,flat_simulation_list,program_list,base_dir):
	length=0

	for i in range(0,len(program_list)):
		if program_list[i][3]=="random_file_name":
			length=int(program_list[i][2])

	progress_window=progress_class()
	progress_window.show()
	progress_window.start()

	process_events()

	for i in range(0,length):
		rand=codecs.encode(os.urandom(int(16 / 2)), 'hex').decode()
		cur_dir=os.path.join(sim_path,rand)

		if not os.path.exists(cur_dir):
			os.makedirs(cur_dir)
			gpvdm_clone(cur_dir,src_archive=os.path.join(base_dir, "sim.gpvdm"),dest="file")

			os.chdir(cur_dir)
			archive_decompress(os.path.join(cur_dir,"sim.gpvdm"))
			if tree_apply_constant(cur_dir,program_list)==False:
				return False

			if tree_apply_python_script(cur_dir,program_list)==False:
				return False

			tree_apply_duplicate(cur_dir,program_list)
			
			archive_compress(os.path.join(cur_dir,"sim.gpvdm"))

			flat_simulation_list.append(cur_dir)

			progress_window.set_fraction(float(i)/float(length))
			progress_window.set_text("Adding "+cur_dir)
			process_events()

	progress_window.stop()

def tree(flat_simulation_list,program_list,tree_items,base_dir,level,path,var_to_change,value_to_change):
	#print(level,tree_items)
	values=tree_items[2][level]
	values=values.split()

	if tree_items[0][level]=="notknown":
		return False

	if tree_items[1][level]=="notknown":
		return False

	pass_var_to_change=var_to_change+" "+str(level)
	#print(pass_var_to_change)
	for ii in values:
		cur_dir=os.path.join(path,ii)

		if not os.path.exists(cur_dir):
			os.makedirs(cur_dir)

		pass_value_to_change=value_to_change+" "+ii

		if ((level+1)<len(tree_items[0])):
				ret=tree(flat_simulation_list,program_list,tree_items,base_dir,level+1,cur_dir,pass_var_to_change,pass_value_to_change)
				if ret==False:
					return False
		else:
			flat_simulation_list.append(cur_dir)
			new_values=pass_value_to_change.split()
			pos=pass_var_to_change.split()

			config_file=os.path.join(cur_dir,"sim.gpvdm")
			if os.path.isfile(config_file)==False:	#Don't build a simulation over something that exists already
				copy_simulation(base_dir,cur_dir)
				os.chdir(cur_dir)
				if tree_apply_constant(cur_dir,program_list)==False:
					return False

				if tree_apply_python_script(cur_dir,program_list)==False:
					return False

				for i in range(0, len(pos)):
					file_path=os.path.join(cur_dir,tree_items[0][int(pos[i])])
					inp_update_token_value(file_path, tree_items[1][int(pos[i])], new_values[i])
					#print("updating", file_path, tree_items[1][int(pos[i])], new_values[i])

				tree_apply_duplicate(cur_dir,program_list)

				inp_update_token_value(os.path.join(cur_dir,"dump.inp"), "#plot", "0")

		if level==0:
			f = open(os.path.join(cur_dir,'scan.inp'),'w')
			f.write("data")
			f.close()
	return True
