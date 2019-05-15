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
from cal_path import get_sim_path

class shape():
	def __init__(self):
		self.type="none"
		self.width=1e-9
		self.file_name=None

	def do_load(self):
		print(">>>>>>>>>>> do load",os.path.join(get_sim_path(),self.file_name))
		lines=inp_load_file(self.file_name)

		if lines==False:
			return

		inp_callback_add_write_hook(self.file_name,self.do_load,"shape_a")

		self.type=inp_search_token_value(lines, "#shape_type")
		self.width=float(inp_search_token_value(lines, "#shape_width"))

	
	def load(self,file_name):
		if file_name=="none":
			return

		self.file_name=file_name+".inp"
		self.do_load()

	def dump(self):
		print(self.file_name,self.type,self.width)
