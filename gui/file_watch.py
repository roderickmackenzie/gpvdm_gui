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

import zipfile
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
		self.running=False
		self.last_run=-1

	def reset(self):
		#print("watches clear")
		self.files=[]
		self.hooks=[]
		self.disabled=True
		self.timer=QTimer()		
		self.timer.timeout.connect(self.check_dir)
		self.timer.start(300)

	
	def dump(self):
		for f in self.files:
			print(f)

		for f in self.hooks:
			print(f)

	def check_callbacks(self,changed_file):
		#print("Start hook search due to",changed_file)
		for i in range(0,len(self.hooks)):
			h=self.hooks[i]
			#print(">>>",i,h.file_name)
			try:
				if  bool(re.match(h.file_name,changed_file))==True:
					#print("aaaaaa",h.file_name)

					for c in h.call_backs:
						c()
						print("a")
					#print("bbbbb")
			except:
				pass
		#print("End hook search")

	def check_zip_file(self,f):
		zip_file=os.path.join(get_sim_path(),f)
		if os.path.isfile(zip_file)==True:
			zf = zipfile.ZipFile(zip_file, 'r')
			my_list=zf.namelist()
			zf.close()
			#print("open")
			self.check_files(my_list,open_zip_files=False)

	def check_files(self,in_files,open_zip_files=True):
		if self.disabled==True:
			return

		#if open_zip_files==False:
		#	print("here",in_files)

		for f in in_files:
			if f not in self.files:
				a=file_data()
				a.file_name=f
				a.time=inp_getmtime(os.path.join(get_sim_path(),f))
				self.files.append(a)

				if f=="sim.gpvdm" and open_zip_files==True:
					self.check_zip_file(f)
			else:
				i=self.files.index(f)
				file_time=inp_getmtime(os.path.join(get_sim_path(),f))
				#if open_zip_files==False:
				#	print("here",f,self.files[i].time,file_time)
				if self.files[i].time!=file_time:
					#print("changed",f)	#print("changed",self.files[i].file_name,datetime.fromtimestamp(self.files[i].time),datetime.fromtimestamp(file_time))
					#self.dump()
					self.check_callbacks(self.files[i].file_name)

					self.files[i].time=file_time

					if f=="sim.gpvdm" and open_zip_files==True:
						self.check_zip_file(f)
							

		#self.dump()


	def check_dir(self):
		if self.running==False:
			self.running=True
			if os.path.isdir(get_sim_path())==True:
				my_list=os.listdir(get_sim_path())
				self.check_files(my_list)

		self.running=False

	def rebase(self):
		#print("rebase>>")
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
