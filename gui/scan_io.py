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

## @package scan_io
#  IO functions for the scanning simulation parameters.
#


import sys
import os
import shutil

from util import gpvdm_delete_file
from inp import inp_get_token_value
from scan_tree import tree_load_flat_list
from scan_tree import tree_gen_flat_list
from util import copy_scan_dir

from scan_tree import tree_load_program
from scan_tree import tree_gen
from scan_tree import tree_save_flat_list

from server_io import server_find_simulations_to_run


from progress import progress_class
from process_events import process_events
from server import server_break
from numpy import std

from error_dlg import error_dlg

import i18n
_ = i18n.language.gettext

from yes_no_cancel_dlg import yes_no_cancel_dlg

import zipfile
from util_zip import archive_add_dir

def scan_next_archive(sim_dir):
	i=0
	while(1):
		name="archive"+str(i)+".zip"
		full_name=os.path.join(sim_dir,name)
		if os.path.isfile(full_name)==False:
			return name
		i=i+1

def scan_archive(sim_dir):
	progress_window=progress_class()
	progress_window.show()
	progress_window.start()
	archive_path=os.path.join(sim_dir,"build_archive.zip")
	if os.path.isfile(archive_path)==True:
		os.remove(archive_path)
	zf = zipfile.ZipFile(archive_path, 'a',zipfile.ZIP_DEFLATED)

	l=os.listdir(sim_dir)
	for i in range(0,len(l)):
		dir_to_zip=os.path.join(sim_dir,l[i])
		if os.path.isdir(dir_to_zip)==True:
			archive_add_dir(archive_path,dir_to_zip,sim_dir,zf=zf,remove_src_dir=True)

		progress_window.set_fraction(float(i)/float(len(l)))
		progress_window.set_text(_("Adding: ")+l[i])

		#if server_break()==True:
		#	break
		process_events()
		
	zf.close()

	os.rename(archive_path, os.path.join(sim_dir,scan_next_archive(sim_dir)))

	progress_window.stop()

def scan_build_all_nested(sim_dir,parent_window=None):
	commands=scan_build_nested_simulation(sim_dir,os.path.join(os.getcwd(),"sub_sim"))
	commands=scan_build_nested_simulation(sim_dir,os.path.join(os.getcwd(),"sub_sim_tpc"))
	commands=scan_build_nested_simulation(sim_dir,os.path.join(os.getcwd(),"sub_sim_tpv"))


def build_scan(scan_path,base_path,parent_window=None):
	scan_clean_dir(scan_path,parent_window=parent_window)

	flat_simulation_list=[]
	program_list=tree_load_program(scan_path)
	path=os.getcwd()

	if tree_gen(flat_simulation_list,program_list,base_path,scan_path)==False:
		error_dlg(parent_window,_("Problem generating tree."))
		return False
	os.chdir(path)

	tree_save_flat_list(scan_path,flat_simulation_list)
		
def scan_delete_files(dirs_to_del,parent_window=None):
	if parent_window!=None:
		progress_window=progress_class()
		progress_window.show()
		progress_window.start()

		process_events()
	
	for i in range(0, len(dirs_to_del)):
		gpvdm_delete_file(dirs_to_del[i])
		if parent_window!=None:
			progress_window.set_fraction(float(i)/float(len(dirs_to_del)))
			progress_window.set_text("Deleting"+dirs_to_del[i])
			process_events()

	if parent_window!=None:
		progress_window.stop()

def scan_list_simulations(dir_to_search):
	found_dirs=[]
	for root, dirs, files in os.walk(dir_to_search):
		for name in files:
#			full_name=os.path.join(root, name)
			if name=="sim.gpvdm":
				found_dirs.append(root)
	return found_dirs

