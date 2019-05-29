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

## @package shape
#  Shape object file.
#

import os
from inp import inp_load_file
from inp import inp_search_token_value
from inp import inp_callback_add_write_hook
from inp import inp_search_token_array
from cal_path import get_sim_path
from util import str2bool

class shape():
	def __init__(self):
		self.type="none"
		self.dx=1e-9
		self.dy=1e-9
		self.dz=1e-9

		self.shape_nx=1
		self.shape_nz=1
		self.file_name=None
		self.shape_dos="none"

		self.shape_x0=0.0
		self.shape_z0=0.0
		self.shape_remove_layer=False

		self.r=0.8
		self.g=0.8
		self.b=0.8



	def do_load(self):
		print(">>>>>>>>>>> do load",os.path.join(get_sim_path(),self.file_name))
		print(">>>>>> Doing shape load")
		lines=inp_load_file(self.file_name+".inp")

		if lines==False:
			return

		self.type=inp_search_token_value(lines, "#shape_type")
		self.dx=float(inp_search_token_value(lines, "#shape_dx"))
		self.dy=float(inp_search_token_value(lines, "#shape_dy"))
		self.dz=float(inp_search_token_value(lines, "#shape_dz"))

		rgb=inp_search_token_array(lines, "#red_green_blue")
		self.r=float(rgb[0])
		self.g=float(rgb[1])
		self.b=float(rgb[2])

		try:
			self.shape_nx=int(inp_search_token_value(lines, "#shape_nx"))
			self.shape_nz=int(inp_search_token_value(lines, "#shape_nz"))
			self.shape_name=inp_search_token_value(lines, "#shape_name")
			self.shape_dos=inp_search_token_value(lines, "#shape_dos")
			self.shape_x0=float(inp_search_token_value(lines, "#shape_x0"))

			self.shape_z0=float(inp_search_token_value(lines, "#shape_z0"))
			self.shape_remove_layer=str2bool(inp_search_token_value(lines, "#shape_remove_layer"))
		except:
			pass

	def load(self,file_name):
		if file_name=="none":
			return

		if file_name.endswith(".inp")==True:
			file_name=file_name[:-4]

		self.file_name=file_name
		self.do_load()

	def dump(self):
		print(self.file_name,self.type,self.width)
