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

## @package bibtex
#  A bibtex parser for gpvdm
#

import os
from inp import inp
from inp import inp_save_lines_to_file

class bib_item:
	def __init__(self):
		self.type=""
		self.token=""
		self.vars=["author","title","url","journal","volume","number","pages","year","DOI","publisher","address","booktitle","isbn","unformatted"]
		for var in self.vars:
			setattr(self, var, "")

	def short_cite(self):
		build=""
		if self.title!="":
			build=build+self.title+", "

		if self.journal!="":
			build=build+self.journal+", "

		if self.volume!="":
			build=build+self.volume+", "

		if self.pages!="":
			build=build+self.pages+", "

		if self.year!="":
			build=build+self.year+", "

		build=build[:-2]

		return build

	def decode(self,lines):
		l=lines[0][1:]
		if l[-1]==",":
			l=lines[0][:-1]

		l=l.split("{")
		self.type=l[0]
		self.token=l[1]
		if len(lines)<=2:
			return

		lines=lines[1:-1]
		lines[-1]=lines[-1]+","

		wait_for="="
		build=""
		for l in lines:
			ls=l.rstrip()
			for i in range(0,len(ls)):
				c=ls[i]
				if wait_for==",end":
					if c=="," and i==(len(ls)-1):
						build_strip=build.strip()
						if build_strip[0]=="\"":
							build_strip=build_strip[1:]
						if build_strip[-1]=="\"":
							build_strip=build_strip[:-1]

						text=build_strip
						if hasattr(self, token):
							if text.startswith("{") and text.endswith("}"):
								text=text[1:-1]
							setattr(self,token,text)

						wait_for="="
						build=""

						#print("token=",token)
						#print("text=",text)
					else:
						build=build+c

				elif wait_for=="=":
					if c=="=":
						token=build.strip()
						wait_for=",end"
						build=""
					else:
						build=build+c
					

						
		new_lines=[]

		#self.dump()

	def __str__(self):
		build="@"+self.type+"{"+self.token+",\n"

		for var in self.vars:
			val=getattr(self, var)
			#print(var)
			if val!="" and val!=False:
				build=build+" "+var+" = \""+val+"\",\n"

		build=build[:-2]
		build=build+"\n}"
		return build

	def dump(self):
		print(str(self))

	def get_text(self,html=True):
		text=""
		if self.title=="":
			return self.unformatted

		if html==True:
			text=text+"<b>"+_("Associated paper")+":</b>"+self.author+", "+self.title+", "+self.journal+", "+self.volume+", "+self.pages+", "+self.year+"<br>"
			if self.DOI!="":
				text=text+"<b>doi link:</b> <a href=\"http://doi.org/"+self.DOI+"\"> http://doi.org/"+self.DOI+"</a>"
		else:
			text=text+self.author+", "+self.journal+", "+self.title+", "+self.volume+", "+self.pages+", "+self.year+" "+self.DOI

		return text



class bibtex:
	def __init__(self):
		self.refs=[]

	def load(self,file_name):
		f=inp()
		if f.load(file_name)==False:
			return False

		bracket=0
		within=False
		ref_lines=[]
		for l in f.lines:
			if l.lstrip().startswith("@"):
				if bracket!=0:
					print("error parsing bibtex file")
				within=True
				ref_lines=[]

			bracket=bracket+l.count("{")
			bracket=bracket-l.count("}")

			if within==True:
				ref_lines.append(l)

			if bracket==0:
				if within==True:
					item=bib_item()
					item.decode(ref_lines)
					#for l in ref_lines:
					#	print(">",l)
					#item.dump()
					self.refs.append(item)
				within=False
		return True

	def new(self):
		item=bib_item()
		item.type="article"
		self.refs.append(item)
		return self.refs[-1]

	def dump(self):
		for r in self.refs:
			print(str(r))

	def save(self,file_name):
		lines=[]
		for r in self.refs:
			lines.append(str(r)+"\n")

		inp_save_lines_to_file(file_name,lines)

	def get_text(self,html=True):
		out=""
		for r in self.refs:
			if html==True:
				out=out+r.get_text()+"<br>"
			else:
				out=out+r.get_text()+"\n"

		return out

	def get_text_of_token(self,token,html=False):

		for r in self.refs:
			if r.token==token:
				if html==True:
					return r.get_text()+"<br>"
				else:
					return r.get_text()+"\n"

		return False

	def get_ref(self,token):
		for r in self.refs:
			if r.token==token:
				return r

		return False

