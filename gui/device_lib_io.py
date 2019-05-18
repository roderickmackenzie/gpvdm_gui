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

## @package device_lib_io
#  Make changes to the device lib enmass.
#

import os
import glob
from cal_path import get_device_lib_path
from util_zip import archive_add_file
from util_zip import zip_remove_file
from inp import inp_update_token_value
from inp import inp_delete_token
from inp import inp_insert_token
from inp import inp_insert_duplicate

def find_device_libs():
	out=[]
	for root, dirs, files in os.walk(get_device_lib_path()):
		for name in files:
			if name.endswith(".gpvdm")==True:
				out.append(os.path.join(root, name))

	return out

def device_lib_replace(file_name,dir_name=""):
	if dir_name=="":
		dir_name=get_device_lib_path()
	archives=glob.glob(os.path.join(dir_name,"*.gpvdm"))
	for i in range(0,len(archives)):
		print("replace ",archives[i],file_name)
		archive_add_file(archives[i],file_name,"")

def device_lib_delete(file_name,dir_name=""):
	if dir_name=="":
		dir_name=get_device_lib_path()
	archives=glob.glob(os.path.join(dir_name,"*.gpvdm"))
	for i in range(0,len(archives)):
		zip_remove_file(archives[i],file_name)

def device_lib_token_change(file_name,token,value):
	archives=find_device_libs()
	for i in range(0,len(archives)):
		sim_file_name=os.path.join(os.path.dirname(archives[i]),file_name)
		archive=os.path.basename(archives[i])
		#inp_update_token_value(file_path, token, replace,archive="sim.gpvdm",id="")
		print(sim_file_name,archive)
		inp_update_token_value(sim_file_name, token, value,archive=archives[i])


def device_lib_token_delete(file_name,token):
	archives=find_device_libs()
	for i in range(0,len(archives)):
		sim_file_name=os.path.join(os.path.dirname(archives[i]),file_name)
		archive=os.path.basename(archives[i])
		#inp_update_token_value(file_path, token, replace,archive="sim.gpvdm",id="")
		print(sim_file_name,archive)
		inp_delete_token(sim_file_name, token, archive=archives[i])

def device_lib_token_insert(file_name,token_to_insert_after,token,value):
	archives=find_device_libs()
	for i in range(0,len(archives)):
		sim_file_name=os.path.join(os.path.dirname(archives[i]),file_name)
		archive=os.path.basename(archives[i])
		#inp_update_token_value(file_path, token, replace,archive="sim.gpvdm",id="")
		print(sim_file_name,archive)
		inp_insert_token(sim_file_name, token_to_insert_after, token, value, archive=archives[i])

def device_lib_token_duplicate(dest_file, dest_token, src_file, src_token):
	archives=find_device_libs()
	for i in range(0,len(archives)):
		path_to_src_file=os.path.join(os.path.dirname(archives[i]),src_file)
		path_to_dest_file=os.path.join(os.path.dirname(archives[i]),dest_file)

		archive=os.path.basename(archives[i])
		#inp_update_token_value(file_path, token, replace,archive="sim.gpvdm",id="")
		print(path_to_src_file,path_to_dest_file)
		inp_insert_duplicate(path_to_dest_file, dest_token, path_to_src_file, src_token,archive=archives[i])
		#inp_update_token_value(sim_file_name, token, value,archive=archives[i])

