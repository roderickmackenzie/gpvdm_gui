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
#import signal
from util_zip import replace_file_in_zip_archive
#import subprocess
from tempfile import mkstemp

#import logging
#import zipfile
from win_lin import running_on_linux
from util_zip import zip_remove_file
from util_zip import write_lines_to_archive
from util_zip import read_lines_from_archive
from util_zip import archive_isfile
from util_zip import zip_lsdir

from cal_path import get_sim_path
from str2bool import str2bool

import hashlib
from util_zip import archive_get_file_time

enable_encrypt=False
try:
	enable_encrypt=True
	from Crypto.Cipher import AES
except:
	pass

class inp():

	def __init__(self,file_path=None):
		self.lines=[]
		self.pos=0
		if file_path!=None:
			self.set_file_name(file_path)

	def __str__(self):
		if self.lines==False:
			return ""
		ret=""
		for i in range(0, len(self.lines)):
			ret=ret+self.lines[i]+"\n"

		return ret

	def lsdir(self):
		return zip_lsdir(self.zip_file_path)

	def set_file_name(self,file_path,archive="sim.gpvdm",mode="l"):
		if file_path==None:
			return False

		file_name=default_to_sim_path(file_path)

		if file_name.endswith(".gpvdm"):		#we are opperating on just the archive
			self.zip_file_path=file_name
			self.file_name=None
			return

		if os.path.dirname(file_path).endswith(".gpvdm"):		#/handles a/b/sim.gpvdm/jv.inp
			self.zip_file_path=os.path.dirname(file_path)
		else:
			self.zip_file_path=search_zip_file(file_name,archive)

		self.file_name=os.path.basename(file_name)

	def load(self,file_path,archive="sim.gpvdm",mode="l"):
		self.set_file_name(file_path,archive=archive,mode=mode)

		if self.file_name!=None:
			self.lines=read_lines_from_archive(self.zip_file_path,self.file_name,mode=mode)

		if self.lines==False:
			return False

		return self

	def isfile(self,file_path,archive="sim.gpvdm"):
		file_name=default_to_sim_path(file_path)
		
		self.zip_file_name=search_zip_file(file_name,archive)

		return archive_isfile(self.zip_file_name,os.path.basename(file_name))

	def to_sections(self,start="#layers"):
		self.pos=0
		seg_len=0
		tokens={}
		seg_number=-1
		while(1):
			token,val=self.get_next_token_and_val()

			if token==False:
				break

			if token=="#ver" or token=="#end":
				break

			if token.startswith(start)==True:
				seg_number=seg_number+1
				if seg_number==1:
					break

			if seg_number==0:		#We are on the first segment
				token=token.rstrip('1234567890').lstrip("#")
				if token[-1]=="_":
					token=token[:-1]
				tokens.update([ (token, 0) ])

				seg_len=seg_len+1

		section_object = type("section_object",(), tokens)

		self.sections=[]
		self.pos=0
		seg_pos=0
		sec=section_object()
		found_start=False
		while(1):
			token,val=self.get_next_token_and_val()
			#print(token)
			if token=="#end" or token==False:
				break

			if token.startswith(start)==True:
				found_start=True

			if found_start==True:
				token=token.rstrip('1234567890').lstrip("#")
				if token[-1]=="_":
					token=token[:-1]

				setattr(sec, token, val)
				seg_pos=seg_pos+1
				if seg_pos==seg_len:
					seg_pos=0
					self.sections.append(sec)
					sec=section_object()


	def delta_tokens(self,cmp_file):
		missing_in_cmp=[]
		for self_line in self.lines:
			if self_line.startswith("#"):
				for cmp_line in cmp_file.lines:
					found=False
					if self_line==cmp_line:
						found=True
						break
				if found==False:
					missing_in_cmp.append(self_line)

		return missing_in_cmp

	def import_tokens(self,in_file):
		for self_line in self.lines:
			if self_line.startswith("#") and self_line!="#ver" and self_line!="#end":
				in_data=in_file.get_token(self_line)
				if in_data!=False:
					self.replace(self_line,in_data)

	def get_token(self,token):
		if self.lines==False:
			return False

		"""Get the value of a token from a list"""
		for i in range(0, len(self.lines)):
			if self.lines[i]==token:
				return self.lines[i+1]

		return False

	def reset(self):
		self.pos=0

	def get_file_name(self):
		return os.path.join(self.zip_file_path,self.file_name)
	
	def get_tokens(self):
		ret=[]
		for l in self.lines:
			if l.startswith("#"):
				ret.append(l)
		return ret

	def replace_token_name(self,old_token,new_token):
		if type(self.lines)!=list:
			return False

		for i in range(0, len(self.lines)):
			if self.lines[i].startswith(old_token)==True:
				delta=self.lines[i][len(old_token):]
				try:
					int(delta)
				except:
					delta=""

				self.lines[i]=new_token+delta
				#return


	#update a token value
	def set_token(self,token,value):
		return self.replace(token,value)

	def replace(self,token,replace):
		if type(replace)==bool:
			replace=str(replace)

		if type(self.lines)!=list:
			return False

		replaced=False
		if type(replace)==str:
			for i in range(0, len(self.lines)):
				if self.lines[i]==token:
					#print(self.lines[i],token,replace)
					if i+1<len(self.lines):
						self.lines[i+1]=replace
						replaced=True
						break

		if type(replace)==list:
			ret=[]
			i=0
			while(i<len(self.lines)):
				ret.append(self.lines[i])
				if self.lines[i]==token:
					for r in replace:
						ret.append(r)
					for ii in range(i+1,len(self.lines)):
						if self.lines[ii].startswith("#")==True:
							i=ii-1
							break
				i=i+1

			self.lines=ret

		return replaced

	def next_sequential_file(self,prefix):
		files=zip_lsdir(self.zip_file_path)
		for i in range(0,100):
			new_name=prefix+str(i)+".inp"
			if new_name not in files:
				return new_name

		return False

	def save(self,mode="l",dest="archive"):
		"""Write save lines to a file"""
		ret= write_lines_to_archive(self.zip_file_path,self.file_name,self.lines,mode=mode,dest=dest)
		return ret

	def append(self,data):
		self.lines.append(data)

	def save_as(self,file_path,archive="sim.gpvdm",mode="l",dest="archive"):

		full_path=default_to_sim_path(file_path)
		self.zip_file_path=os.path.join(os.path.dirname(full_path),archive)
		self.file_name=os.path.basename(full_path)

		return self.save()

	def delete(self):
		zip_remove_file(self.zip_file_path,self.file_name)

	def get_next_token_and_val(self):
		ret=[]
		if self.pos>=len(self.lines):
			return False,False
		ret.append(self.lines[self.pos])
		self.pos=self.pos+1

		if self.pos>=len(self.lines):
			return False,False
		ret.append(self.lines[self.pos])
		self.pos=self.pos+1

		return ret[0],ret[1]

	def get_next_val(self):
		self.pos=self.pos+1
		val=self.lines[self.pos]
		self.pos=self.pos+1
		return val

	def get_array(self, token):
		"""Get an array of data assosiated with a token"""
		ret=[]
		for i in range(0, len(self.lines)):
			if self.lines[i]==token:
				pos=i+1
				for ii in range(pos,len(self.lines)):
					if len(self.lines[ii])>0:
						if self.lines[ii][0]=="#":
							return ret
					
					ret.append(self.lines[ii])
				return ret
		return False

	def is_token(self,token):
		"""Is the token in a file"""
		for i in range(0, len(self.lines)):
			if lines[i]==token:
				return True

		return False

	def time(self):
		full_file_name=default_to_sim_path(self.file_name)

		if os.path.isfile(full_file_name):
			return os.path.getmtime(full_file_name)

		if os.path.isfile(self.zip_file_path):
			return archive_get_file_time(self.zip_file_path,os.path.basename(self.file_name))

		return -1

	def get_next_token_array(self):
		"""Get the next token as an array"""
		values=[]
		if self.pos>=len(self.lines):
			return False,False

		token=self.lines[self.pos]
		self.pos=self.pos+1

		for i in range(self.pos,len(self.lines)):
			self.pos=i
			if len(self.lines[i])>0:
				if self.lines[i][0]=="#":
					break

			values.append(self.lines[i])		

		return token,values

	def delete_token(self,token,times=-1):
		ret=[]
		copy=True
		c=0
		for l in self.lines:
			if l.startswith("#"):
				copy=True

			if l.startswith("#"):
				if l==token:
					if c<times or c==-1:
						copy=False
						c=c+1

			if copy==True:
				ret.append(l)

		self.lines=ret

