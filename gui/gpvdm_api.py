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


## @package gpvdm_api
#  An api used to run gpvdm
#

#import sys
import os
import sys
import shutil
from shutil import copyfile
from cal_path import calculate_paths
from cal_path import calculate_paths_init
from cal_path import set_sim_path

calculate_paths_init()
calculate_paths()

from server import base_server
from server import server_get
from cal_path import get_sim_path
from progress_class import progress_class
from spectral2 import spectral2
from inp import inp_update_token_value
from inp import inp_get_token_value

#scan
from scan_item import scan_items_clear
from scan_item import scan_items_populate_from_known_tokens
from scan_item import scan_items_populate_from_files
from scan_io import scan_build_nested_simulation
from scan_io import build_scan
from cal_path import get_exe_command
from scan_tree import tree_load_program
from scan_tree import tree_load_flat_list
from gui_enable import set_gui
from scan_ml import scan_ml_build_vector
from scan_io import scan_archive
from multiplot import multiplot
from multiplot_from_tokens import multiplot_from_tokens


class api_scan():
	def build(self,scan_dir_path,base_dir):
		scan_items_clear()
		scan_items_populate_from_known_tokens()
		scan_items_populate_from_files()
		build_scan(scan_dir_path,base_dir)

	def build_nested(self,built_scan_dir,dir_to_insert):
		scan_items_clear()
		scan_items_populate_from_known_tokens()
		scan_items_populate_from_files()

		scan_dir_path=os.path.abspath(built_scan_dir)	#program file
		sim_to_nest=os.path.abspath(dir_to_insert)	#program file
		scan_build_nested_simulation(scan_dir_path,os.path.join(os.getcwd(),sim_to_nest))

	def run(self,scan_dir_path):
		exe_command=get_exe_command()
		program_list=tree_load_program(scan_dir_path)

		watch_dir=os.path.join(os.getcwd(),scan_dir_path)

		commands=[]
		#server_find_simulations_to_run(commands,scan_dir_path)
		commands=tree_load_flat_list(scan_dir_path)
		print(commands)
		
		myserver=base_server()
		myserver.base_server_init(watch_dir)

		for i in range(0, len(commands)):
			myserver.base_server_add_job(commands[i],"")
			print("Adding job"+commands[i])

		myserver.print_jobs()
		myserver.simple_run()
		#simple_run(exe_command)

	def build_ml_vectors(self,path):
		set_gui(False)
		scan_ml_build_vector(path)

	def archive(self,path):
		scan_archive(path)

class gpvdm_api():
	def __init__(self,verbose=True):
		self.save_dir=os.getcwd()
		self.my_server=base_server()
		if verbose==True:
			self.my_server.pipe_to_null=False
		else:
			self.my_server.pipe_to_null=True

		#self.my_server.base_server_init(get_sim_path())
		self.my_server=server_get()
		self.my_server.clear_cache()
		self.scan=api_scan()

		print("gpvdm_api")

	def run(self,callback=None):
		if callback!=None:
			self.my_server.base_server_set_callback(callback)
		self.my_server.start()

	def add_job(self,path=""):
		if path=="":
			path=get_sim_path()
		else:
			path=os.path.join(get_sim_path(),path)
		print("add path>",path)
		self.my_server.add_job(path,"")


	def set_sim_path(self,path):
		set_sim_path(path)

	def spectral2(self):
		s=spectral2()
		s.calc()

	def set_save_dir(self,path):
		if os.path.isdir(path)==False:
			os.makedirs(path)

		self.save_dir=path

	def save(self,dest,src):
		copyfile(src, os.path.join(self.save_dir,dest))

	def edit(self,file_name,token,value):
		inp_update_token_value(os.path.join(get_sim_path(),file_name),token,value)

	def get(self,file_name,token):
		return inp_get_token_value(os.path.join(get_sim_path(),file_name),token)

	def mkdir(self,file_name):
		if os.path.isdir(file_name)==False:
			os.mkdir(os.path.join(get_sim_path(),file_name))

	def clone(self,file_name):
		output_dir=os.path.join(get_sim_path(),file_name)
		if os.path.isdir(output_dir)==False:
			os.mkdir(output_dir)
		for f in os.listdir(get_sim_path()):
			if f.endswith(".inp") or f.endswith(".gpvdm"):
				copyfile(os.path.join(get_sim_path(),f), os.path.join(output_dir,f))

	def build_multiplot(self,path):
		a=multiplot()
		a.find_files(os.path.join(get_sim_path(),path))
		a.save()

	def graph_from_tokens(self,output_file,path,file0,token0,file1,token1):
		output_file=os.path.join(get_sim_path(),path,output_file)
		plot=multiplot_from_tokens()
		print("here")
		plot.gen_plot(os.path.join(get_sim_path(),path),file0,token0,file1,token1,output_file=os.path.join(get_sim_path(),output_file))


