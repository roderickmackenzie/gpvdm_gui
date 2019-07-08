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

class watch_data():
	def __init__(self):
		self.file_name=""
		self.call_backs=[]
		self.time=0
	def __eq__(self,other):
		if self.file_name==other:
			return True
		return False

	def __str__(self):
		return self.file_name+" "+str(self.time)+" "+str(len(self.call_backs))

class file_watch():
	def __init__(self):
		self.files=[]
		self.disabled=True

	def reset(self):
		self.files=[]
		self.disabled=True
		self.timer=QTimer()		
		self.timer.timeout.connect(self.callback_check)
		self.timer.start(1000)

	
	def dump(self):
		for f in self.files:
			print(f)

	def callback_check(self):
		if self.disabled==True:
			return

		files=zip_lsdir(os.path.join(get_sim_path(),"sim.gpvdm"))
		if files==False:
			return

		for f in files:
			if f not in self.files:
				a=watch_data()
				a.file_name=f
				a.time=inp_getmtime(os.path.join(get_sim_path(),f))
				#print("add",f)
				self.files.append(a)
			else:
				i=self.files.index(f)
				file_time=inp_getmtime(os.path.join(get_sim_path(),f))
				if self.files[i].time!=file_time:
					#print("changed",self.files[i].file_name,datetime.fromtimestamp(self.files[i].time),datetime.fromtimestamp(file_time),len(self.files[i].call_backs))
					for c in self.files[i].call_backs:
						c()

					self.files[i].time=file_time
				
		#self.dump()

	def rebase(self):
		self.disabled=False
		self.callback_check()

	def add_call_back(self,file_name,function):
		if file_name in self.files:
			i=self.files.index(file_name)
			if function not in self.files[i].call_backs:
				self.files[i].call_backs.append(function)

watch=file_watch()

def get_watch():
	global watch
	return watch