callbacks=[]
class callback_data():
	def __init__(self):
		self.file_name=""
		self.call_back=""
		self.id=""
		self.call_back_fn=None

	def __eq__(self,other):
		if self.file_name==other.file_name and self.id==other.id:
			return True
		return False


def inp_callbacks_clear():
	global callbacks
	callbacks=[]

def inp_callback_add_write_hook(file_name,call_back_fn,id):
	global callbacks
	a=callback_data()
	a.file_name=file_name
	a.call_back=call_back_fn
	a.id=id
	#print("add hook",a.file_name)
	#for i in range(0,len(callbacks)):
	#	print(callbacks[i].file_name,callbacks[i].call_back_fn)
	for i in range(0,len(callbacks)):
		c=callbacks[i]
		if c==a:
			if c.call_back_fn!=call_back_fn:
				callbacks[i].call_back_fn=call_back_fn
				inp_dump_hooks()
				return

	callbacks.append(a)
	inp_dump_hooks()

def inp_callback_check_hook(file_name,id):
	print("inp_callback_check_hook",id)
	global callbacks
	inp_dump_hooks()
	for c in callbacks:
		#print("check>>",c.file_name,file_name)
		if c.file_name==file_name and c.id!=id:
			#print("call")
			inp_dump_hooks()
			c.call_back()

