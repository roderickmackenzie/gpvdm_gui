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
from inp import inp_load_file
from str2bool import str2bool
from triangle import triangle
from inp import inp_save_lines_to_file

def dat_files_to_gnuplot(out_dir,data):
	os.mkdir(out_dir)
	data_dir=os.path.join(out_dir,"data")
	os.mkdir(data_dir)

	makefile=[]
	makefile.append("main:")
	makefile.append("	gnuplot plot.plot >plot.eps")
	makefile.append("	gs -dNOPAUSE -r600 -dEPSCrop -sDEVICE=jpeg -sOutputFile=plot.jpg plot.eps -c quit")
	makefile.append("	xdg-open plot.jpg")
	inp_save_lines_to_file(os.path.join(out_dir,"makefile"),makefile)

	plotfile=[]
	plotfile.append("set term postscript eps enhanced color solid \"Helvetica\" 25")
	plotfile.append("set ylabel '"+data[0].data_label+" ("+data[0].data_units+")'")
	plotfile.append("set xlabel '"+data[0].y_label+" ("+data[0].y_units+")'")
	plotfile.append("set key top left")
	plotfile.append("set colors classic")
	if data[0].logdata==True:
		plotfile.append("set logscale y")
		plotfile.append("set format y \"%2.0t{/Symbol \\264}10^{%L}\"")
	else:
		plotfile.append("#set logscale y")
		plotfile.append("#set format y \"%2.0t{/Symbol \\264}10^{%L}\"")

	plotfile.append("plot \\")

	for i in range(0,len(data)):
		d=data[i]
		d.save_as_txt(os.path.join(data_dir,str(i)+".txt"))
		file_path=os.path.join("data",str(i)+".txt")
		file_path=d.file_name
		line="'"+file_path+"' using ($1):($2) with lp title '"+d.key_text+"'"
		print(i,len(data))
		if i<len(data)-1:
			line=line+",\\"

		plotfile.append(line)

	inp_save_lines_to_file(os.path.join(out_dir,"plot.plot"),plotfile)