def scan_plot_fits(dir_to_search):
	files=os.listdir(dir_to_search)
	for i in range(0,len(files)):
		if files[i].endswith(".jpg"):
			os.remove(os.path.join(dir_to_search,files[i]))
			#print("remove",os.path.join(dir_to_search,files[i]))

	sim_dirs=tree_load_flat_list(dir_to_search)
	
	for i in range(0,len(sim_dirs)):
		os.chdir(sim_dirs[i])
		name=sim_dirs[i].replace("/","_")
		
		os.system("gnuplot fit.plot >plot.eps")
		os.system("gs -dNOPAUSE -r600 -dEPSCrop -sDEVICE=jpeg -sOutputFile="+os.path.join(dir_to_search,name+".jpg")+" plot.eps -c quit")
	os.chdir(dir_to_search)

def scan_get_converged_status(fit_log_path):
	error=False

	if os.path.isfile(fit_log_path):
		f = open(fit_log_path, "r")
		lines = f.readlines()
		f.close()

		for l in range(0, len(lines)):
			lines[l]=lines[l].rstrip()

		if len(lines)>4:
			error=float(lines[len(lines)-2].split()[1])
	
	return error

def scan_list_unconverged_simulations(dir_to_search):
	found_dirs=[]
	sim_dirs=tree_load_flat_list(dir_to_search)
	
	for i in range(0,len(sim_dirs)):
		add=False
		fit_log=os.path.join(sim_dirs[i],'fitlog.dat')

		error=scan_get_converged_status(fit_log)

		if error==False:
			add=True
		elif error>0.1:
			add=True

		if add==True:
			found_dirs.append(sim_dirs[i])

	return found_dirs

def scan_ask_to_delete(parent,dirs_to_del,parent_window=None):
	if (len(dirs_to_del)!=0):


		text_del_dirs=""
		if len(dirs_to_del)>30:
			for i in range(0,30,1):
				text_del_dirs=text_del_dirs+dirs_to_del[i]+"\n"
			text_del_dirs=text_del_dirs+_("and ")+str(len(dirs_to_del)-30)+_(" more.")
		else:
			for i in range(0,len(dirs_to_del)):
				text_del_dirs=text_del_dirs+dirs_to_del[i]+"\n"

		text=_("Should I delete these files?:\n")+"\n"+text_del_dirs

		response = yes_no_cancel_dlg(parent,text)

		if response == "yes":
			scan_delete_files(dirs_to_del,parent_window)
			return "yes"
		elif response == "no":
			return "no"
		elif response == "cancel":
			return "cancel"

class report_token():
	def __init__(self,file_name,token):
		self.file_name=file_name
		self.token=token
		self.values=[]

def scan_gen_report(path):
	tokens=[]
	tokens.append(report_token("dos0.inp","#Etrape"))
	tokens.append(report_token("dos0.inp","#mueffe"))
	tokens.append(report_token("dos0.inp","#Ntrape"))
	tokens.append(report_token("dos0.inp","#srhsigman_e"))
	tokens.append(report_token("dos0.inp","#srhsigmap_e"))
	tokens.append(report_token("dos0.inp","#srhsigman_h"))
	tokens.append(report_token("dos0.inp","#srhsigmap_h"))
	tokens.append(report_token("sim/thick_light/sim_info.dat","#jv_pmax_tau"))
	tokens.append(report_token("sim/thick_light/sim_info.dat","#jv_pmax_mue"))
	tokens.append(report_token("sim/thick_light/sim_info.dat","#jv_pmax_muh"))
	tokens.append(report_token("jv1.inp","#jv_Rcontact"))
	tokens.append(report_token("jv1.inp","#jv_Rshunt"))


	simulation_dirs=tree_load_flat_list(path)
	errors=[]
	for i in range(0,len(simulation_dirs)):
		print(simulation_dirs[i])

		error=scan_get_converged_status(os.path.join(simulation_dirs[i],"fitlog.dat"))
		print("error",error)
		errors.append(error)

		for ii in range(0,len(tokens)):
			value=inp_get_token_value(os.path.join(simulation_dirs[i],tokens[ii].file_name), tokens[ii].token)
			#print(os.path.join(simulation_dirs[i],tokens[ii].file_name), tokens[ii].token,value)
			if value!=None:
				print(tokens[ii].token,str(value))

				tokens[ii].values.append(float(value))

	print("Errors:",errors)
	for ii in range(0,len(tokens)):
		print(tokens[ii].token,tokens[ii].values,sum(tokens[ii].values)/len(tokens[ii].values),std(tokens[ii].values))

	for ii in range(0,len(tokens)):
		print(tokens[ii].token,sum(tokens[ii].values)/len(tokens[ii].values),std(tokens[ii].values))