def inp_dump_hooks():
	print("inp_dump_hooks")
	global callbacks
	for c in callbacks:
		print("inp_dump_hooks>>",c.file_name,c.id)

def inp_issequential_file(file_name,root):
	if file_name.startswith(root) and file_name.endswith(".inp"):
		number=file_name[len(root):-4]
		if number.isdigit()==True:
			return True
	return False

def inp_find_active_file(file_path):
	"""if you are looking for /path/to/file/cluster0.inp it will expect /path/to/file/cluster"""
	path=os.path.dirname(file_path)
	root=os.path.basename(file_path)
	files=zip_lsdir(os.path.join(path,"sim.gpvdm"))
	for f in files:
		if inp_issequential_file(f,root)==True:
			ret=str2bool(inp_get_token_value(os.path.join(path,f), "#tab_enabled"))
			if ret==True:
				return f
	return False


## List the content of an archive and directory in one list
#  @param file_name /path/to/gpvdm.sim
def inp_lsdir(file_name):
	full_path=default_to_sim_path(file_name)
	return zip_lsdir(full_path)

def inp_ls_seq_files(path,root):
	ret=[]
	files=inp_lsdir(path)

	for f in files:
		if inp_issequential_file(f,root)==True:
			ret.append(f)

	return ret

def inp_dir_listing(file_name):
	full_path=default_to_sim_path(file_name)
	files=zip_lsdir(full_path)
	for f in files:
		print(f)

def inp_remove_file(file_name,archive="sim.gpvdm"):
	"""Remove a file from an archive"""
	full_name=default_to_sim_path(file_name)

	archive_path=os.path.join(os.path.dirname(full_name),archive)
	zip_remove_file(archive_path,os.path.basename(full_name))

def inp_read_next_item(lines,pos):
	"""Read the next item form an inp file"""
	token=lines[pos]
	pos=pos+1
	value=lines[pos]
	pos=pos+1
	return token,value,pos


def inp_replace_token_value(lines,token,replace):
	"""replace the value of a token in a list"""
	if type(lines)!=list:
		return False

	replaced=False
	for i in range(0, len(lines)):
		if lines[i]==token:
			if i+1<len(lines):
				lines[i+1]=replace
				replaced=True
				break

	return replaced

def inp_replace_token_array(lines,token,replace):
	"""replace the value of a token array in a list"""
	new_list=[]
	pos=0
	for i in range(0, len(lines)):
		new_list.append(lines[i])
		if lines[i]==token:
			pos=i+1
			new_list.extend(replace)
			break

	new_pos=0
	for i in range(pos, len(lines)):
		if len(lines[i])>0:
			if lines[i][0]=="#":
				new_pos=i
				break

	for i in range(new_pos, len(lines)):
		new_list.append(lines[i])
	
	return new_list


