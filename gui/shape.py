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
from inp import inp_search_token_array
from cal_path import get_sim_path
from str2bool import str2bool
from gui_enable import gui_get
if gui_get()==True:
	from file_watch import get_watch

from cal_path import get_shape_path
from dat_file import dat_file

from triangle_io import triangles_get_min
from triangle_io import triangles_get_max
from triangle_io import triangles_sub_vec
from triangle_io import triangles_div_vec
from triangle_io import triangles_mul_vec
from triangle import vec
from triangle_io import triangles_print 

class shape():

	def __init__(self,callback=None):
		self.callback=callback
		self.type="none"
		self.triangles=None
		self.dx=1e-9
		self.dy=1e-9
		self.dz=1e-9

		self.x0=0.0
		self.z0=0.0
		self.y0=0.0

		self.dx_padding=0.0
		self.dy_padding=0.0
		self.dz_padding=0.0

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

		self.shape_path=""



	def do_load(self):
		lines=inp_load_file(self.file_name+".inp")

		if lines==False:
			print("shape file not found: ",self.file_name)
			return
		self.type=inp_search_token_value(lines, "#shape_type")

		self.shape_path=os.path.join(get_shape_path(),self.type,"shape.inp")
		self.dx=float(inp_search_token_value(lines, "#shape_dx"))
		self.dy=float(inp_search_token_value(lines, "#shape_dy"))
		self.dz=float(inp_search_token_value(lines, "#shape_dz"))

		if os.path.isfile(self.shape_path)==True:
			self.triangles=dat_file()
			self.triangles.load(self.shape_path)
			if self.triangles.data!=None:
				min_vec=triangles_get_min(self.triangles.data)

				self.triangles.data=triangles_sub_vec(self.triangles.data,min_vec)

				max_vec=triangles_get_max(self.triangles.data)

				#triangles_print(self.triangles.data)

				self.triangles.data=triangles_div_vec(self.triangles.data,max_vec)

				#triangles_print(self.triangles.data)
				#print(max_vec)
				#print("bing")
				#v=vec()
				#v.x=1.0
				#v.y=-1.0
				#v.z=1.0

				#self.triangles.data=triangles_mul_vec(self.triangles.data,v)

				#min_vec=triangles_get_min(self.triangles.data)

				#v=vec()
				#v.x=0.0
				#v.y=min_vec.y
				#v.z=0.0

				#self.triangles.data=triangles_sub_vec(self.triangles.data,v)
		try:

					
			self.dx_padding=float(inp_search_token_value(lines, "#shape_padding_dx"))
			self.dy_padding=float(inp_search_token_value(lines, "#shape_padding_dy"))
			self.dz_padding=float(inp_search_token_value(lines, "#shape_padding_dz"))

			rgb=inp_search_token_array(lines, "#red_green_blue")
			self.r=float(rgb[0])
			self.g=float(rgb[1])
			self.b=float(rgb[2])


			self.shape_nx=int(inp_search_token_value(lines, "#shape_nx"))
			self.shape_nz=int(inp_search_token_value(lines, "#shape_nz"))
			self.shape_name=inp_search_token_value(lines, "#shape_name")
			self.shape_dos=inp_search_token_value(lines, "#shape_dos")
			self.x0=float(inp_search_token_value(lines, "#shape_x0"))

			self.z0=float(inp_search_token_value(lines, "#shape_z0"))
			self.y0=0.0

			self.shape_remove_layer=str2bool(inp_search_token_value(lines, "#shape_remove_layer"))
		except:
			pass

	def on_change(self):
		self.do_load()
		print("oh")
		if self.callback!=None:
			self.callback()

	def load(self,file_name):
		if file_name=="none":
			return

		if file_name.endswith(".inp")==True:
			file_name=file_name[:-4]

		self.file_name=file_name
		self.do_load()
		if gui_get()==True:
			get_watch().add_call_back(self.file_name+".inp",self.on_change)
			#get_watch().add_call_back(self.shape_path,self.do_load)

		

	def dump(self):
		print(self.file_name,self.type,self.width)
