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

import yaml

def scale(c):
	#return c
	if c<=0.031308:
		c=c*12.92
	else:
		c=1.055*pow(c,1.0/2.4)-0.055
	return c

def n_to_rgb(n_x,n_y,alpha_x,alpha_y,fname=None):
	w=[390e-9,395e-9,400e-9,405e-9,410e-9,415e-9,420e-9,425e-9,430e-9,435e-9,440e-9,445e-9,450e-9,455e-9,460e-9,465e-9,470e-9,475e-9,480e-9,485e-9,490e-9,495e-9,500e-9,505e-9,510e-9,515e-9,520e-9,525e-9,530e-9,535e-9,540e-9,545e-9,550e-9,555e-9,560e-9,565e-9,570e-9,575e-9,580e-9,585e-9,590e-9,595e-9,600e-9,605e-9,610e-9,615e-9,620e-9,625e-9,630e-9,635e-9,640e-9,645e-9,650e-9,655e-9,660e-9,665e-9,670e-9,675e-9,680e-9,685e-9,690e-9,695e-9,700e-9,705e-9,710e-9,715e-9,720e-9,725e-9,730e-9,735e-9,740e-9,745e-9,750e-9,755e-9,760e-9,765e-9,770e-9,775e-9,780e-9,785e-9,790e-9,795e-9,800e-9,805e-9,810e-9,815e-9,820e-9,825e-9,830e-9]
	x0=[0.0023616,0.0072423,0.0191097,0.0434,0.084736,0.140638,0.204492,0.264737,0.314679,0.357719,0.383734,0.386726,0.370702,0.342957,0.302273,0.254085,0.195618,0.132349,0.080507,0.041072,0.016172,0.005132,0.003816,0.015444,0.037465,0.071358,0.117749,0.172953,0.236491,0.304213,0.376772,0.451584,0.529826,0.616053,0.705224,0.793832,0.878655,0.951162,1.01416,1.0743,1.11852,1.1343,1.12399,1.0891,1.03048,0.95074,0.856297,0.75493,0.647467,0.53511,0.431567,0.34369,0.268329,0.2043,0.152568,0.11221,0.0812606,0.05793,0.0408508,0.028623,0.0199413,0.013842,0.00957688,0.0066052,0.00455263,0.0031447,0.00217496,0.0015057,0.00104476,0.00072745,0.000508258,0.00035638,0.000250969,0.00017773,0.00012639,9.0151e-05,6.45258e-05,4.6339e-05,3.34117e-05,2.4209e-05,1.76115e-05,1.2855e-05,9.41363e-06,6.913e-06,5.09347e-06,3.7671e-06,2.79531e-06,2.082e-06,1.55314e-06]
	y0=[0.0002534,0.0007685,0.0020044,0.004509,0.008756,0.014456,0.021391,0.029497,0.038676,0.049602,0.062077,0.074704,0.089456,0.106256,0.128201,0.152761,0.18519,0.21994,0.253589,0.297665,0.339133,0.395379,0.460777,0.53136,0.606741,0.68566,0.761757,0.82333,0.875211,0.92381,0.961988,0.9822,0.991761,0.99911,0.99734,0.98238,0.955552,0.915175,0.868934,0.825623,0.777405,0.720353,0.658341,0.593878,0.527963,0.461834,0.398057,0.339554,0.283493,0.228254,0.179828,0.140211,0.107633,0.081187,0.060281,0.044096,0.0318004,0.0226017,0.0159051,0.0111303,0.0077488,0.0053751,0.00371774,0.00256456,0.00176847,0.00122239,0.00084619,0.00058644,0.00040741,0.000284041,0.00019873,0.00013955,9.8428e-05,6.9819e-05,4.9737e-05,3.55405e-05,2.5486e-05,1.83384e-05,1.3249e-05,9.6196e-06,7.0128e-06,5.1298e-06,3.76473e-06,2.77081e-06,2.04613e-06,1.51677e-06,1.12809e-06,8.4216e-07,6.297e-07]
	z0=[0.0104822,0.032344,0.0860109,0.19712,0.389366,0.65676,0.972542,1.2825,1.55348,1.7985,1.96728,2.0273,1.9948,1.9007,1.74537,1.5549,1.31756,1.0302,0.772125,0.57006,0.415254,0.302356,0.218502,0.159249,0.112044,0.082248,0.060709,0.04305,0.030451,0.020584,0.013676,0.007918,0.003988,0.001091,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
	sun=[54.6482,68.7015,82.7549,87.1204,91.486,92.4589,93.4318,90.057,86.6823,95.7736,104.865,110.936,117.008,117.41,117.812,116.336,114.861,115.392,115.923,112.367,108.811,109.082,109.354,108.578,107.802,106.296,104.79,106.239,107.689,106.047,104.405,104.225,104.046,102.023,100.0,98.1671,96.3342,96.0611,95.788,92.2368,88.6856,89.3459,90.0062,89.8026,89.5991,88.6489,87.6987,85.4936,83.2886,83.4939,83.6992,81.863,80.0268,80.1207,80.2146,81.2462,82.2778,80.281,78.2842,74.0027,69.7213,70.6652,71.6091,72.979,74.349,67.9765,61.604,65.7448,69.8856,72.4863,75.087,69.3398,63.5927,55.0054,46.4182,56.6118,66.8054,65.0941,63.3828,63.8434,64.304,61.8779,59.4519,55.7054,51.959,54.6998,57.4406,58.8765,60.3125]
#[1137721.59073,1169620.6907,1634639.11394,1709764.51107,1574713.95908,1860015.30534,1721792.35963,1932863.58551,1364985.64832,1959877.58842,2139516.81524,2333947.57104,2506969.5349,2462984.19875,2489453.25059,2511640.54405,2481278.98458,2677072.11805,2690695.89473,2619073.75446,2718527.32424,2771076.17715,2606228.4793,2646515.9332,2626858.7697,2605060.72701,2598054.21329,2697313.15769,2646515.9332,2666562.34746,2548813.99185,2657998.83069,2656247.20226,2701984.16684,2553095.75024,2638147.04181,2576840.04674,2573920.66602,2618684.50369,2673568.86118,2397006.19454,2504828.65571,2584235.81123,2611483.36459,2576256.1706,2579564.80208,2588322.94423,2465319.70333,2450138.9236,2542780.60504,2522734.19077,2563216.27006,2393697.56306,2378322.15794,2465514.32871,2505023.28109,2501520.02423,2459870.19266,2462011.07185,2423864.49714,2091444.34609,2245587.64798,2264660.93534,2333363.69489,2326551.80655,2224178.85605,1750460.67828,1843900.32378,2003473.6738,2160536.35641,2164039.61327,2219507.84691,2194011.92197,2203353.94027,481036.092109,1233477.27827,2071981.80798,2102148.74206,2079961.4486,2072565.68412,1955011.95389,1959099.0869,1924047.05575,1893121.08268,1897363.91599,1613969.89846,1555037.33304,1746801.72111,1652953.36231]
	r=[]
	n=numpy.interp(w, n_x, n_y, left=0.0, right=0.0)
	#for i in range(0,len(n)):
	#	n[i]=1.0
	#for i in range(0,20):
	#	n[i]=10.0

	alpha=numpy.interp(w, alpha_x, alpha_y, left=0.0, right=0.0)
	for i in range(0,len(w)):
		n_comp=complex(n[i],(w[i]*alpha[i]/(4.0*3.1415926)))
		l_r=(1.0-n_comp)/(1.0+n_comp)
		l_r=abs(l_r)
		reflected=pow(l_r,2.0)
		#print("rod>>",n_comp,l_r,reflected)
		reflected=reflected*sun[i]
		r.append(reflected)


	if fname!=None:
		text_file = open(fname, "w")
		for i in range(0,len(w)):
			text_file.write(str(w[i])+" "+str(r[i])+"\n")
		text_file.close()
	x=0
	y=0
	z=0
	for i in range(0,len(w)):
		x=x+x0[i]*r[i]
		y=y+y0[i]*r[i]
		z=z+z0[i]*r[i]
		#print(x0[i]*r[i],y0[i]*r[i],z0[i]*r[i])
	tot=x+y+z
	print(x,y,z,tot,len(w))
	x=x/tot
	y=y/tot
	z=z/tot

	r =  3.2404542*x - 1.5371385*y - 0.4985314*z
	g = -0.9692660*x + 1.8760108*y + 0.0415560*z
	b =  0.0556434*x - 0.2040259*y + 1.0572252*z


	r=scale(r)
	g=scale(g)
	b=scale(b)

	#print(r,g,b)
	return str(r),str(g),str(b)

def process_yml_file(dest,yml_src_file):
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
					r=settingsMap['DATA'][0]['range'].split()
					r0=float(r[0])*1e-6
					r1=float(r[1])*1e-6
					delta=(r1-r0)/2000.0

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
				src_file=os.path.join(src_dir,"generic","air")
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

				zip_remove_file(path,"n_eq.inp")
				zip_remove_file(path,"alpha_eq.inp")

				zip_remove_file(path,"n_gen.gmat")
				zip_remove_file(path,"alpha_gen.gmat")

				zip_remove_file(path,"fit.inp")
				zip_remove_file(path,"dos.inp")
				zip_remove_file(path,"pl.inp")

				ref=settingsMap['REFERENCES']
				inp_update_token_value("n.ref","#ref_website","refractiveindex.info",archive=path+"")
				inp_update_token_value("n.ref","#ref_unformatted",ref,archive=path)
				inp_update_token_value("n.ref","#ref_authors","",archive=path)
				
				inp_update_token_value("alpha.ref","#ref_website","refractiveindex.info",archive=path)
				inp_update_token_value("alpha.ref","#ref_unformatted",ref,archive=path)
				inp_update_token_value("alpha.ref","#ref_authors","",archive=path)

				r,g,b=n_to_rgb(n_x,n_y,alpha_x,alpha_y)
		
				inp_update_token_array(os.path.join(dest,"mat.inp"),"#red_green_blue",[r,g,b])

			else:
				print(settingsMap['DATA'][0]['type'])

	return

def refractiveindex_info_sync():
	search_path=os.path.join(get_materials_path(),"refractiveindex.info","database","data")
	if os.path.isdir(search_path)==False:
		print("Put the refractiveindex.info database in if you want it imported"+ search_path)
		return

	for root, dirnames, filenames in os.walk(search_path):
		for file_name in fnmatch.filter(filenames, '*.yml'):
			yml_file=os.path.join(root, file_name)

			rel_path=os.path.relpath(yml_file, search_path)[:-4]
			dest=os.path.join(get_materials_path(),"refractiveindex.info",rel_path)
			#print(yml_file,rel_path,divert(rel_path))
			process_yml_file(dest,yml_file)

	return
