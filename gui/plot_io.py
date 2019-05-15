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

## @package plot_io
#  Back end for the plot files
#


import os
from inp import inp_load_file
from inp import inp_search_token_value
from util_zip import zip_get_data_file
from util import str2bool
from inp import inp_save_lines_to_file

def plot_load_info(plot_token,file_name_in):
	#print "whoo",file_name_in
	#file_name=os.path.splitext(file_name_in)[0]+".dat"
	if get_plot_file_info(plot_token,file_name_in)==False:
		return False

	config_file=os.path.splitext(file_name_in)[0]+".oplot"
	ret=plot_load_oplot_file(plot_token,config_file)

	return True

def plot_load_oplot_file(plot_token,file_name):
	lines=inp_load_file(file_name)
	if lines!=False:
		plot_token.logy=str2bool(inp_search_token_value(lines, "#logy"))
		plot_token.logx=str2bool(inp_search_token_value(lines, "#logx"))
		plot_token.logz=str2bool(inp_search_token_value(lines, "#logz"))
		plot_token.grid=str2bool(inp_search_token_value(lines, "#grid"))
		plot_token.invert_y=str2bool(inp_search_token_value(lines, "#invert_y"))
		plot_token.normalize=str2bool(inp_search_token_value(lines, "#normalize"))
		plot_token.norm_to_peak_of_all_data=str2bool(inp_search_token_value(lines, "#norm_to_peak_of_all_data"))
		plot_token.subtract_first_point=str2bool(inp_search_token_value(lines, "#subtract_first_point"))
		plot_token.add_min=str2bool(inp_search_token_value(lines, "#add_min"))
		plot_token.file0=inp_search_token_value(lines, "#file0")
		plot_token.file1=inp_search_token_value(lines, "#file1")
		plot_token.file2=inp_search_token_value(lines, "#file2")
		plot_token.tag0=inp_search_token_value(lines, "#tag0")
		plot_token.tag1=inp_search_token_value(lines, "#tag1")
		plot_token.tag2=inp_search_token_value(lines, "#tag2")
		plot_token.legend_pos=inp_search_token_value(lines, "#legend_pos")
		plot_token.key_units=inp_search_token_value(lines, "#key_units")
		plot_token.label_data=str2bool(inp_search_token_value(lines, "#label_data"))
		plot_token.type=inp_search_token_value(lines, "#type")
		plot_token.x_label=inp_search_token_value(lines, "#x_label")
		plot_token.y_label=inp_search_token_value(lines, "#y_label")
		plot_token.z_label=inp_search_token_value(lines, "#z_label")
		plot_token.data_label=inp_search_token_value(lines, "#data_label")
		plot_token.x_units=inp_search_token_value(lines, "#x_units")
		plot_token.y_units=inp_search_token_value(lines, "#y_units")
		plot_token.y_units=inp_search_token_value(lines, "#z_units")
		plot_token.data_units=inp_search_token_value(lines, "#data_units")
		plot_token.x_mul=float(inp_search_token_value(lines, "#x_mul"))
		plot_token.y_mul=float(inp_search_token_value(lines, "#y_mul"))
		plot_token.z_mul=float(inp_search_token_value(lines, "#z_mul"))
		plot_token.data_mul=float(inp_search_token_value(lines, "#data_mul"))
		plot_token.key_units=inp_search_token_value(lines, "#key_units")
		plot_token.x_start=float(inp_search_token_value(lines, "#x_start"))
		plot_token.x_stop=float(inp_search_token_value(lines, "#x_stop"))
		plot_token.x_points=float(inp_search_token_value(lines, "#x_points"))
		plot_token.y_start=float(inp_search_token_value(lines, "#y_start"))
		plot_token.y_stop=float(inp_search_token_value(lines, "#y_stop"))
		plot_token.y_points=float(inp_search_token_value(lines, "#y_points"))
		plot_token.time=float(inp_search_token_value(lines, "#time"))
		plot_token.Vexternal=float(inp_search_token_value(lines, "#Vexternal"))

		return True
	return False

