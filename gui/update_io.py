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
import random


class http_get_u(http_get):
	"""This is a """
	def __init__(self,address):
		http_get.__init__(self)
		self.address=address

		if am_i_rod()==False:
			self.web_site="http://www.gpvdm.com/api/updates/"
		else:
			self.web_site="http://127.0.0.1:8080/updates/"


	def go(self):

		file_name=os.path.join(self.web_site,self.address)+"?uid="+get_lock().get_uid()
		#print("asking for",file_name)

		self.data=self.get(file_name)

		return self.data



class update_cache(QObject):
	update_progress = pyqtSignal(int,float)

	def print_cache_status(self):
		print("files:"+str(len(self.file_list)))
		for f in self.file_list:
			print(f.get_status_line())

		print(self.to_download)
		print(self.on_disk)

	def callback_update_line(self,file_name,number):
		for i in range(0,len(self.file_list)):
			#print(self.file_list[i].file_name,file_name)
			#print(self.file_list[i].file_name,"-",file_name,file_name.count(self.file_list[i].file_name))
			if self.file_list[i].file_name==file_name:
				self.file_list[i].progress=number
				self.file_list[i].status="downloading"

	def __init__(self,sub_dir="materials"):
		QObject.__init__(self)
		self.sub_dir=sub_dir
		self.file_list=[]
		self.to_download=0
		self.to_install=0
		self.installed=0
		self.on_disk=0
		#self.web_cache_dir=get_web_cache_path()
		self.load_cache_status()
		self.first_contact=True
		self.state="downloading"

	def progress(self):
		total=len(self.file_list)
		if total==0:
			return 0.0
		if self.state=="downloading":
			return float(self.on_disk)/float(total)
		else:
			return float(self.installed)/float(total)

	def get_progress_text(self):
		if self.state=="downloading" and self.installed!=len(self.file_list):
			return str(self.on_disk)+"/"+str(len(self.file_list))+" extra materials downloaded"
		else:
			return str(self.installed)+"/"+str(len(self.file_list))+" extra materials installed"

	def write_cache_status(self):
		file_name=os.path.join(get_web_cache_path(),self.sub_dir,"info2.dat")
		if os.path.isdir(os.path.dirname(file_name))==False:
			os.makedirs(os.path.dirname(file_name))

		a = open(file_name, "w")
		for f in self.file_list:
			a.write(f.get_status_line()+"\n")
		a.close()



	def load_cache_status(self):
		self.file_list=[]

		file_path=os.path.join(get_web_cache_path(),self.sub_dir,"info2.dat")
		if os.path.isfile(file_path)==False:
			return False

		f = open(file_path)
		lines = f.readlines()
		f.close()

		self.file_list=[]
		
		for i in range(0, len(lines)):
			lines[i]=lines[i].rstrip()


		for l in lines:
			a=update_file_info()
			a.decode_from_disk(l)
			self.add_to_cache_from_disk(a)

	def add_to_cache_from_disk(self,f_in):
		if f_in.status=="on-disk" or f_in.status=="up-to-date":
			self.on_disk=self.on_disk+1

		if f_in.status=="downloading":
			f_in.status="update-avaliable"
			self.to_download=self.to_download+1

		if f_in.status=="up-to-date":
			self.installed=self.installed+1

		self.file_list.append(f_in)


	def add_to_cache_from_web(self,f_in):
		for i in range(0,len(self.file_list)):
			if f_in==self.file_list[i]:
				if os.path.isfile(os.path.join(get_web_cache_path(),self.sub_dir,f_in.file_name))==False:
					self.file_list[i].status="update-avaliable"
					self.file_list[i].md5_web=f_in.md5_web
					self.file_list[i].md5_disk="none"
					self.to_download=self.to_download+1
					return

				if self.file_list[i].md5_disk != f_in.md5_web:
					self.file_list[i].status="update-avaliable"
					self.file_list[i].md5_web=f_in.md5_web
					self.to_download=self.to_download+1
					return

				return

		f_in.status="update-avaliable"
		self.to_download=self.to_download+1
		self.file_list.append(f_in)


	def updates_get(self):

		data=http_get_u(self.sub_dir+"/info2.dat")
		ret=data.go()

		if ret==False:
			return False

		lines=ret.decode("utf-8").split("\n")
		lines.reverse()
		for l in lines:
			if len(l)>2:
				a=update_file_info()
				a.decode_from_web(l)
				#print(a)
				#a.cache_dir=sub_dir
				self.add_to_cache_from_web(a)

		self.write_cache_status()
		self.update_progress.emit(-1,self.progress())
		#self.print_cache_status()

	def updates_download(self):
		self.state="downloading"
		for i in range(0,len(self.file_list)):
			f=self.file_list[i]
			if f.status=="update-avaliable":
				self.callback_update_line(f.file_name,0)
				data=http_get_u(self.sub_dir+"/"+f.file_name)
				#data.got_data.connect(self.callback_got_data)
				ret=data.go()
				if ret!=False:
					#print(len(ret),f.size)
					cache_sub_dir=os.path.join(get_web_cache_path(),self.sub_dir)

					if os.path.isdir(cache_sub_dir)==False:
						os.makedirs(cache_sub_dir)
				
					file_han=open(os.path.join(cache_sub_dir,f.file_name), mode='wb')
					lines = file_han.write(ret)
					file_han.close()
					f.md5_disk=hashlib.md5(ret).hexdigest()[:5]

					self.callback_update_line(f.file_name,len(ret))

					f.status="on-disk"
					self.to_download=self.to_download-1
					self.on_disk=self.on_disk+1

					self.write_cache_status()
					self.update_progress.emit(i,self.progress())

				else:
					print("failed "+self.sub_dir+"/"+f.file_name)

	def emit_decompress(self,file_name,percent):
		#self.decompress.emit(file_name,percent)
		#print(file_name,percent)
		for f in self.file_list:
			if f.file_name==os.path.basename(file_name):
				f.progress=percent
				f.status="installing"

	def updates_install(self):
		self.state="installing"
		for i in range(0,len(self.file_list)):
			f=self.file_list[i]
			if f.status=="on-disk":
				out_sub_dir=f.file_name
				zip_file=os.path.join(get_web_cache_path(),self.sub_dir,f.file_name)
				install_path=os.path.join(os.path.dirname(get_materials_path()),f.target)
				#print(install_path,zip_file)
				if install_path!="":
					archive_extract(install_path, zip_file)
					#self.emit_decompress()
					self.update_progress.emit(i,1.0)
					f.status="up-to-date"
					self.installed=self.installed+1
					#addasdas

		self.write_cache_status()

	def updates_avaliable(self):
		for f in self.file_list:
			#print(f.status)
			if f.status=="update-avaliable" or f.status=="on-disk":
				return True
		#print("no")
		return False