def inp_add_token(lines,token,value):
	a=[]
	a.append(token)
	a.append(value)
	ret=a + lines
	return ret



def inp_update_token_array(file_path, token, replace):
	lines=[]
	base_name=os.path.basename(file_path)
	path=os.path.dirname(file_path)

	zip_file_name=os.path.join(path,"sim.gpvdm")

	lines=read_lines_from_archive(zip_file_name,os.path.basename(file_path))

	lines=inp_replace_token_array(lines,token,replace)

	write_lines_to_archive(zip_file_name,base_name,lines)

def inp_delete_token(file_path, token, archive="sim.gpvdm",id=""):
	lines=[]
	lines_out=[]

	lines=inp_load_file(file_path,archive=archive)
	if lines==False:
		return False

	count=2
	for l in lines:
		if l==token:
			count=0

		if count>1:
			lines_out.append(l)

		count=count+1
		
	inp_save(file_path,lines_out,archive=archive,id=id)

	return True

def inp_insert_token(file_path, token_to_insert_after, token, value, archive="sim.gpvdm",id=""):
	lines=[]
	lines_out=[]

	lines=inp_load_file(file_path,archive=archive)
	if lines==False:
		return False
	if token_to_insert_after==False:
		new_lines=[]
		new_lines.append(token)
		new_lines.append(value)
		new_lines.extend(lines)
		lines_out=new_lines
		#print(lines_out)
	else:
		count=3
		for l in lines:

			lines_out.append(l)

			if l==token_to_insert_after:
				count=0

			if count==1:
				lines_out.append(token)
				lines_out.append(value)

			count=count+1
	
	#print(lines_out)	
	inp_save(file_path,lines_out,archive=archive,id=id)

	return True

def inp_insert_duplicate(dest_file_path, dest_token, src_file_path, src_token, archive="sim.gpvdm",id=""):
	lines=[]
	lines_dest=[]

	lines_src=inp_load_file(src_file_path,archive=archive)
	if lines_src==False:
		return False

	lines_dest=inp_load_file(dest_file_path,archive=archive)
	if lines_dest==False:
		return False

	val=inp_get_token_value_from_list(lines_src, src_token)
	if val==None or val==False:
		return False
	
	ret=inp_replace_token_value(lines_dest,dest_token,val)
	if ret==False or val==False:
		return False

	#print(lines_dest)	
	inp_save(dest_file_path,lines_dest,archive=archive,id=id)

	return True

def inp_update_token_value(file_path, token, replace,archive="sim.gpvdm",id=""):
	lines=[]

	if token=="#Ty0":
		inp_update_token_value("thermal.inp", "#Ty1", replace,archive)

		inp_update_token_value("thermal.inp", "#Tx0", replace,archive)
		inp_update_token_value("thermal.inp", "#Tx1", replace,archive)

		inp_update_token_value("thermal.inp", "#Tz0", replace,archive)
		inp_update_token_value("thermal.inp", "#Tz1", replace,archive)

		files=inp_lsdir(os.path.join(os.path.dirname(file_path),"sim.gpvdm"))
		for i in range(0,len(files)):
			if files[i].startswith("dos") and files[i].endswith(".inp"):

				inp_update_token_value(files[i], "#Tstart", replace,archive)
				try:
					upper_temp=str(float(replace)+5)
				except:
					upper_temp="300.0"
				inp_update_token_value(files[i], "#Tstop", upper_temp,archive)

	lines=inp_load_file(file_path,archive=archive)
	if lines==False:
		return False

	ret=inp_replace_token_value(lines,token,replace)
	if ret==False:
		return False


	inp_save(file_path,lines,archive=archive,id=id)

	return True

def inp_copy_file(dest,src):
	lines=[]
	lines=inp_load_file(src)
	if lines!=False:
		inp_save(dest,lines)
		return True
	else:
		return False

def default_to_sim_path(file_path):
	"""For file names with no path assume it is in the simulation directory"""
	head,tail=os.path.split(file_path)
	if head=="":
		return os.path.join(get_sim_path(),file_path)
	else:
		return file_path