def gen_header_from_token(plot_token,full=False,single_line=True):
	lines=[]
	lines.append("#title")
	lines.append(str(plot_token.title))
	lines.append("#type")
	lines.append(str(plot_token.type))
	lines.append("#x_mul")
	lines.append(str(plot_token.x_mul))
	lines.append("#y_mul")
	lines.append(str(plot_token.y_mul))
	lines.append("#z_mul")
	lines.append(str(plot_token.z_mul))
	lines.append("#data_mul")
	lines.append(str(plot_token.data_mul))
	lines.append("#x_label")
	lines.append(str(plot_token.x_label))
	lines.append("#y_label")
	lines.append(str(plot_token.y_label))
	lines.append("#z_label")
	lines.append(str(plot_token.z_label))
	lines.append("#data_label")
	lines.append(str(plot_token.data_label))
	lines.append("#x_units")
	lines.append(str(plot_token.x_units))
	lines.append("#y_units")
	lines.append(str(plot_token.y_units))
	lines.append("#z_units")
	lines.append(str(plot_token.z_units))
	lines.append("#data_units")
	lines.append(str(plot_token.data_units))
	lines.append("#logy")
	lines.append(str(plot_token.logy))
	lines.append("#logx")
	lines.append(str(plot_token.logx))
	lines.append("#logz")
	lines.append(str(plot_token.logz))
	lines.append("#time")
	lines.append(str(plot_token.time))
	lines.append("#Vexternal")
	lines.append(str(plot_token.Vexternal))
	lines.append("#x")
	lines.append(str(plot_token.x_len))
	lines.append("#y")
	lines.append(str(plot_token.y_len))
	lines.append("#z")
	lines.append(str(plot_token.z_len))

	if full==True:
		lines.append("#grid")
		lines.append(str(plot_token.grid))
		lines.append("#invert_y")
		lines.append(str(plot_token.invert_y))
		lines.append("#normalize")
		lines.append(str(plot_token.normalize))
		lines.append("#norm_to_peak_of_all_data")
		lines.append(str(plot_token.norm_to_peak_of_all_data))
		lines.append("#subtract_first_point")
		lines.append(str(plot_token.subtract_first_point))
		lines.append("#add_min")
		lines.append(str(plot_token.add_min))
		lines.append("#file0")
		lines.append(str(plot_token.file0))
		lines.append("#file1")
		lines.append(str(plot_token.file1))
		lines.append("#file2")
		lines.append(str(plot_token.file2))
		lines.append("#tag0")
		lines.append(str(plot_token.tag0))
		lines.append("#tag1")
		lines.append(str(plot_token.tag1))
		lines.append("#tag2")
		lines.append(str(plot_token.tag2))
		lines.append("#legend_pos")
		lines.append(str(plot_token.legend_pos))
		lines.append("#key_units")
		lines.append(str(plot_token.key_units))
		lines.append("#label_data")
		lines.append(str(plot_token.label_data))
		lines.append("#key_units")
		lines.append(str(plot_token.key_units))
		lines.append("#x_start")
		lines.append(str(plot_token.x_start))
		lines.append("#x_stop")
		lines.append(str(plot_token.x_stop))
		lines.append("#x_points")
		lines.append(str(plot_token.x_points))
		lines.append("#y_start")
		lines.append(str(plot_token.y_start))
		lines.append("#y_stop")
		lines.append(str(plot_token.y_stop))
		lines.append("#y_points")
		lines.append(str(plot_token.y_points))
	
	if single_line==True:
		l=[]
		for i in range(0,int(len(lines)/2)):
			l.append(lines[i*2]+" "+lines[(i*2)+1])

		lines=l

		lines.append("#begin")

	return lines

def plot_save_oplot_file(config_file,plot_token):
	save_name=config_file
	if save_name!="":
		if save_name.endswith(".oplot")==False:
			save_name=save_name.split(".")[0]+".oplot"

		lines=gen_header_from_token(plot_token,full=True,single_line=False)
		lines.append("#ver")
		lines.append("1.0")
		lines.append("#end")

		#print(lines)
		inp_save_lines_to_file(save_name,lines)

def get_plot_file_info(output,file_name):
	found,lines=zip_get_data_file(file_name)
	#print(file_name)
	if found==False:
		print("can't find file",file_name)
		return False

	for i in range(0, len(lines)):
		lines[i]=lines[i].rstrip()


	if len(lines)>1:
		if lines[0]=="#gpvdm":
			for i in range(0, len(lines)):
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
						if (command[0]=="#x"):
							output.x_len=int(command[1])
						if (command[0]=="#y"):
							output.y_len=int(command[1])
						if (command[0]=="#z"):
							output.z_len=int(command[1])

			return True

	return False