#maybe delete
def scan_nested_simulation(root_simulation,nest_simulation):
	a=tree_gen_flat_list(root_simulation,level=1)
	print(a)
	return
	program_list=tree_load_program(nest_simulation)

	names=tree_load_flat_list(root_simulation)
	commands=[]

	flat_simulation_list=[]
	#tree_save_flat_list(self.sim_dir,flat_simulation_list)

	for i in range(0,len(names)):
		dest_name=os.path.join(root_simulation,names[i])
		tree_gen(flat_simulation_list,program_list,dest_name,dest_name)

		files = os.listdir(dest_name)
		for file in files:
			if file.endswith(".inp") or file.endswith(".gpvdm") or file.endswith(".dat") :
				os.remove(os.path.join(dest_name,file))

		print(names[i],flat_simulation_list)
	tree_save_flat_list(root_simulation,flat_simulation_list)

	return

def scan_build_nested_simulation(root_simulation,nest_simulation):

	progress_window=progress_class()
	progress_window.show()
	progress_window.start()

	process_events()

	program_list=tree_load_program(nest_simulation)
		
	files = os.listdir(root_simulation)
	simulations=[]
	for i in range(0,len(files)):
		if os.path.isfile(os.path.join(root_simulation,files[i],"sim.gpvdm"))==True:
			simulations.append(files[i])

	flat_simulation_list=[]

	path=os.getcwd()
	for i in range(0,len(simulations)):
		dest_name=os.path.join(root_simulation,simulations[i])
		tree_gen(flat_simulation_list,program_list,dest_name,dest_name)

		progress_window.set_fraction(float(i)/float(len(simulations)))
		progress_window.set_text(simulations[i])
		process_events()

	progress_window.stop()
	
	os.chdir(path)

	flat_simulation_list=tree_gen_flat_list(root_simulation,level=1)

	print(flat_simulation_list)
	tree_save_flat_list(root_simulation,flat_simulation_list)

	return

def scan_clean_nested_simulation(root_simulation,nest_simulation):
	files = os.listdir(root_simulation)
	simulations=[]
	for i in range(0,len(files)):
		if os.path.isfile(os.path.join(root_simulation,files[i],"sim.gpvdm"))==True:
			simulations.append(files[i])

	for i in range(0,len(simulations)):
		dest_name=os.path.join(root_simulation,simulations[i])

		files = os.listdir(dest_name)
		for file in files:
			if file.endswith(".inp") or file.endswith(".gpvdm") or file.endswith(".dat") :
				os.remove(os.path.join(dest_name,file))


	return
#def clean_simulation(parent_window,dir_to_clean):
#	files_to_delete=[]
#	listing=os.listdir(dir_to_clean)

