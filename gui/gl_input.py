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

## @package gl_input
#  The mouse and keyboard input to the OpenGL display.
#

import sys
open_gl_ok=False

import sys
from math import fabs

try:
	from OpenGL.GL import *
	from OpenGL.GLU import *
	from PyQt5 import QtOpenGL
	from PyQt5.QtOpenGL import QGLWidget
	from gl_color import set_color
	from gl_lib import val_to_rgb
	from gl_color import set_false_color
	from gl_color import color
	from gl_color import search_color
	from gl_scale import project_m2screen_x
	from gl_scale import project_m2screen_y
	from gl_scale import project_m2screen_z

except:
	pass

from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import time


#mesh
from mesh import mesh_get_xlen
from mesh import mesh_get_zlen
from epitaxy import get_epi

class mouse_event():
	def __init__(self):
		self.time=0
		self.x=0
		self.y=0

	def delta_time(self):
		return time.time()-self.time

class gl_input():

	def keyPressEvent(self, event):
		if type(event) == QtGui.QKeyEvent:
			if event.text()=="f":
				self.showFullScreen()
			if event.text()=="r":
				if self.timer==None:
					self.start_rotate()
				else:
					self.timer.stop()
					self.timer=None
			if event.text()=="z":
				if self.timer==None:
					self.start_rotate()
					if self.view.zoom>-40:
						self.view.zoom =-400
					self.timer=QTimer()
					self.timer.timeout.connect(self.fzoom_timer)
					self.timer.start(50)
				else:
					self.timer.stop()
					self.timer=None


	def event_to_3d_obj(self,event):
		x = event.x()
		y = self.height()-event.y()
		set_false_color(True)

		self.enable_render_text=False
		self.render()
		self.enable_render_text=True

		data=glReadPixelsub(x, y, 1, 1, GL_RGBA,GL_FLOAT)

		#self.swapBuffers()
		c=color(int(255*data[0][0][0]),int(255*data[0][0][1]),int(255*data[0][0][2]))
		obj=search_color(c)

		set_false_color(False)
		return obj

	def mouseDoubleClickEvent(self,event):
		#thumb_nail_gen()
		self.obj=self.event_to_3d_obj(event)

		if self.obj.startswith("layer")==True:
			self.selected_layer=self.obj
			self.do_draw()

	def mouseMoveEvent(self,event):
		if 	self.timer!=None:
			self.timer.stop()
			self.timer=None

		if self.lastPos==None:
			self.lastPos=event.pos()
		dx = event.x() - self.lastPos.x();
		dy = event.y() - self.lastPos.y();
		sel=self.gl_objects_is_selected()
		if sel==False:
			if event.buttons()==Qt.LeftButton:
				
				self.view.xRot =self.view.xRot - 1 * dy
				self.view.yRot =self.view.yRot - 1 * dx

			if event.buttons()==Qt.RightButton:
				self.view.x_pos =self.view.x_pos + 0.1 * dx
				self.view.y_pos =self.view.y_pos - 0.1 * dy
		else:
			#print(sel.moveable)
			if sel.moveable==True:
				self.gl_objects_move(sel,dx*0.05,-dy*0.05)
			#print(dx,dy)
		
		self.lastPos=event.pos()
		self.setFocusPolicy(Qt.StrongFocus)
		self.setFocus()
		self.update()
		#self.view_dump()

	def mousePressEvent(self,event):
		self.lastPos=None
		self.mouse_click_event=mouse_event()
		self.mouse_click_event.time=time.time()
		self.mouse_click_event.x=event.x()
		self.mouse_click_event.y=event.y()
		
		if event.buttons()==Qt.LeftButton:
			self.obj=self.event_to_3d_obj(event)

			if self.obj.startswith("layer")==True:
				self.selected_layer=self.obj
				#self.enable_render_text=False
				self.update()
				#self.enable_render_text=True
		return

		if event.buttons()==Qt.LeftButton:
			#thumb_nail_gen()
			#self.mouse_click_time=time.time()
			x = event.x()
			y = self.height()-event.y()
			set_false_color(True)
			self.enable_render_text=False
			self.render()
			self.enable_render_text=True
			data=glReadPixelsub(x, y, 1, 1, GL_RGBA,GL_FLOAT)
			set_false_color(False)

			c=color(int(255*data[0][0][0]),int(255*data[0][0][1]),int(255*data[0][0][2]))

			self.obj=search_color(c)
			if self.obj=="none":
				return

			self.gl_objects_select(self.obj)
			self.update()

			print("you have clicked on=",self.obj)



	def mouseReleaseEvent(self,event):
		delta=time.time() - self.mouse_click_event.time

		self.obj=self.event_to_3d_obj(event)

		print(self.mouse_click_event.y,self.mouse_click_event.delta_time())
		if event.button()==Qt.RightButton:
			
			if (delta)<0.5:
				if self.obj!="none":
					if self.obj.startswith("layer")==True:
						self.selected_layer=self.obj
						self.update()
						self.menu_layer(event)

						return
					if self.obj.startswith("mesh")==True:
						self.mesh_menu(event)
				else:
					self.menu(event)
		obj=self.gl_object_deselect()
		if obj!=False:
			if obj.id=="ray_src":
				x=scale_screen_x2m(obj.x)
				y=scale_screen_y2m(obj.y)-epitaxy_get_device_start()
				z=project_m2screen_z(obj.z)
				inp_update_token_value("ray.inp","#ray_xsrc",str(x))
				inp_update_token_value("ray.inp","#ray_ysrc",str(y))
				#inp_update_token_value("ray.inp","#ray_zsrc",str(z))

			self.update()
	#	self.lastPos=None


	def isChecked(self): 
		""" Prints selected menu labels. """ 
		[print(action.text()) for action in self.m.actions() if action.isChecked()]


	def wheelEvent(self,event):
		p=event.angleDelta()
		self.view.zoom =self.view.zoom - p.y()/120
		self.update()

