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


## @package update_io
#  Back end for getting updates
#

import sys
import os
from urllib.parse import urlparse
from cal_path import get_web_cache_path

from util_zip import archive_extract
from PyQt5.QtCore import pyqtSignal,QObject

import re
import urllib.request
from time import sleep
import hashlib

from ver import ver_core
from ver import ver_subver
from disk_speed import get_disk_speed
from display import is_open_gl_working
import platform
from i18n import get_full_language
from bugs import bugs_to_url
from inp_util import inp_get_all_tokens
from inp_util import inp_file_to_list

from cal_path import get_materials_path

from update_file_info import update_file_info
#import os
from ver import ver_core

from http_get import http_get
from threading import Thread
from code_ctrl import am_i_rod


class http_get_u(http_get):
	"""This is a """
	def __init__(self,address):
		http_get.__init__(self)
		self.address=address

		if am_i_rod()==False:
			self.web_site="http://www.gpvdm.com:8080/updates/"
		else:
			self.web_site="http://127.0.0.1:8080/updates/"


	def go(self):

		file_name=os.path.join(self.web_site,self.address)+"?uid="+get_lock().get_uid()
		#print("asking for",file_name)

		self.data=self.get(file_name)

		return self.data



class update_cache(QObject):
	#got_data = pyqtSignal()

	def print_cache_status(self):
		print("files:"+str(len(self.file_list)))
		for f in self.file_list:
			print(f.file_name,f.status,f.progress)
		print()



	def callback_got_data(self,file_name,number):
		for i in range(0,len(self.file_list)):
			#print(self.file_list[i].file_name,"-",file_name,file_name.count(self.file_list[i].file_name))
			if file_name.count(self.file_list[i].file_name)>0:
				self.file_list[i].progress=number
				self.file_list[i].status="downloading"

	def __init__(self):
		QObject.__init__(self)
		self.file_list=[]
		#self.web_cache_dir=get_web_cache_path()
		self.load_cache_status()
		self.first_contact=True

	def write_cache_status(self):
		a = open(os.path.join(get_web_cache_path(),"info.dat"), "w")
		for f in self.file_list:
			a.write(str(f)+"\n")
		a.write("#ver\n")
		a.write("1.0\n")
		a.write("#end\n")
		a.close()


	def load_cache_status(self):

		file_path=os.path.join(get_web_cache_path(),"info.dat")
		if os.path.isfile(file_path)==False:
			return False

		f = open(file_path)
		lines = f.readlines()
		f.close()

		self.file_list=[]
		
		for i in range(0, len(lines)):
			lines[i]=lines[i].rstrip()

		items=inp_file_to_list(lines)
		for i in items:
			#print(i)
			a=update_file_info()
			a.decode_list(i)
			self.file_list.append(a)


	def add_to_cache(self,f_in):
		for f in self.file_list:
			if f_in==f:
				if f_in.ver!=ver_core():
					f.status="gpvdm-too-old"
					f.ver=f_in.ver
					return
				if os.path.isfile(os.path.join(get_web_cache_path(),f_in.cache_dir,f_in.file_name))==False:
					f.status="update-avaliable"
					f.size=f_in.size
					return
				if f.md5 != f_in.md5:
					f.status="update-avaliable"
					f.size=f_in.size
					return
				
				return

		f_in.status="update-avaliable"
		self.file_list.append(f_in)


	def get_cache_dirs(self):
		self.web_dirs=[]
		data=http_get_u("info.dat")
		ret=data.go()
		print(">>read",ret)
		if ret==False:
			return False

		lines=ret.decode("utf-8").split("\n")

		self.web_dirs=inp_get_all_tokens(lines)
		#print("web dirs",self.web_dirs)
		for i in range(0,len(self.web_dirs)):
			if self.web_dirs[i].startswith("#")==True:
				self.web_dirs[i]=self.web_dirs[i][1:]
		#print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
		return True

	def updates_get(self):
		#print("updates_get:>>>><<")
		self.get_cache_dirs()
	
		for sub_dir in self.web_dirs:
			#print("here")
			data=http_get_u(sub_dir+"/info.dat")
			ret=data.go()
			if ret==False:
				return False

			lines=ret.decode("utf-8").split("\n")

			pos=0
			items=inp_file_to_list(lines)
			#print(items)
			for i in items:
				a=update_file_info()
				a.decode_list(i)
				a.cache_dir=sub_dir
				self.add_to_cache(a)

		self.write_cache_status()




	def updates_download(self):

		for f in self.file_list:
			if f.status=="update-avaliable" and f.ver==ver_core():
				data=http_get_u(f.cache_dir+"/"+f.file_name)
				data.got_data.connect(self.callback_got_data)
				ret=data.go()
				if ret!=False:
					#print(len(ret),f.size)
					cache_sub_dir=os.path.join(get_web_cache_path(),f.cache_dir)

					if os.path.isdir(cache_sub_dir)==False:
						os.makedirs(cache_sub_dir)
				
					file_han=open(os.path.join(cache_sub_dir,f.file_name), mode='wb')
					lines = file_han.write(ret)
					file_han.close()
					f.md5=hashlib.md5(ret).hexdigest()
					f.status="on-disk"

					self.write_cache_status()

	def emit_decompress(self,file_name,percent):
		#self.decompress.emit(file_name,percent)
		#print(file_name,percent)
		for f in self.file_list:
			if f.file_name==os.path.basename(file_name):
				f.progress=percent
				f.status="installing"

	def updates_install(self):

		for f in self.file_list:
			if f.status=="on-disk":
				out_sub_dir=f.file_name
				if out_sub_dir.endswith(".zip"):
					out_sub_dir=out_sub_dir[:-4]
				install_path=""
				if f.target=="materials":
					install_path=get_materials_path()

				#print(f.target,f.cache_dir)

				if install_path!="":
					archive_extract(os.path.join(install_path,out_sub_dir), os.path.join(get_web_cache_path(), f.cache_dir, f.file_name),call_back=self.emit_decompress)
					f.status="up-to-date"

		self.write_cache_status()

	def updates_avaliable(self):
		for f in self.file_list:
			#print(f.status)
			if f.status=="update-avaliable":
				return True
		#print("no")
		return False