#	for i in range(0,len(listing)):
#		if os.path.isdir(listing[i])==True:
#			files_to_delete.append(listing[i])
	
	#simulation_dirs=scan_list_simulations(dir_to_clean)

	#sims_we_should_have=tree_load_flat_list(dir_to_clean)
	#for i in range(0,len(simulation_dirs)):
		#if sims_we_should_have.count(simulation_dirs[i])==0:
			#files_to_delete.append(simulation_dirs[i])
		#else:
			#listing=os.listdir(simulation_dirs[i])

			#for ii in range(0,len(listing)):
				#delete=True
				#path=os.path.join(simulation_dirs[i],listing[ii])
				#if path.endswith(".inp"):
					#delete=False

				#if path.endswith("exp"):
					#delete=False

				#if path.endswith("materials"):
					#delete=False

				#if path.endswith(".gpvdm"):
					#delete=False

				#elif path.endswith(".gpvdm"):
					#delete=False

				#elif path.endswith("fitlog_time_error.dat"):
					#delete=False

				#elif path.endswith("fitlog_time_speed.dat"):
					#delete=False

				#elif path.endswith("fitlog_time_odes.dat"):
					#delete=False

				#elif path.endswith("fitlog.dat"):
					#delete=False

				#elif path.endswith("fitlog_speed.dat"):
					#delete=False

				#elif path.endswith("fiterror.dat"):
					#delete=False

				#if delete==True:
					##print("delete",path)
					#files_to_delete.append(path)

	#scan_ask_to_delete(parent_window,files_to_delete)

def scan_clean_dir(dir_to_clean,parent_window=None):
	dirs_to_del=[]
	listing=os.listdir(dir_to_clean)

	for i in range(0,len(listing)):
		full_path=os.path.join(dir_to_clean,listing[i])
		if os.path.isdir(full_path)==True:
			dirs_to_del.append(full_path)

	scan_ask_to_delete(parent_window,dirs_to_del,parent_window=parent_window)

def scan_clean_unconverged(parent,dir_to_clean):
		dirs_to_del=[]
		dirs_to_del=scan_list_unconverged_simulations(dir_to_clean)

		#print(dirs_to_del,dir_to_clean)

		scan_ask_to_delete(parent,dirs_to_del)

def scan_push_to_hpc(base_dir,only_unconverged):
	config_file=os.path.join(os.getcwd(),"server.inp")
	#print(config_file)
	hpc_path=inp_get_token_value(config_file, "#hpc_dir")
	hpc_path=os.path.abspath(hpc_path)

	if os.path.isdir(hpc_path)==True:
		hpc_files=[]
		hpc_files=scan_list_simulations(hpc_path)
		#print("hpc files=",hpc_files)
		scan_delete_files(hpc_files)
		files=[]

		if only_unconverged==True:
			files=scan_list_unconverged_simulations(base_dir)
		else:
			files=scan_list_simulations(base_dir)

		#print("copy files=",files)
		for i in range(0,len(files)):
			dest_path=os.path.join(hpc_path,files[i][len(base_dir)+1:])
			#print(dest_path)
			shutil.copytree(files[i], dest_path,symlinks=True)
	else:
		print("HPC dir not found",hpc_path)

def scan_import_from_hpc(base_dir):
	config_file=os.path.join(os.getcwd(),"server.inp")
	hpc_path=inp_get_token_value(config_file, "#hpc_dir")
	hpc_path=os.path.abspath(hpc_path)

	if os.path.isdir(hpc_path)==True:

		hpc_files=scan_list_simulations(hpc_path)

		for i in range(0,len(hpc_files)):
			if hpc_files[i].endswith("orig")==False:
				src_path=hpc_files[i]
				dest_path=os.path.join(base_dir,hpc_files[i][len(hpc_path)+1:])
				if os.path.isdir(dest_path):
					shutil.rmtree(dest_path)
				shutil.copytree(src_path, dest_path, symlinks=False, ignore=None)
				#print(src_path,dest_path)
	else:
		print("HPC dir not found",hpc_path)

def get_scan_dirs(scan_dirs,sim_dir):
	ls=os.listdir(sim_dir)

	for i in range(0, len(ls)):
		dir_name=os.path.join(sim_dir,ls[i])
		full_name=os.path.join(sim_dir,ls[i],"gpvdm_gui_config.inp")
		if os.path.isfile(full_name):
			scan_dirs.append(dir_name)


def delete_scan_dirs(path):
	sim_dirs=[]
	get_scan_dirs(sim_dirs,path)

	for my_file in sim_dirs:
		#print("Deleteing ",my_file)
		shutil.rmtree(my_file)

