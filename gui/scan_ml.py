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

## @package scan_ml
#  ML framework.
#

import sys
import os
import shutil

from util import gpvdm_delete_file
from inp import inp_get_token_value
from scan_tree import tree_load_flat_list
from util import copy_scan_dir

from server_io import server_find_simulations_to_run
from util_zip import read_lines_from_archive
from math import log10
from math import isnan

import i18n
_ = i18n.language.gettext

from progress_class import progress_class
from process_events import process_events
from server import server_break
from util_zip import zip_lsdir
from util_zip import extract_dir_from_archive

from inp import inp_get_token_value

import zipfile
import random
import string
import numpy as np

from gui_util import yes_no_dlg

from yes_no_cancel_dlg import yes_no_cancel_dlg

tindex=[]

def tindex_add(token,value):
	global tindex
	for i in range(0,len(tindex)):
		if tindex[i][0]==token:
			return
	tindex.append([token,value])		
	return

def tindex_dump(fname):
	global tindex

	f = open(fname, 'w')
	for i in range(0,len(tindex)):
		f.write(tindex[i][0]+" "+tindex[i][1]+'\n')
	f.close()

def make_vector_from_file(file_name,x_values):
	if os.path.isfile(file_name)==True:
		f=open(file_name,'r')
		lines = f.readlines()
		f.close()
	else:
		return False

	x=[]
	y=[]
	for i in range(0,len(lines)):
		if lines[i].startswith("#")==False:

			if lines[i].count("nan")!=0:
				return False

			if lines[i].count("inf")!=0:
				return False

			r=lines[i].split()
			if len(r)==2:
				try:
					x.append(float(r[0]))
					y.append(float(r[1]))
				except:
					return False
	

	x, y = zip(*sorted(zip(x, y)))

	r=np.interp(x_values,x,y)
	return r

def get_vectors(file_name,x_values,dolog=False,div=1.0,fabs=False,do_norm=False,mul=1.0):

	data=make_vector_from_file(file_name,x_values)

	if type(data)==bool:
		if data==False:
			return False
	

	if do_norm==True:
		mi=1e6
		for i in range(0,len(data)):
			if float(data[i])<mi:
				mi=float(data[i])
		div=mi

	n=[]
	for i in range(0,len(data)):
		#print(data[i])
		r=float(data[i])/div

		if fabs==True:
			r=abs(r)

		if dolog==True:
			#print(r)
			if r!=0.0:
				r=log10(r)
			else:
				r=0.0

		r=r*mul
		n.append(r)
	#print(n)

	s=""
	for ii in range(0,len(n)):
		s=s+'{:e}'.format(float(n[ii]))+" "

	return s

	

def scan_ml_build_token_abs(file_name,token0,token1,min_max="",dolog=False,mul=1.0,lim=-1.0):

	if token0==token1 and min_max=="min":
		return ""

	if token0==token1 and min_max=="max":
		return ""

	if min_max=="":
		temp=inp_get_token_value(file_name, token0)
		if temp==None:
			return False
		val=abs(float(temp))
	elif min_max=="max":
		temp=inp_get_token_value(file_name, token0)
		if temp==None:
			return False
		v0=abs(float(temp))

		temp=inp_get_token_value(file_name, token1)
		if temp==None:
			return False
		v1=abs(float(temp))

		val=v0
		if v1>v0:
			val=v1
	elif min_max=="min":
		temp=inp_get_token_value(file_name, token0)
		if temp==None:
			return False
		v0=abs(float(temp))
		
		temp=inp_get_token_value(file_name, token1)
		if temp==None:
			return False
		v1=abs(float(temp))

		val=v0
		if v1<v0:
			val=v1
	elif min_max=="avg":
		temp=inp_get_token_value(file_name, token0)
		if temp==None:
			return False
		v0=abs(float(temp))

		temp=inp_get_token_value(file_name, token1)
		if temp==None:
			return False
		v1=abs(float(temp))

		val=(v0+v1)/2.0

	v=[]
	s=""

	if lim!=-1:
		if val<lim:
			return False

	if dolog==True:
		if val!=0.0:
			#print("value=",val)
			val=log10(val)
			val=abs(val)
		else:
			val=0.0

	val=val*mul
	if isnan(val)==True:
		return False

	s=token0+"_"+min_max+"_abs\n"
	s=s+str(val)+"\n"

	full_token=token0+"_"+min_max+"_abs"

	tindex_add(full_token,str(-1))

	return s




