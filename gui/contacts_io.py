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
from inp import inp_load_file
from inp import inp_search_token_value
from inp import inp_save

from util import str2bool
from cal_path import get_sim_path

class segment():
	def __init__(self):
		self.name=""
		self.position=""
		self.active=False
		self.start=0.0
		self.depth=0.0
		self.voltage=0.0
		self.width=0.0

store=[]

def contacts_print():
	global store
	for s in store:
		print(s.start, s.width,s.depth,s.voltage,s.active)

def contacts_get_contacts():
	global store
	return len(store)

def contacts_get_array():
	global store
	return store

def contacts_clear():
	global store
	store=[]

def contacts_append(name,position,active,start,width,depth,voltage):
	global store
	s=segment()
	s.name=name
	s.position=position
	s.active=active
	s.start=start
	s.depth=depth
	s.voltage=voltage
	s.width=width
	store.append(s)

def contacts_dump():
	global store
	print("dump of contacts:")
	print(str(len(store)))
	i=0
	for s in store:
		print("#contact_name"+str(i))
		print(str(s.name))
		print("#contact_position"+str(i))
		print(str(s.position))
		print("#contact_active"+str(i))
		print(str(s.active))
		print("#contact_start"+str(i))
		print(str(s.start))
		print("#contact_width"+str(i))
		print(str(s.width))
		print("#contact_depth"+str(i))
		print(str(s.depth))
		print("#contact_voltage"+str(i))
		print(str(s.voltage))


def contacts_save():
	global store
	lines=[]
	lines.append("#contacts")
	lines.append(str(len(store)))
	i=0
	for s in store:
		lines.append("#contact_name"+str(i))
		lines.append(str(s.name))
		lines.append("#contact_position"+str(i))
		lines.append(str(s.position))
		lines.append("#contact_active"+str(i))
		lines.append(str(s.active))
		lines.append("#contact_start"+str(i))
		lines.append(str(s.start))
		lines.append("#contact_width"+str(i))
		lines.append(str(s.width))
		lines.append("#contact_depth"+str(i))
		lines.append(str(s.depth))
		lines.append("#contact_voltage"+str(i))
		lines.append(str(s.voltage))
		i=i+1
	lines.append("#ver")
	lines.append("1.1")
	lines.append("#end")
	
	inp_save(os.path.join(get_sim_path(),"contacts.inp"),lines)


def contacts_load():
	global store
	store=[]
	lines=[]
	pos=0
	lines=inp_load_file(os.path.join(get_sim_path(),"contacts.inp"))
	if lines!=False:
		pos=pos+1	#first comment
		layers=int(lines[pos])

		for i in range(0, layers):
			#name
			pos=pos+1					#token
			token=lines[pos]
			
			pos=pos+1
			name=lines[pos]			#read value

			#position
			pos=pos+1					#token
			token=lines[pos]
			
			pos=pos+1
			position=lines[pos]			#read value
			
			#active
			pos=pos+1					#token
			token=lines[pos]
			
			pos=pos+1
			active=lines[pos]			#read value
	
			#start
			pos=pos+1					#token
			token=lines[pos]

			pos=pos+1
			start=lines[pos]			#read value

			#width
			pos=pos+1					#token
			token=lines[pos]

			pos=pos+1
			width=lines[pos]			#read value

			#depth
			pos=pos+1					#token
			token=lines[pos]

			pos=pos+1
			depth=lines[pos]			#read value

			#voltage
			pos=pos+1					#token
			token=lines[pos]

			pos=pos+1
			voltage=lines[pos]			#read value


			contacts_append(name,position,str2bool(active),float(start),float(width),float(depth),float(voltage))

		#contacts_dump()

