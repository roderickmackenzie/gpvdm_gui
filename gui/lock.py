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
from str2bool import str2bool
import time
from i18n import get_full_language
from inp import inp_replace_token_value

from lock_util import lock_load

from cal_path import get_exe_path
from threading import Thread

from cal_path import get_exe_command

if running_on_linux()==False:
	import winreg


#for tx_code
from ver import ver_core
from ver import ver_subver
from disk_speed import get_disk_speed
import platform
from i18n import get_full_language

from cal_path import get_tmp_path
from inp import inp

#firewall-cmd --permanent --add-port=8080/tcp
#firewall-cmd --reload

class lock():
	def __init__(self):
		self.registered=False

		self.uid=""
		self.renew_date=0
		self.register_date=0
		self.error=""
		self.disabled=False
		self.use_count=False
		self.open_gl_working=True
		self.reg_client_ver="ver"
		self.client_ver_from_lock=""
		self.status="no_key"
		self.use_count_check_web=5
		self.locked=[]
		self.not_locked=[]

		self.website="www.gpvdm.com"
		self.port="/api"

		self.data_path=os.path.join(get_user_settings_dir(),"settings.inp")

		if self.load()==True:
			if self.client_ver_from_lock!=self.reg_client_ver:
				self.get_license()

	def can_i_run_a_simulation(self):
		if self.disabled==True:
			return False
		else:
			return True
		return True

	def server_check_user(self):
		command=get_exe_command()+" --use"
		os.system(command)

	def report_bug(self,data):
		#Transmit debug info
		a=http_get()
		params = {'action':"crash_report",'ver_core': ver_core()+"."+ver_subver()+" "+self.reg_client_ver, 'uid': self.get_uid(),'data':data.replace("\n"," ")}
		tx_string="http://"+self.website+self.port+"/debug?"+urllib.parse.urlencode(params)
		lines=a.get(tx_string)

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
		l=inp()
		l.append("#email")
		l.append(email)
		l.append("#name")
		l.append(name)
		l.append("#company")
		l.append(company)
		l.append("#lang")
		l.append(get_full_language())
		l.append("#end")

		l.save_as(os.path.join(get_tmp_path(),"reg.txt"))

		command=get_exe_command()+" --register"
		os.system(command)
		#l.delete()

		l=inp()
		l.load(os.path.join(get_tmp_path(),"ret.txt"))
		lines=l.get_token("#ret")

		if lines==False:
			return False

		if lines=="no_internet":
			self.error="no_internet"
			return False

		if lines=="tooold":
			self.error="too_old"
			return False

		self.uid=lines

		return True

	def get_term(self):
		return (self.renew_date-self.register_date)/1000/60/60/24

	def html(self):
		text=""
		text=text+"UID:"+self.uid+"<br>"
		text=text+"count:"+str(self.use_count)+"<br>"
		return text

	def get_license(self,key="none",uid=None):
		if uid==None:
			uid=self.uid

		command=get_exe_command()+" --license"
		os.system(command)

		l=inp()
		l.load(os.path.join(get_tmp_path(),"ret.txt"))
		lines=l.get_token("#ret")

		if lines==False:
			return False

		if lines=="tooold":
			self.error="too_old"
			return False

		if lines=="error":
			self.error="uid_not_found"
			return False

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


	def is_function_locked(self,id):
		if id in self.locked:
			return True
		return False

	def is_function_not_locked(self,id):
		if id in self.not_locked:
			return True
		return False
		return True

	def load_new(self):
		if self.get_reg_key("new_install")=="true":
			print("fresh install.....")
			return False

		lines=[]

		lines=lock_load(self.data_path)
#		print(lines)

		self.reg_client_ver=self.get_reg_key("ver")
		if self.reg_client_ver==False:
			self.reg_client_ver="linux"

		if lines==False:
			return False

		ver=inp_search_token_value(lines, "#ver")
		if ver=="2.0":
			return False

		self.uid=inp_search_token_value(lines, "#uid")
		self.disabled=str2bool(inp_search_token_value(lines, "#disabled"))
		self.renew_date=int(inp_search_token_value(lines, "#renew_date"))
		self.register_date=int(inp_search_token_value(lines, "#register_date"))
		self.use_count=int(inp_search_token_value(lines, "#use_count"))
		self.locked=inp_search_token_value(lines, "#locked").split(";")
		self.not_locked=inp_search_token_value(lines, "#not_locked").split(";")

		self.client_ver_from_lock=inp_search_token_value(lines, "#client_ver")

		self.status=inp_search_token_value(lines, "#status")

		ver=float(inp_search_token_value(lines, "#ver"))
		
		if ver>1.0:
			self.registered=True
			return True

		return False
		return True

	def load(self):

		if self.load_new()==True:
			return

		value=self.get_reg_key("uid")
		if value!=False:
			self.uid=value
			#print("I found a uid in the registry.")
		return

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

	def is_registered(self):
		return self.registered
		return True

	def over_use_count_limit(self):
		return self.use_count>self.use_count_check_web+5
		return 0

	def is_expired(self):
		if self.status=="expired":
			return True
		return False

	def is_trial(self):
		if self.status=="no_key":
			return False

		if self.status=="full_version":
			return False

		if self.status=="cluster":
			if round((self.renew_date/1000-time.time())/24/60/60)<0:
				return True

			return False

		return True
		return False

	def validate_key(self,key):
		command=get_exe_command()+" --validate "+key
		os.system(command)

		l=inp()
		l.load(os.path.join(get_tmp_path(),"ret.txt"))
		lines=l.get_token("#ret")

		if lines==False:
			self.error="no_internet"
			return False

		if lines=="ok":
			self.load()
			return True
		elif lines=="tooold":
			self.error="too_old"
			return False

		self.error=lines
		return False

	

my_lock=lock()

def get_lock():
	global my_lock
	return my_lock

def get_email():
	return "roderick.mackenzie@nottingham.ac.uk"