def search_zip_file(file_name,archive):
	#Assume sim.gpvdm is in /a/b/c/ where mat.inp is in /a/b/c/mat.inp 
	zip_file_path=os.path.join(os.path.dirname(file_name),archive)
	if os.path.isfile(file_name)==True:
		#we found the file there so we do not care about the arhive 
		return zip_file_path

	#now try back one level
	#Using path /a/b/c/mat.inp look in /a/b/sim.gpvdm for the sim file
	if os.path.isfile(zip_file_path)==False:
		zip_file_path=os.path.join(os.path.dirname(os.path.dirname(file_name)),archive)

	return zip_file_path

def inp_load_file(file_path,archive="sim.gpvdm",mode="l"):
	"""load file"""
	if file_path==None:
		return False

	file_name=default_to_sim_path(file_path)
	#print(">",file_name)
	zip_file_path=search_zip_file(file_name,archive)#os.path.join(os.path.dirname(file_name),archive)
	#print(">>",zip_file_path)
	file_name=os.path.basename(file_name)
	ret=read_lines_from_archive(zip_file_path,file_name,mode=mode)
	return ret

def inp_save(file_path,lines,archive="sim.gpvdm",id=""):
	"""Write save lines to a file"""

	full_path=default_to_sim_path(file_path)
	archive_path=os.path.join(os.path.dirname(full_path),archive)
	file_name=os.path.basename(full_path)
	#print("archive",archive_path)
	#print("file",file_name)
	#print(lines)


	ret= write_lines_to_archive(archive_path,file_name,lines)

	if id!="":
		inp_callback_check_hook(file_path,id)

	return ret

def inp_save_lines_to_file(file_path,lines):
	"""This will save lines to a text file"""
	file_name=default_to_sim_path(file_path)
	dump='\n'.join(lines)

	dump=dump.rstrip("\n")
	dump=dump.encode('utf-8')
	try:
		f=open(file_name, mode='wb')
	except:
		return False
	written = f.write(dump)
	f.close()

	return True

def inp_new_file():
	"""Make a new input file"""
	ret=[]
	ret.append("#ver")
	ret.append("1.0")
	ret.append("#end")
	return ret



def inp_search_token_array(lines, token):
	"""Get an array of data assosiated with a token"""
	ret=[]
	for i in range(0, len(lines)):
		if lines[i]==token:
			pos=i+1
			for ii in range(pos,len(lines)):
				if len(lines[ii])>0:
					if lines[ii][0]=="#":
						return ret
				
				ret.append(lines[ii])
			return ret
	return False

def inp_get_token_array(file_path, token):
	"""Get an array of data assosiated with a token"""
	lines=[]
	ret=[]
	lines=inp_load_file(file_path)

	ret=inp_search_token_array(lines, token)

	return ret

def inp_get_token_value_from_list(lines, token):
	"""Get the value of a token from a list - don't use this one any more"""
	for i in range(0, len(lines)):
		if lines[i]==token:
			return lines[i+1]
	return None

def inp_search_token_value(lines, token):
	"""Get the value of a token from a list"""
	for i in range(0, len(lines)):
		if lines[i]==token:
			return lines[i+1]

	return False

def inp_get_token_value(file_path, token,archive="sim.gpvdm",search_active_file=False):
	"""Get the value of a token from a file"""

	if search_active_file==True:
		file_path=inp_find_active_file(file_path)

	lines=[]
	lines=inp_load_file(file_path,archive=archive)
	if lines==False:
		return None

	ret=inp_search_token_value(lines, token)
	if ret!=False:
		return ret

	return None

def inp_sum_items(lines,token):
	my_sum=0.0
	for i in range(0, len(lines)):
		if lines[i].startswith(token)==True:
			my_sum=my_sum+float(lines[i+1])

	return my_sum


def inp_get_file_ver(archive,file_name):
	lines=[]
	lines=read_lines_from_archive(archive,file_name)

	if lines!=False:
		ver=inp_search_token_value(lines, "#ver")
	else:
		return ""

	return ver

def inp_get_next_token_array(lines,start):
	"""Get the next token"""
	ret=[]
	if start>=len(lines):
		return None,start

	for i in range(start,len(lines)):
		if i!=start:
			if len(lines[i])>0:
				if lines[i][0]=="#":
					break

		ret.append(lines[i])
			

	return ret,i
