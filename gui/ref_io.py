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

## @package ref_io
#  Back end IO for the reference manager window.
#

import os
from inp import inp_load_file
from inp import inp_get_token_value_from_list

class ref:
	def __init__(self):
		self.group=""
		self.author=""
		self.journal=""
		self.title=""
		self.volume=""
		self.pages=""
		self.year=""
		self.doi=""
		self.unformatted=""
		self.website=""

def load_ref(file_name):
	r=ref()
	#we could have zipped the file
	archive=os.path.basename(os.path.dirname(file_name))+".zip"

	file_name=os.path.splitext(file_name)[0]+".ref"

	#if os.path.isfile(file_name)==False:
	#	return None

	lines=inp_load_file(file_name,archive=archive)

	#print(file_name,lines)
	if lines==False:
		return None

	text=""

	r.website=inp_get_token_value_from_list(lines, "#ref_website")
	if r.website==None:
		r.website=""

	r.group=inp_get_token_value_from_list(lines, "#ref_research_group")
	if r.group==None:
		r.group=""
		
	r.author=inp_get_token_value_from_list(lines, "#ref_authors")
	if r.author==None:
		r.author=""

	r.journal=inp_get_token_value_from_list(lines, "#ref_jounral")
	if r.journal==None:
		r.journal=""

	r.title=inp_get_token_value_from_list(lines, "#ref_title")
	if r.title==None:
		r.title=""

	r.volume=inp_get_token_value_from_list(lines, "#ref_volume")
	if r.volume==None:
		r.volume=""

	r.pages=inp_get_token_value_from_list(lines, "#ref_pages")
	if r.pages==None:
		r.pages=""

	r.year=inp_get_token_value_from_list(lines, "#ref_year")
	if r.year==None:
		r.year=""

	r.doi=inp_get_token_value_from_list(lines, "#ref_doi")
	if r.doi==None:
		r.doi=""

	r.unformatted=inp_get_token_value_from_list(lines, "#ref_unformatted")
	if r.unformatted==None:
		r.unformatted=""

	return r
	
