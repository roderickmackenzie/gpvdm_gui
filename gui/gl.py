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

## @package gl
#  The main OpenGL display.
#

import sys
open_gl_ok=False

try:
	from OpenGL.GLU import *
	from OpenGL.GL import *
	from PyQt5 import QtOpenGL
	from PyQt5.QtOpenGL import QGLWidget
	open_gl_ok=True
except:
	print("opengl error ",sys.exc_info()[0])

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QScreen
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QMenu, QColorDialog, QAction

import os

#inp
from inp import inp_load_file
from inp import inp_search_token_value

#path
from cal_path import get_materials_path
from cal_path import get_sim_path

#contacts
from contacts_io import contacts_get_contacts
from contacts_io import contacts_get_array


#epitaxy
from epitaxy import epitaxy_get_layers
from epitaxy import epitaxy_get_width
from epitaxy import epitaxy_get_dos_file
from epitaxy import epitaxy_get_layer
from epitaxy import epitaxy_get_epi
from epitaxy import get_epi

#qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import qRgba

from PyQt5.QtGui import QPainter,QFont,QColor,QPen
from PyQt5.QtGui import QPainterPath,QPolygonF
from PyQt5.QtCore import QRectF,QPoint

import numpy as np
from inp import inp_get_token_value
from util import str2bool

import random

from dat_file import dat_file

import glob

from gl_lib import draw_stars
from gl_lib import draw_grid
from gl_lib import draw_photon
from gl_lib import box_lines
from gl_lib import box

from gl_lib_ray import draw_rays
from gl_lib_ray import fast_data

from global_objects import global_object_register

from inp import inp_search_token_array
from math import fabs
from gl_color import color
# Rotations for cube.
cube_rotate_x_rate = 0.2
cube_rotate_y_rate = 0.2
cube_rotate_z_rate = 0.2


from gl_color import set_color
from gl_color import clear_color
from gl_color import print_color
from gl_color import set_false_color
from gl_color import search_color

from gl_save import gl_save_clear
from gl_save import gl_save_print
from gl_save import gl_save_save
from gl_lib import gl_save_draw
from gl_save import gl_save_load

from open_save_dlg import save_as_filter

from OpenGL.GLU import *

import time
import copy

from thumb import thumb_nail_gen

from gl_view_point import view_point 
from gl_view_point import gl_move_view
from gl_graph import draw_mode
from gl_graph import graph
from gl_active_tab import tab	

from gl_lib import val_to_rgb

from gl_mesh import gl_mesh

from inp import inp_callback_add_write_hook

from mesh import mesh_get_xmesh
from mesh import mesh_get_ymesh
from mesh import mesh_get_zmesh

from mesh import mesh_get_xlen

from gl_layer_editor import gl_layer_editor

from gl_cords import gl_cords

from gl_lib import shape_layer
from gl_base_widget import gl_base_widget

from gl_scale import scale_get_xmul
from gl_scale import scale_get_ymul
from gl_scale import scale_get_zmul

from gl_scale import scale_get_device_y
from gl_scale import scale_get_device_x
from gl_scale import scale_get_device_z

from gl_scale import scale_get_start_x
from gl_scale import scale_get_start_z
from gl_scale import scale_get_start_y

from gl_scale import scale_m2screen_x
from gl_scale import scale_m2screen_z
from gl_scale import scale_m2screen_y

from gl_main_menu import gl_main_menu

