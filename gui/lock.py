# -*- coding: utf-8 -*-
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

## @package register
#  Registration window
#


import os

from icon_lib import icon_get

from inp import inp_load_file
import re

from error_dlg import error_dlg

from http_get import http_get
from ver import ver
import urllib.parse
from cal_path import get_user_settings_dir
from win_lin import running_on_linux
from inp import inp_save
from inp import inp_search_token_value
from os.path import expanduser
from util import str2bool
import time
from i18n import get_full_language
from inp import inp_replace_token_value

from lock_util import lock_load
from lock_util import lock_save
from lock_util import lock_update_token

from cal_path import get_exe_path
from code_ctrl import am_i_rod
from threading import Thread

if running_on_linux()==False:
	import winreg


#for tx_code
from ver import ver_core
from ver import ver_subver
from disk_speed import get_disk_speed
import platform
from i18n import get_full_language

#firewall-cmd --permanent --add-port=8080/tcp
#firewall-cmd --reload

class lock():
	def __init__(self,lock_on=False):
		self.lock_on=lock_on
		self.registered=False
		self.uid=""
		self.renew_date=0
		self.register_date=0
		self.lver="2.0"
		self.error=""
		self.disabled=False
		self.use_count=False
		self.ping_server=True
		self.open_gl_working=True
		self.reg_client_ver="ver"
		self.client_ver_from_lock=""
		self.status="trial"
		self.use_count_check_web=5
		if am_i_rod()==True:
			print("I'm running on Rods pc")
			self.website="127.0.0.1"
			self.port=":8080"
		else:
			self.website="www.gpvdm.com"
			self.port="/api"
		
		#self.website="www.gpvdm.com"


		if running_on_linux()==True:
			self.data_path=os.path.join(get_user_settings_dir(),"settings.inp")
			#self.li_file=os.path.join(get_user_settings_dir(),".gpvdm_li.inp")

		else:
			self.data_path=os.path.join(get_user_settings_dir(),"settings.inp")
			#self.li_file=os.path.join(get_user_settings_dir(),"gpvdm_li.inp")

		if self.lock_on==False:
			self.registered=True
			self.uid="LINUX_OPEN"

		if self.load()==True:
			if self.client_ver_from_lock!=self.reg_client_ver:
				self.get_license()
	
	def can_i_run_a_simulation(self):
		if self.disabled==True:
			return False
		else:
			return True

	def server_check_user(self):
		if self.use_count>self.use_count_check_web:
			self.get_license()

	def report_bug(self,data):
		#Transmit debug info
		a=http_get()
		params = {'action':"crash_report",'ver_core': ver_core()+"."+ver_subver()+" "+self.reg_client_ver, 'uid': self.get_uid(),'data':data.replace("\n"," ")}
		tx_string="http://"+self.website+self.port+"/debug?"+urllib.parse.urlencode(params)
		lines=a.get(tx_string)

	def debug_action_worker(self,data):
		a=http_get()
		params = {'action':"action",'uid': self.get_uid(),'data': data.replace("\n"," ")}
		tx_string="http://"+self.website+self.port+"/debug?"+urllib.parse.urlencode(params)
		lines=a.get(tx_string)

	def debug_action(self,data):
		p = Thread(target=self.debug_action_worker,args=(data,))
		p.daemon = True
		p.start()

	def debug(self):
		self.server_check_user()
		#Transmit debug info
		a=http_get()
		params = {'action':"new_sim",'ver_core': ver_core()+"."+ver_subver()+" "+self.reg_client_ver, 'uid': self.get_uid(),'os': platform.platform(), 'opengl': str(self.open_gl_working), 'lang': get_full_language(),'disk_speed': get_disk_speed()}
		tx_string="http://"+self.website+self.port+"/debug?"+urllib.parse.urlencode(params)
		lines=a.get(tx_string)


	def debug_tx_info(self):
		p = Thread(target=self.debug)
		p.daemon = True
		p.start()	



	def register(self,email="",name="",company=""):
		a=http_get()
		params = {'email': email, "ver": ver(), "name": name, "uid": self.uid, "lang": get_full_language() ,"lver":self.lver, "test":"true" , "win_id":self.get_win_id(),"company":company,"client_ver":self.reg_client_ver,"mac":self.get_mac()}

		lines=a.get("http://"+self.website+self.port+"/register?"+urllib.parse.urlencode(params))
		if lines==False:
			self.error="no_internet"
			return False

		lines=lines.decode("utf-8")

		if lines=="tooold":
			self.error="too_old"
			return False

		self.uid=lines

		return True

	def get_term(self):
		return (self.renew_date-self.register_date)/1000/60/60/24


	def html(self):
		text=""
		if self.lock_on==True:
			text=text+"UID:"+self.uid+"<br>"

		return text

	def get_license(self,key="none"):

		a=http_get()
		params = {"uid": self.uid, "key": key,"lver":self.lver, "win_id":self.get_win_id(),"win_id":self.get_mac()}
		lines=a.get("http://"+self.website+self.port+"/license?"+urllib.parse.urlencode(params))
	
		if lines==False:
			self.error="no_internet"
			return False

		lines=lines.decode("utf-8").split("\n")

		inp_replace_token_value(lines,"#client_ver",self.reg_client_ver)

		if lines[0]=="tooold":
			self.error="too_old"
			return False

		
		lock_save(self.data_path,lines)
		self.write_reg_key("new_install","false")

		self.load()

		self.registered=True
		return True

	def get_uid(self):
		return self.uid

	def get_next_gui_action(self):
		if self.over_use_count_limit()==True and self.disabled==False:
			return "no_internet"

		if self.is_registered()==False:
			return "register"


		return "ok"

	def load_new(self):

		if self.get_reg_key("new_install")=="true":
			print("fresh install.....")
			return False

		lines=[]
		lines=lock_load(self.data_path)
		#print(lines)

		self.reg_client_ver=self.get_gpvdm_ver_from_reg()

		if lines==False:
			return False

		ver=inp_search_token_value(lines, "#ver")
		if ver=="2.0":
			return False

		self.uid=inp_search_token_value(lines, "#uid")
		self.disabled=str2bool(inp_search_token_value(lines, "#disabled"))
		self.renew_date=int(inp_search_token_value(lines, "#renew_date"))
		self.register_date=int(inp_search_token_value(lines, "#register_date"))
		self.old_user=inp_search_token_value(lines, "#old_user")
		self.win_id=inp_search_token_value(lines, "#win_id")
		self.mac=inp_search_token_value(lines, "#mac")
		self.use_count=inp_search_token_value(lines, "#use_count")

		self.client_ver_from_lock=inp_search_token_value(lines, "#client_ver")


		val=inp_search_token_value(lines, "#ping_server")
		if val!=False:
			self.ping_server=str2bool(val)

		self.status=inp_search_token_value(lines, "#status")

		#print(lines,self.ping_server)

		#print(lines)

		if self.use_count!=False and self.ping_server==True:
			self.use_count=int(self.use_count)
			lock_update_token(self.data_path,"#use_count",str(self.use_count+1))
		else:
			self.use_count=0
		#print(lines)

		ver=float(inp_search_token_value(lines, "#ver"))
		
		if ver>1.0:
			self.registered=True
			return True

		return False

	def load(self):

		if self.load_new()==True:
			if self.get_reg_key("uid")==False:
				self.write_reg_key("uid",self.uid)
			return

		#check if old file exists
		if running_on_linux()==True:
			path=os.path.join(expanduser("~"),"settings.inp")
		else:
			path=os.path.join(get_exe_path(),"uid.inp")

		#test for old users
		if os.path.isfile(path)==True:
			try:
				lines=[]
				lines=lock_load(path)
				self.uid=inp_search_token_value(lines, "#uid")
				#print("old uid found",self.uid)
				return
			except:
				pass


		value=self.get_reg_key("uid")
		if value!=False:
			self.uid=value
			#print("I found a uid in the registry.")

	def get_reg_key(self,token):
		if running_on_linux()==False:
			try:
				registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\gpvdm", 0, winreg.KEY_READ)
				value, regtype = winreg.QueryValueEx(registry_key, token)
				winreg.CloseKey(registry_key)
				return value
			except WindowsError:
				pass

		return False

	def get_gpvdm_ver_from_reg(self):
		if running_on_linux()==False:
			try:
				registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\gpvdm", 0, winreg.KEY_READ)
				value, regtype = winreg.QueryValueEx(registry_key, "ver")
				winreg.CloseKey(registry_key)
				return str(value)
			except WindowsError:
				print("data search")
				pass

		return "linux_ver"

	def get_win_id(self):
		if running_on_linux()==False:
			try:
				registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Cryptography", 0, winreg.KEY_READ |winreg.KEY_WOW64_64KEY)
				value, regtype = winreg.QueryValueEx(registry_key, "MachineGuid")
				winreg.CloseKey(registry_key)
				return str(value)
			except WindowsError:
				print("data search")
				pass
		else:
			return "undefined"

	def get_mac(self):
		if running_on_linux()==True:
			import fcntl
			import socket
			import struct

			ifname=os.listdir('/sys/class/net/')[0]
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
			return ':'.join('%02x' % b for b in info[18:24])
		else:
			return "undefined"

	def write_reg_key(self,token,value):
		if running_on_linux()==False:
			try:
				key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\gpvdm", sam=winreg.KEY_SET_VALUE | winreg.KEY_WRITE)
			except:
				key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\gpvdm")
			try:
				winreg.SetValueEx(key, token, 0, winreg.REG_SZ, value)
			finally:
				key.Close()

	def is_registered(self):
		return self.registered

	def over_use_count_limit(self):
		return self.use_count>self.use_count_check_web+5

	#is the GUI disabled
	def is_disabled(self):
		#print("disabled",self.disabled)
		#return True
		if self.disabled==True:
			return True

		if self.over_use_count_limit()==True:
			return True

		if self.renew_date==-1:
			return False



		self.disable_now()
		return True

	def disable_now(self):
		lock_update_token(self.data_path,"#disabled","true")
		self.disabled=True

	def enable_now(self):
		lock_update_token(self.data_path,"#disabled","false")
		self.disabled=False

	def is_trial(self):
		if self.status=="full_version":
			return False

		return True

	def validate_key(self,key):
		a=http_get()

		params = {"key": key, "uid": self.uid,"lver":self.lver, "win_id":self.get_win_id(), "mac":self.get_mac()}

		data=a.get("http://"+self.website+self.port+"/activate?"+urllib.parse.urlencode(params))
		if data==False:
			self.error="no_internet"
			return False

		data=data.decode("utf-8") 
		
		if data=="ok":
			self.get_license()
			return True
		elif data=="tooold":
			self.error="too_old"
			return False

		self.error=data
		return False


my_lock=lock(lock_on=True)

def get_lock():
	global my_lock
	return my_lock