def scan_ml_build_vector(sim_dir):
	output_file=os.path.join(sim_dir,"vectors.dat")
	if os.path.isfile(output_file)==True:
		response=yes_no_cancel_dlg(None,"The file "+output_file+" already exists.  Continue? ")

		if response!="yes":
			sys.exit(0)

	out=open(output_file,'wb')
	progress_window=progress_class()
	progress_window.show()
	progress_window.start()

	tot_archives=0
	for archive_name in os.listdir(sim_dir):
		if archive_name.startswith("archive")==True and archive_name.endswith(".zip")==True:
			tot_archives=tot_archives+1

	done=0

	errors=0
	for archive_name in os.listdir(sim_dir):

		if archive_name.startswith("archive")==True and archive_name.endswith(".zip")==True:

			archive_path=os.path.join(sim_dir,archive_name)

			if done==0:		#Find the measurment files and determine which ones are needed
				found=[]
				zf = zipfile.ZipFile(archive_path, 'r')
				items=zf.namelist()
				for l in items:
					parts=l.split("/")
					fname=parts[-1]
					if fname.endswith("scan.inp")==True:
						found_item=os.path.join(parts[-2],parts[-1])

						a=parts[-2]
						#measurment()
						#a.experiment=parts[-2]
						#a.measurement_file=parts[-1]
						#a.token="#ml_input_"+parts[-1][8:-4]+"_"+parts[-2]

						if found.count(a)==False:
							found.append(a)

			zf = zipfile.ZipFile(archive_path, 'r')
			dirs=zip_lsdir(archive_path,zf=zf,sub_dir="/")

			items=len(dirs)
			for i in range(0,len(dirs)):
				rnd = [random.choice(string.ascii_letters + string.digits) for n in range(0,32)]
				rnd = "".join(rnd)

				tmp_dir="/dev/shm/gpvdm_"+rnd
				if os.path.isdir(tmp_dir)==True:
					shutil.rmtree(tmp_dir)

				os.mkdir(tmp_dir)

				extract_dir_from_archive(tmp_dir,"",dirs[i],zf=zf)
	
				full_name=tmp_dir
				written=False
				#print(dirs[i])

				error=False
				v="#ml_id\n"
				v=v+dirs[i]+"\n"

				
				for scan_folder in found:
					token="#ml_input_"+scan_folder
					v=v+token+"\n"

					dolog=False
					div=1.0
					mul=1.0
					do_fabs=False

					sim_mode=inp_get_token_value(os.path.join(full_name,scan_folder,"sim.inp"), "#simmode")
					if sim_mode==None:
						error=True
						break
					sim_mode=sim_mode.lower()

					light=float(inp_get_token_value(os.path.join(full_name,scan_folder,"light.inp"), "#Psun"))

					if sim_mode.endswith("jv") or sim_mode.startswith("jv"):
						file_name="jv.dat"
						sim_mode="jv"
						vector=[0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]	#np.linspace(0.2,1.0,20)#

						#if light>0.0:
						#	div=1e2

						#if light==0.0:
						#	dolog=True

					elif sim_mode=="sun_voc":
						file_name="suns_voc.dat"
						vector=[0.02,0.04,0.05,0.1,0.5,0.7,1.0]
						#dolog=True
						#mul=-10.0

					elif sim_mode.startswith("tpc")==True:
						file_name="time_i.dat"
						vector=[1.1e-6,2e-6,2e-5,1e-4,0.02,0.1]
						#dolog=True
						#do_fabs=True
					elif sim_mode.startswith("celiv")==True:
						file_name="time_i.dat"
						vector=[2e-6,3e-6,4e-6,5e-6,6e-6,7e-6,8e-6]
						#do_fabs=True
						#mul=1000.0
					elif sim_mode.startswith("tpv")==True:
						file_name="time_v.dat"
						vector=[10e-6,20e-6,30e-6,40e-6,50e-6,60e-6,80e-6]
						#do_fabs=True
						#mul=10.0
					else:
						print(sim_mode)
						asdas
					ret=get_vectors(os.path.join(full_name,scan_folder,file_name),vector,dolog=dolog,div=div,mul=mul,fabs=do_fabs)
					#print(ret)
					if ret==False:
						error=True
						break
					v=v+ret+"\n"

					if sim_mode=="jv" and light>0.0:
						ret=scan_ml_build_token_abs(os.path.join(full_name,scan_folder,"sim_info.dat"),"#jv_pmax_tau","#jv_pmax_tau",min_max="avg",dolog=True)
						if ret==False:
							error=True
							break
						v=v+ret

						ret=scan_ml_build_token_abs(os.path.join(full_name,scan_folder,"sim_info.dat"),"#jv_pmax_mue","#jv_pmax_mue",min_max="avg",dolog=True)
						if ret==False:
							error=True
							break

						v=v+ret

						ret=scan_ml_build_token_abs(os.path.join(full_name,scan_folder,"sim_info.dat"),"#pce","#pce",min_max="avg",lim=0.1)
						if ret==False:
							error=True
							break

						v=v+ret

					#print(a.experiment,a.measurement_file,a.token)


				for min_max in ["min","max","avg"]:
					a=scan_ml_build_token_abs(os.path.join(full_name,"dos0.inp"),"#Etrape","#Etraph",min_max=min_max) #,mul=1e3
					if a==False:
						error=True
						break
					v=v+a

					a=scan_ml_build_token_abs(os.path.join(full_name,"dos0.inp"),"#mueffe","#mueffh",min_max=min_max) #,dolog=True
					if a==False:
						error=True
						break
					v=v+a

					a=scan_ml_build_token_abs(os.path.join(full_name,"dos0.inp"),"#Ntraph","#Ntrape",min_max=min_max) #,dolog=True
					if a==False:
						error=True
						break
					v=v+a

				a=scan_ml_build_token_abs(os.path.join(full_name,"parasitic.inp"),"#Rshunt","#Rshunt",min_max="avg") #,dolog=True
				if a==False:
					error=True
					break
				v=v+a

				a=scan_ml_build_token_abs(os.path.join(full_name,"parasitic.inp"),"#Rcontact","#Rcontact",min_max="avg")
				if a==False:
					error=True
					break
				v=v+a
		
				v=v+"#break\n"

				if error==False:
					out.write(str.encode(v))
					written=True
				else:
					errors=errors+1

				done=done+1


				progress_window.set_fraction(float(done)/float(len(dirs)*tot_archives))
				if written==True:
					progress_window.set_text(dirs[i])
				else:
					progress_window.set_text("                         /Last error: "+dirs[i]+" tot errors="+str(errors)+" "+str(round(100.0*errors/done,1))+"%")

				progress_window.set_text(dirs[i])

				#if server_break()==True:
				#	break
				process_events()
				#return

				shutil.rmtree(tmp_dir)

	out.close()
	progress_window.stop()

	tindex_dump(os.path.join(sim_dir,"index.dat"))