if open_gl_ok==True:		
	class glWidget(QGLWidget,gl_move_view,gl_mesh,gl_layer_editor,gl_cords,gl_base_widget,gl_main_menu):


		def __init__(self, parent):
			QGLWidget.__init__(self, parent)
			gl_move_view.__init__(self)
			gl_base_widget.__init__(self)
			self.setAutoBufferSwap(False)

			self.failed=True
			self.graph_path=None
			#view pos



			self.selected_layer=""
			self.graph_data=dat_file()


			self.tab_active_layers=True
			self.dy_layer_offset=0.05

			self.draw_electrical_mesh=False
			self.enable_draw_device=True

			#For image
			#self.render_grid=False
			#self.render_text=False
			#self.tab_active_layers=False
			#self.dy_layer_offset=0.1

		def optics(self):

			width=0.02
			leng=0.5
			start_x=-4
			start_z=10

			quad=gluNewQuadric()

			glPushMatrix()
			set_color(1.0,0.0,0.0,"cordinates",alpha=1.0)
			glTranslatef(start_x,0.0,start_z)

			quad=gluNewQuadric()
			glRotatef(90, 0.0, 1.0, 0.0)
			gluCylinder(quad, width, width, leng, 10, 1)
			glTranslatef(0.0,0.0,leng)
			gluCylinder(quad, 0.1, 0.00, 0.2, 10, 1)
			set_color(1.0,1.0,1.0,"cordinates",alpha=1.0)
			if self.view.zoom>-20:
				self.renderText (0.2,0.0,0.0, "x",font)
			glPopMatrix()

			glPushMatrix()
			set_color(0.7,0.7,0.7,"cordinates",alpha=1.0)
			glTranslatef(start_x,0.0,start_z)
			quad=gluNewQuadric()
			#glTranslatef(0.0,0.0,0.0)
			glRotatef(90, -1.0, 0.0, 0.0)
			gluCylinder(quad, width, width, leng, 10, 1)
			glTranslatef(0.0,0.0,leng)
			gluCylinder(quad, 0.1, 0.00, 0.2, 10, 1)
			set_color(1.0,1.0,1.0,"cordinates",alpha=1.0)
			if self.view.zoom>-20:
				self.renderText (0.2,0.0,0.0, "y",font)
			glPopMatrix()

			glPushMatrix()
			set_color(0.7,0.7,0.7,"cordinates",alpha=1.0)
			glTranslatef(start_x,0.0,start_z)

			quad=gluNewQuadric()
			glRotatef(180, 0.0, 1.0, 0.0)
			gluCylinder(quad, width, width, leng, 10, 1)
			glTranslatef(0.0,0.0,leng)
			gluCylinder(quad, 0.1, 0.00, 0.2, 10, 1)

			gluSphere(quad,0.08,32,32)
			set_color(1.0,1.0,1.0,"cordinates",alpha=1.0)
			if self.view.zoom>-20:
				self.renderText (-0.2,0.0,0.0, "z",font)
			glPopMatrix()

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
			self.render()
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

			if event.buttons()==Qt.LeftButton:
				
				self.view.xRot =self.view.xRot - 1 * dy
				self.view.yRot =self.view.yRot - 1 * dx

			if event.buttons()==Qt.RightButton:
				self.view.x_pos =self.view.x_pos + 0.1 * dx
				self.view.y_pos =self.view.y_pos - 0.1 * dy
				

			self.lastPos=event.pos()
			self.setFocusPolicy(Qt.StrongFocus)
			self.setFocus()
			self.update()
			#self.view_dump()

		def mousePressEvent(self,event):
			self.lastPos=None
			self.mouse_click_time=time.time()
			self.obj=self.event_to_3d_obj(event)

			if self.obj.startswith("layer")==True:
				self.selected_layer=self.obj
				self.do_draw()

			if event.buttons()==Qt.LeftButton:
				#thumb_nail_gen()
				#self.mouse_click_time=time.time()
				x = event.x()
				y = self.height()-event.y()
				set_false_color(True)
				self.render()
				data=glReadPixelsub(x, y, 1, 1, GL_RGBA,GL_FLOAT)
				set_false_color(False)

				c=color(int(255*data[0][0][0]),int(255*data[0][0][1]),int(255*data[0][0][2]))

				self.obj=search_color(c)
				if self.obj=="none":
					return

				print("you have clicked on=",self.obj)



		def mouseReleaseEvent(self,event):
			self.obj=self.event_to_3d_obj(event)

			if event.button()==Qt.RightButton:
				delta=time.time() - self.mouse_click_time
				if (delta)<0.5:
					if self.obj!="none":
						if self.obj.startswith("layer")==True:
							self.selected_layer=self.obj
							self.do_draw()
							self.menu_layer(event)

							return
						if self.obj.startswith("mesh")==True:
							self.mesh_menu(event)
					else:
						self.menu(event)

		#	self.lastPos=None


		def isChecked(self): 
			""" Prints selected menu labels. """ 
			[print(action.text()) for action in self.m.actions() if action.isChecked()]



		def wheelEvent(self,event):
			p=event.angleDelta()
			self.view.zoom =self.view.zoom - p.y()/120
			self.update()

		def draw_photons(self,x0,z0):
			up_photons=False
			device_top=scale_get_device_y()
			if self.light_illuminate_from=="bottom":
				y=-1.5
				up_photons=True
			else:
				y=device_top

			if self.suns!=0:
				if self.suns<=0.01:
					den=1.4
				elif self.suns<=0.1:
					den=0.8
				elif self.suns<=1.0:
					den=0.6
				elif self.suns<=10.0:
					den=0.3
				else:
					den=0.2

				x=np.arange(x0, x0+scale_get_device_x() , den)
				z=np.arange(z0, z0+scale_get_device_z() , den)
				for i in range(0,len(x)):
					for ii in range(0,len(z)):
						draw_photon(x[i],y+0.1,z[ii],up_photons,color=[0.0, 1.0, 0.0])

			if self.emission==True and self.ray_model==False:
				den=1.2
				#x=np.arange(0, max_gui_device_x , den)
				#y=np.arange(0, max_gui_device_z , den)
				x=np.arange(x0, x0+scale_get_device_x() , den)
				z=np.arange(z0, z0+scale_get_device_z() , den)
				for i in range(0,len(x)):
					for ii in range(0,len(z)):
						draw_photon(x[i]+0.1,device_top+0.1,z[ii],True,color=[0.0, 0.0, 1.0])



		def bix_axis(self):
			for xx in range(0,10):
				box(0+xx,0,0,0.5,0.5,0.5,1.0,0,0,0.5)

			for yy in range(0,10):
				box(0,0+yy,0,0.5,0.5,0.5,1.0,0,0,0.5)


			for zz in range(0,10):
				box(0,0,0+zz,0.5,0.5,0.5,0.0,0,1,0.5)


		def draw_device(self,x,z):


			y=scale_get_device_y()


			l=0
			btm_layer=len(epitaxy_get_epi())-1

			for obj in epitaxy_get_epi():
				y_len=obj.width*scale_get_ymul()
				y=y-y_len
				dy_shrink=y_len*0.1

				name=obj.name
				layer_name="layer:"+name
				display_name=name
				alpha=obj.alpha
				if len(obj.shapes)>0:
					for s in obj.shapes:
						shape_layer(obj,s,x,y+dy_shrink/2, z, name=layer_name)
					alpha=0.5

				if obj.electrical_layer=="contact":

					for c in contacts_get_array():
						if (c.position=="top" and l==0) or (c.position=="bottom" and l==btm_layer):
							if len(self.x_mesh.points)==1 and len(self.z_mesh.points)==1:
								xstart=x
								xwidth=scale_get_device_x()
							else:
								xstart=x+scale_get_xmul()*c.start
								xwidth=scale_get_xmul()*c.width
								#print(c.position,xstart,xwidth)
								if (c.start+c.width)>self.x_len:
									xwidth=scale_get_device_x()
							#lens_layer(xstart,y+dy_shrink/2,z,xwidth,scale_get_device_z(),y_len-dy_shrink,scale_get_device_x()/10)

							box(xstart,y+dy_shrink/2,z,xwidth,y_len-dy_shrink, scale_get_device_z(), obj.r,obj.g, obj.b,alpha, name=layer_name)
				else:
					box(x,y+dy_shrink/2,z,scale_get_device_x(),y_len-dy_shrink,scale_get_device_z(),obj.r,obj.g,obj.b,alpha,name=layer_name)

				if obj.electrical_layer.startswith("dos")==True:
					tab(x+scale_get_device_x(),y,z,y_len-dy_shrink)
					display_name=display_name+" ("+_("active")+")"

				if self.selected_layer==layer_name:
					box_lines(x,y,z,scale_get_device_x(),y_len,scale_get_device_z())

				if self.view.render_text==True:
					if self.view.zoom<20:
						set_color(1.0,1.0,1.0,"text")
						font = QFont("Arial")
						font.setPointSize(18)
						self.renderText (x+scale_get_device_x()+0.1,y+y_len/2,z, display_name,font)

				l=l+1

				

		def render(self):

			self.update_real_to_gl_mul()
			x=scale_m2screen_x(0)
			y=0.0#scale_m2screen_y(0)
			z=scale_m2screen_z(0)

			clear_color()
			glClearColor(self.view.bg_color[0], self.view.bg_color[1], self.view.bg_color[2], 0.5)
			gl_save_clear()


			self.dos_start=-1
			self.dos_stop=-1



			self.emission=False
			self.ray_model=False
			
			lines=inp_load_file(os.path.join(get_sim_path(),"led.inp"))

			if lines!=False:
				self.ray_model=val=str2bool(inp_search_token_value(lines, "#led_on"))
				
			lines=[]

			for i in range(0,epitaxy_get_layers()):
				if epitaxy_get_dos_file(i)!="none":
					lines=inp_load_file(os.path.join(get_sim_path(),epitaxy_get_dos_file(i)+".inp"))
					if lines!=False and len(lines)!=0:
						if str2bool(lines[3])==True:
							self.emission=True
					
			glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
			glLoadIdentity()
			glScalef(1.0, 1.0, -1.0) 

			glTranslatef(self.view.x_pos, self.view.y_pos, self.view.zoom) # Move Into The Screen
			
			glRotatef(self.view.xRot, 1.0, 0.0, 0.0)
			glRotatef(self.view.yRot, 0.0, 1.0, 0.0)
			glRotatef(self.view.zRot, 0.0, 0.0, 1.0)

			glColor3f( 1.0, 1.5, 0.0 )
			glPolygonMode(GL_FRONT, GL_FILL);

			threed_files=glob.glob("*.3d")
			if len(threed_files)>0:
				gl_save_load()
				gl_save_draw()
				draw_grid()
				return

			#glClearColor(0.92, 0.92, 0.92, 0.5) # Clear to black.

			lines=[]

			self.pos=0.0
			
			self.draw_cords()
			if self.draw_electrical_mesh==True:
				self.draw_mesh()
			else:
				if self.enable_draw_device==True:
					self.draw_device(x,z)
				draw_mode(x,y,z,scale_get_device_y())
				draw_rays(x,y,z,self.ray_file,scale_get_device_y()-self.dy_layer_offset,scale_get_device_x(),scale_get_ymul(),scale_get_device_z()*1.05)

				if self.view.render_photons==True:
					self.draw_photons(x,z)

				graph(scale_get_start_x(),0.0,scale_get_start_z()-0.2,scale_get_device_x(),scale_get_device_y(),self.graph_data)

			if self.view.render_grid==True:
				draw_grid()

			if self.view.zoom>self.view.stars_distance:
				draw_stars()


		def do_draw(self):
			self.render()
			self.swapBuffers()
			#gl_save_print()

		#def paintEvent(self, e):
		#	qp = QPainter()
		#	qp.begin(self)

		#	path=QPainterPath()
		#	path.addRoundedRect(QRectF(0, 0, 1000, 100), 0, 0)
		#	qp.fillPath(path,QColor(206 , 206, 206))

		#	qp.end()



		def paintGL(self):

			if self.failed==False:
				self.do_draw()

			#return


		def load_data(self):
			lines=[]

			val=inp_get_token_value(os.path.join(get_sim_path(),"light.inp"), "#Psun")
			self.dump_energy_slice_xpos=int(inp_get_token_value(os.path.join(get_sim_path(),"dump.inp"), "#dump_energy_slice_xpos"))
			self.dump_energy_slice_ypos=int(inp_get_token_value(os.path.join(get_sim_path(),"dump.inp"), "#dump_energy_slice_ypos"))
			self.dump_energy_slice_zpos=int(inp_get_token_value(os.path.join(get_sim_path(),"dump.inp"), "#dump_energy_slice_zpos"))
			self.light_illuminate_from=inp_get_token_value(os.path.join(get_sim_path(),"light.inp"), "#light_illuminate_from")
			self.dump_1d_slice_xpos=int(inp_get_token_value(os.path.join(get_sim_path(),"dump.inp"), "#dump_1d_slice_xpos"))
			self.dump_1d_slice_zpos=int(inp_get_token_value(os.path.join(get_sim_path(),"dump.inp"), "#dump_1d_slice_zpos"))

			self.dump_verbose_electrical_solver_results=str2bool(inp_get_token_value(os.path.join(get_sim_path(),"dump.inp"), "#dump_verbose_electrical_solver_results"))
			try:
				self.suns=float(val)
			except:
				self.suns=0.0

			self.y_mesh=mesh_get_ymesh()
			self.x_mesh=mesh_get_xmesh()
			self.z_mesh=mesh_get_zmesh()

			self.x_len=mesh_get_xlen()

		def random_device(self):
			self.view.render_grid=True
			self.view.render_photons=True
			self.view.render_text=False

			for i in range(0,100):
				r=random.randint(0,epitaxy_get_layers()-1)
				w=float(random.randint(20,100))*1e-9
				e=epitaxy_get_epi()
				e[r].width=w
				levels = range(32,256,32)
				color=tuple(random.choice(levels) for _ in range(3))
				if r!=2:
					e[r].r=color[0]/256.0
					e[r].g=color[1]/256.0
					e[r].b=color[2]/256.0

				self.do_draw()
				self.grabFrameBuffer().save("./one/a"+str(i)+".png")
			
		def force_redraw(self):
			self.load_data()
			self.update()

			#y_mesh.calculate_points()
			#x_mesh.calculate_points()
			#z_mesh.calculate_points()
			self.do_draw()

		def resizeEvent(self,event):
			if self.failed==False:
				#glClearDepth(1.0)              
				#glDepthFunc(GL_LESS)
				#glEnable(GL_DEPTH_TEST)
				#glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
				#glEnable(GL_BLEND);
				#glShadeModel(GL_SMOOTH)
				glViewport(0, 0, self.width(), self.height()+100)
				glMatrixMode(GL_PROJECTION)
				glLoadIdentity()
				#glScalef(1.0, 1.0, -1.0)              
				gluPerspective(45.0,float(self.width()) / float(self.height()+100),0.1, 1000.0) 
				glMatrixMode(GL_MODELVIEW)


		def initializeGL(self):
			self.load_data()
			try:
				glClearDepth(1.0)              
				glDepthFunc(GL_LESS)
				glEnable(GL_DEPTH_TEST)
				glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
				glEnable(GL_BLEND);
				#glEnable(GL_PROGRAM_POINT_SIZE_EXT);
				glShadeModel(GL_SMOOTH)

				#glEnable(GL_COLOR_MATERIAL)
				#glEnable(GL_CULL_FACE)
				#glEnable(GL_DEPTH_TEST)
				#glEnable(GL_LIGHTING)
				#lightZeroPosition = [3,-3,3,1.0]
				#lightZeroColor = [1.0,1.0,1.0,1.0] #green tinged
				#glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
				#glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
				#glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.01)
				#glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.01)
				#glEnable(GL_LIGHT0)

				#lightZeroColor = [0.7,0.7,0.7,0.7] #green tinged
				#glLightfv(GL_LIGHT1, GL_POSITION, lightZeroPosition)
				#glLightfv(GL_LIGHT1, GL_AMBIENT, lightZeroColor)
				#glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 0.01)
				#glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.01)
				#glEnable(GL_LIGHT1)

				#glEnable(GL_FOG);
				#fogColor = [0.5, 0.5, 0.5, 1.0];

				#glFogi (GL_FOG_MODE, GL_EXP);
				#glFogfv (GL_FOG_COLOR, fogColor);
				#glFogf (GL_FOG_DENSITY, 0.35);
				#glHint (GL_FOG_HINT, GL_DONT_CARE);
				#glFogf (GL_FOG_START, 1.0);
				#glFogf (GL_FOG_END, 5.0);

				glViewport(0, 0, self.width(), self.height()+100)
				glMatrixMode(GL_PROJECTION)
				glLoadIdentity()
				#glScalef(1.0, 1.0, -1.0)                  
				gluPerspective(45.0,float(self.width()) / float(self.height()+100),0.1, 1000.0) 
				glMatrixMode(GL_MODELVIEW)
				#self.resizeEvent.connect(self.resize)
			
				self.failed=False
				global_object_register("gl_force_redraw",self.force_redraw)
				inp_callback_add_write_hook(os.path.join(get_sim_path(),"light.inp"),self.force_redraw,"gl")
			except:
				print("OpenGL failed to load falling back to 2D rendering.",sys.exc_info()[0])

else:
	class glWidget(QWidget):

		def __init__(self, parent):
			QWidget.__init__(self)
			self.failed=True
