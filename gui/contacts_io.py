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

## @package contacts_io
#  Back end to deal with contacts.
#

import os

from inp import inp
from inp import inp_save

from str2bool import str2bool
from cal_path import get_sim_path
from shape import shape

from gui_enable import gui_get


class segment():
	def __init__(self):
		self.name=""
		self.position=""
		self.active=False
		self.resistance_sq=0.0
		self.voltage=0.0
		self.np=1e20
		self.charge_type="electron"
		self.shape=None

	def save(self):
		self.shape.save()

		#contacts_dump()
class contacts_io():

	def __init__(self):
		self.contacts=[]

	#def init_watch(self):
	#	if gui_get()==True:
	#		get_watch().add_call_back("contacts.inp",self.em)

	def em(self):
		self.load()
		self.changed.emit()

	def load(self):
		self.contacts=[]

		pos=0
		contact_file=inp()
		if contact_file.load(os.path.join(get_sim_path(),"contacts.inp"))!=False:
			layers=int(contact_file.get_next_val())

			for i in range(0, layers):
				name=contact_file.get_next_val()

				position=contact_file.get_next_val()

				active=contact_file.get_next_val()

				voltage=contact_file.get_next_val()

				charge_density=contact_file.get_next_val()

				charge_type=contact_file.get_next_val()

				shape_file_name=contact_file.get_next_val()

				resistance_sq=contact_file.get_next_val()

				#print(depth,voltage,charge_density)
				self.contact_load(name,position,str2bool(active),float(voltage),float(charge_density), charge_type,shape_file_name)

	def get_shape_files(self):
		ret=[]
		for c in self.contacts:
			ret.append(c.shape.file_name+".inp")
		return ret

	def print():
		for s in self.contacts:
			print(s.shape.x0, s.shape.dx,s.depth,s.voltage,s.active)

	def clear():
		self.contacts=[]

	def contact_load(self,name,position,active,voltage,np,charge_type,shape_file_name):
		s=segment()
		s.name=name
		s.position=position
		s.active=active
		s.voltage=voltage
		s.np=np
		s.charge_type=charge_type
		s.shape=shape()
		s.shape.load(shape_file_name)
		self.contacts.append(s)

	def gen_file(self):
		lines=[]
		lines.append("#contacts")
		lines.append(str(len(self.contacts)))
		i=0
		for s in self.contacts:
			lines.append("#contact_name"+str(i))
			lines.append(str(s.name))
			lines.append("#contact_position"+str(i))
			lines.append(str(s.position))
			lines.append("#contact_active"+str(i))
			lines.append(str(s.active))
			lines.append("#contact_voltage"+str(i))
			lines.append(str(s.voltage))
			lines.append("#contact_charge_density"+str(i))
			lines.append(str(s.np))
			lines.append("#contact_charge_type"+str(i))
			lines.append(str(s.charge_type))
			lines.append("#contact_shape_file_name"+str(i))
			lines.append(s.shape.file_name)
			lines.append("#contact_resistance_sq"+str(i))
			lines.append(str(s.resistance_sq))


			i=i+1

		lines.append("#ver")
		lines.append("1.3")
		lines.append("#end")

		return lines


	def dump(self):
		lines=self.gen_file()
		for s in lines:
			print(s)


	def save(self):
		lines=self.gen_file()
		inp_save(os.path.join(get_sim_path(),"contacts.inp"),lines)

		for c in self.contacts:
			c.save()

	def remove(self,index):
		self.contacts.pop(index)

	def insert(self,pos,shape_file_name):
		s=segment()
		s.name="new_contact"
		s.position="top"
		s.active=False
		s.voltage=0.0
		s.np=1e25
		s.charge_type="electron"
		s.shape=shape()
		s.shape.load(shape_file_name)
		s.shape.type="box"
		self.contacts.insert(pos,s)
		return self.contacts[pos]

