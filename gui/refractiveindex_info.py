# -*- coding: utf-8 -*-
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

import os
import re
import time
import sys
import random
import fnmatch
import numpy
from cal_path import get_materials_path
from clone import clone_material
from util_zip import write_lines_to_archive
from util_zip import zip_remove_file
from inp import inp_update_token_value
from util_zip import read_lines_from_archive
from math import sqrt
from inp import inp_update_token_array
from n_to_rgb import n_to_rgb
import yaml
from util_zip import read_lines_from_file

def scale(c):
	#return c
	if c<=0.031308:
		c=c*12.92
	else:
		c=1.055*pow(c,1.0/2.4)-0.055
	return c


def process_yml_file(dest,yml_src_file):
	print(dest)
	found=False
	lam=[]
	n=[]
	alpha=[]
	settings_stream=open(yml_src_file, 'r')
	print("Importing",yml_src_file,dest)
	settingsMap=yaml.safe_load(settings_stream)
	for main in settingsMap:
		if main=="DATA":
			lines_n=[]
			n_x=[]
			n_y=[]
			n_x_vis=[]
			n_y_vis=[]
			lines_n.append("#gpvdm")
			lines_n.append("#title Refractive index")
			lines_n.append("#type xy")
			lines_n.append("#x_mul 1e9")
			lines_n.append("#y_mul 1e9")
			lines_n.append("#x_mul 1e9")
			lines_n.append("#data_mul 1e9")
			lines_n.append("#x_label Wavelength")
			lines_n.append("#data_label Refractive index")
			lines_n.append("#x_units nm")
			lines_n.append("#data_units m^{-1}")
			lines_n.append("#logscale_x 0")
			lines_n.append("#logscale_y 0")
			lines_n.append("#section_one Materials")
			lines_n.append("#section_two Refractive index")
			lines_n.append("#data")

			lines_alpha=[]
			alpha_x=[]
			alpha_y=[]
			alpha_x_vis=[]
			alpha_y_vis=[]
			lines_alpha.append("#gpvdm")
			lines_alpha.append("#title Absorption")
			lines_alpha.append("#type xy")
			lines_alpha.append("#x_mul 1e9")
			lines_alpha.append("#y_mul 1e9")
			lines_alpha.append("#z_mul 1e9")
			lines_alpha.append("#data_mul 1.000000")
			lines_alpha.append("#x_label Wavelength")
			lines_alpha.append("#data_label Absorption")
			lines_alpha.append("#x_units nm")
			lines_alpha.append("#data_units m^{-1}")
			lines_alpha.append("#logscale_x 0")
			lines_alpha.append("#logscale_y 0")
			lines_alpha.append("#section_one Materials")
			lines_alpha.append("#section_two Absorption")
			lines_alpha.append("#data")

			understood_n=False
			understood_alpha=False

			if settingsMap['DATA'][0]['type']=="tabulated nk":
				lines=settingsMap['DATA'][0]['data'].split("\n")

				for i in range(0,len(lines)):
					l=lines[i].split()
					if len(l)==3:
						try:
							lam=float(l[0])*1e-6
							n=float(l[1])
							alpha=4*3.14159*float(l[2])/lam
							n_x.append(lam)
							n_y.append(n)
						
							alpha_x.append(lam)
							alpha_y.append(alpha)
						except:
							pass
				understood_n=True
				understood_alpha=True

			elif len(settingsMap['DATA'])>1:
				if settingsMap['DATA'][0]['type'].startswith("formula")==True:
					#print(settingsMap['DATA'][0])
					r=settingsMap['DATA'][0]['wavelength_range'].split()
					r0=float(r[0])*1e-6
					r1=float(r[1])*1e-6
					#print("range",r0*1e9,r1*1e9)
					delta=(r1-r0)/2000.0
					delta_vis=(r1-r0)/2000.0

					c=settingsMap['DATA'][0]['coefficients'].split()
					cf=[]
					for v in c:
						cf.append(float(v))
					c=cf
					c0=c[0]
					c.pop(0)

				if (settingsMap['DATA'][0]['type']=="formula 3"):
					lam=r0
					while(lam<r1):
						n2=c0
						for i in range(0,int(len(c)/2)):
							#print(n2,c[(i*2)],lam,c[(i*2)+1])
							n2=n2+c[(i*2)]*pow((lam/1e-6),c[(i*2)+1])

						#print(n2)
						n=sqrt(n2)

						n_x.append(lam)
						n_y.append(n)
					
						lam=lam+delta
					#print(lines_n)
					understood_n=True

				if (settingsMap['DATA'][0]['type']=="formula 2"):
					lam=r0
					while(lam<r1):
						n2=c0+1
						for i in range(0,int(len(c)/2)):
							n2=n2+(c[(i*2)]*pow((lam/1e-6),2.0))/(pow((lam/1e-6),2.0)-pow(c[(i*2)+1],2.0))

						#print(n2)
						n=sqrt(n2)
						n_x.append(lam)
						n_y.append(n)

						lam=lam+delta
					#print(lines_n)
					understood_n=True

				if (settingsMap['DATA'][0]['type']=="formula 5"):
					lam=r0
					while(lam<r1):
						n=c0
						for i in range(0,int(len(c)/2)):
							#print(n2,c[(i*2)],lam,c[(i*2)+1])
							n=n+c[(i*2)]*pow((lam/1e-6),c[(i*2)+1])

						#print(n2)
						#n=sqrt(n2)
						n_x.append(lam)
						n_y.append(n)

						lam=lam+delta
					#print(lines_n)
					understood_n=True

				if (settingsMap['DATA'][1]['type']=="tabulated k"):
					lines=settingsMap['DATA'][1]['data'].split("\n")
					for i in range(0,len(lines)):
						l=lines[i].split()
						#print(len(l))
						if len(l)==2:
							lam=float(l[0])*1e-6
							alpha=4*3.14159*float(l[1])/lam
							alpha_x.append(lam)
							alpha_y.append(n)

					#print(lines_alpha)
					understood_alpha=True

			if understood_n==True and understood_alpha==True:
				src_dir=get_materials_path()
				src_file=os.path.join(src_dir,"generic","default")
				path=dest

				clone_material(path,src_file)
				
				for i in range(0,len(n_x)):
					lines_n.append(str(n_x[i])+" "+str(n_y[i]))

				for i in range(0,len(alpha_x)):
					lines_alpha.append(str(alpha_x[i])+" "+str(alpha_y[i]))

				path=dest+"/sim.gpvdm"

				write_lines_to_archive(path,"alpha.gmat",lines_alpha,mode="l",dest="file")
				write_lines_to_archive(path,"n.gmat",lines_n,mode="l",dest="file")
				zip_remove_file(path,"cost.xlsx")

				zip_remove_file(path,"fit.inp")
				zip_remove_file(path,"dos.inp")
				zip_remove_file(path,"pl.inp")
				zip_remove_file(path,"homo.inp")
				zip_remove_file(path,"lumo.inp")

				ref=settingsMap['REFERENCES']
				inp_update_token_value("n.ref","#ref_website","refractiveindex.info",archive=path+"")
				inp_update_token_value("n.ref","#ref_unformatted",ref,archive=path)
				inp_update_token_value("n.ref","#ref_authors","",archive=path)
				
				inp_update_token_value("alpha.ref","#ref_website","refractiveindex.info",archive=path)
				inp_update_token_value("alpha.ref","#ref_unformatted",ref,archive=path)
				inp_update_token_value("alpha.ref","#ref_authors","",archive=path)

				r,g,b=n_to_rgb(n_x,n_y,alpha_x,alpha_y)
		
				inp_update_token_array(os.path.join(dest,"mat.inp"),"#red_green_blue",[r,g,b])
				inp_update_token_value(os.path.join(dest,"mat.inp"),"#mat_src","refractive_index.info")

			else:
				print("Not understood",settingsMap['DATA'][0]['type'])

	return

