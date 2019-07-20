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


## @package inp
#  Used for writing and reading .inp files from .gpvdm archives
#

#import sys
import os
import shutil
from PyQt5.QtCore import QTimer

from util_zip import zip_lsdir
from cal_path import get_sim_path
from inp import inp_getmtime
from datetime import datetime
import re

class file_data():
	def __init__(self):
		self.file_name=""
		self.time=0

	def __eq__(self,other):
		if self.file_name==other:
			return True
		return False

	def __str__(self):
		return self.file_name+" "+str(self.time)

class hook_data():
	def __init__(self):
		self.file_name=""
		self.call_backs=[]

	def __eq__(self,other):
		if self.file_name==other:
			return True
		return False

	def __str__(self):
		return self.file_name+" "+str(len(self.call_backs))

class file_watch():
	def __init__(self):
		self.files=[]
		self.hooks=[]
		self.disabled=True

	def reset(self):
		#print("watches clear")
		self.files=[]
		self.hooks=[]
		self.disabled=True
		self.timer=QTimer()		
		self.timer.timeout.connect(self.check_dir)
		self.timer.start(250)

	
	def dump(self):
		for f in self.files:
			print(f)

		for f in self.hooks:
			print(f)

	def check_callbacks(self,changed_file):
		for h in self.hooks:
			#print(h.file_name,changed_file)
			if  bool(re.match(h.file_name,changed_file))==True:
				for c in h.call_backs:
					c()

	def check_dir(self):
		if self.disabled==True:
			return

		files=zip_lsdir(os.path.join(get_sim_path(),"sim.gpvdm"))
		if files==False:
			return

		for f in files:
			if f not in self.files:
				a=file_data()
				a.file_name=f
				a.time=inp_getmtime(os.path.join(get_sim_path(),f))
				#print("add",f)
				self.files.append(a)
			else:
				i=self.files.index(f)
				file_time=inp_getmtime(os.path.join(get_sim_path(),f))
				if self.files[i].time!=file_time:
					#print("changed",self.files[i].file_name,datetime.fromtimestamp(self.files[i].time),datetime.fromtimestamp(file_time))
					#self.dump()
					self.check_callbacks(self.files[i].file_name)

					self.files[i].time=file_time
				
		#self.dump()

	def rebase(self):
		self.disabled=False
		self.check_dir()

	def add_call_back(self,file_name,function):
		if file_name not in self.hooks:
			a=hook_data()
			a.file_name=file_name
			self.hooks.append(a)

			i=self.hooks.index(file_name)
			if function not in self.hooks[i].call_backs:
				self.hooks[i].call_backs.append(function)

watch=file_watch()

def get_watch():
	global watch
	return watch
