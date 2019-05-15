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

## @package clone
#  Clone a simulation
#
#import sys
import os
import shutil
#import glob
from cal_path import get_inp_file_path
from util_zip import zip_lsdir
from util_zip import read_lines_from_archive
from util_zip import write_lines_to_archive
from util_zip import archive_make_empty
from shutil import copyfile
from inp import inp_search_token_value
from cal_path import get_materials_path
from cp_gasses import copy_gasses
from materials_io import find_materials
from cal_path import find_light_source
from cal_path import get_spectra_path

def gpvdm_clone(path,src_archive="",copy_dirs=False,dest="archive"):
	if src_archive=="":
		src_dir=get_inp_file_path()
		src_archive=os.path.join(src_dir,"base.gpvdm")
		
	dest_archive=os.path.join(path,"sim.gpvdm")
	files=zip_lsdir(src_archive)
	lines=[]

	archive_make_empty(dest_archive)

	for i in range(0,len(files)):
		if files[i].endswith(".inp"):
			lines=read_lines_from_archive(src_archive,files[i])
			write_lines_to_archive(dest_archive,files[i],lines,dest=dest)


	if copy_dirs==True:
		if os.path.isdir(os.path.join(src_dir,"plot")):
			shutil.copytree(os.path.join(src_dir,"plot"), os.path.join(path,"plot"))

		if os.path.isdir(os.path.join(src_dir,"exp")):
			shutil.copytree(os.path.join(src_dir,"exp"), os.path.join(path,"exp"))

		#if os.path.isdir(os.path.join(src_dir,"materials")):
		#	shutil.copytree(os.path.join(src_dir,"materials"), os.path.join(path,"materials"))

		#clone_materials(path)
		clone_spectras(path)

def clone_material(dest_material_dir,src_material_dir):
	if os.path.isdir(dest_material_dir)==False:
		try:
			os.makedirs(dest_material_dir)
		except:
			return False

	files=os.listdir(src_material_dir)
	for i in range(0,len(files)):
		src_mat_file=os.path.join(src_material_dir,files[i])
		if os.path.isfile(src_mat_file)==True:
			copyfile(src_mat_file,os.path.join(dest_material_dir,files[i]))
	return True

def clone_spectra(dest_spectra_dir,src_spectra_dir):
	if os.path.isdir(dest_spectra_dir)==False:
		os.mkdir(dest_spectra_dir)

	for copy_file in ["spectra_gen.inp","spectra.inp","mat.inp","spectra_eq.inp"]:
		src_spectra_file=os.path.join(src_spectra_dir,copy_file)
		if os.path.isfile(src_spectra_file)==True:
			copyfile(src_spectra_file,os.path.join(dest_spectra_dir,copy_file))
			
def clone_materials(dest):
	src_dir=os.path.join(get_materials_path())
	dest_dir=os.path.join(dest,"materials")
	if os.path.isdir(dest_dir)==False:
		os.makedirs(dest_dir)

	copy_gasses(dest_dir,src_dir)

	files=find_materials()
	for i in range(0,len(files)):
		src_file=os.path.join(src_dir,files[i])
		dest_file=os.path.join(dest_dir,files[i])

		clone_material(dest_file,src_file)

def clone_spectras(dest):
	src_dir=os.path.join(get_spectra_path())
	dest_dir=os.path.join(dest,"spectra")
	if os.path.isdir(dest_dir)==False:
		os.mkdir(dest_dir)

	files=find_light_source()
	for i in range(0,len(files)):
		src_file=os.path.join(src_dir,files[i])
		dest_file=os.path.join(dest_dir,files[i])
		clone_spectra(dest_file,src_file)