class decode_mat():
	def __init__(self):
		self.name=""
		self.path=""
	def dump(self):
		print(self.name,self.path)

def gen_path(path,id_string,mat_folder):
	pos=path.find(id_string)
	if pos==0:
		return path
	s=path[pos:]
	return mat_folder+s

#	s=path.split(mat_type)
#	return mat_type+s[1]

def decode_path(path):
	if path.startswith("glass")==True:
		return gen_path(path,"glass","glass")

	if path.startswith("other")==True:
		return gen_path(path,"other","other")

	if path.startswith("organic")==True:
		return gen_path(path,"organic","organic")

	print(path)

	types=[]
	type_file=os.path.join(get_materials_path(),"src","type_list.inp")
	lines=read_lines_from_file(type_file)
	for l in lines:
		if l.count(",")>0:
			s=l.split(",")
			a=decode_mat()
			a.name="/"+s[0]+"/"
			a.path=s[1]
			#a.dump()
			types.append(a)
	for t in types:
		if path.count(t.name)>0:
			print(path,t.name,t.path)
			return gen_path(path,t.name,t.path)

	if path.startswith("main")==True:
		return gen_path(path,"main","extra")

	return os.path.join(path,"extra","extra")
	
def refractiveindex_info_sync():
	search_path=os.path.join(get_materials_path(),"src","refractiveindex.info","data")
	if os.path.isdir(search_path)==False:
		print("Put the refractiveindex.info database in if you want it imported"+ search_path)
		return

	for root, dirnames, filenames in os.walk(search_path):
		for file_name in fnmatch.filter(filenames, '*.yml'):
			yml_file=os.path.join(root, file_name)

			rel_path=os.path.relpath(yml_file, search_path)[:-4]
			decoded_path=decode_path(rel_path)
			dest=os.path.join(get_materials_path(),decoded_path)
			#print(yml_file,rel_path,divert(rel_path))
			process_yml_file(dest,yml_file)

	return
