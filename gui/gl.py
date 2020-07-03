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
from PyQt5.QtGui import QScreen
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QMenu, QColorDialog, QAction

import os

#inp
from inp import inp_load_file
from inp import inp_search_token_value

#path
from cal_path import get_materials_path
from cal_path import get_sim_path


#epitaxy
from epitaxy import epitaxy_get_layers
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
from str2bool import str2bool

import random

from dat_file import dat_file

import glob

from gl_lib import draw_stars
from gl_lib import draw_grid
from gl_lib import draw_photon
from gl_lib import box_lines
from gl_shapes import box

from global_objects import global_object_register

from inp import inp_search_token_array
from math import fabs
# Rotations for cube.
cube_rotate_x_rate = 0.2
cube_rotate_y_rate = 0.2
cube_rotate_z_rate = 0.2


from gl_color import set_color
from gl_color import clear_color
from gl_color import print_color


from gl_save import gl_save_clear
from gl_save import gl_save_print
from gl_save import gl_save_save
from gl_lib import gl_save_draw
from gl_save import gl_save_load

from OpenGL.GLU import *

import copy

from thumb import thumb_nail_gen

from gl_view_point import view_point 
from gl_view_point import gl_move_view
from gl_graph import draw_mode
from gl_active_tab import tab	

from gl_lib import val_to_rgb

from gl_mesh import gl_mesh


from mesh import get_mesh

from gl_layer_editor import gl_layer_editor

from gl_cords import gl_cords

from gl_shape_layer import shape_layer
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

from gl_scale import project_m2screen_x
from gl_scale import project_m2screen_z
from gl_scale import project_m2screen_y

from gl_main_menu import gl_main_menu

from gl_list import gl_objects

from gl_scale import scale_screen_x2m
from gl_scale import scale_screen_y2m

from inp import inp_update_token_value
from file_watch import get_watch
from gl_input import gl_input

from gl_text import gl_text
from gl_lib_ray import gl_lib_ray
from gl_contacts import gl_contacts
from gl_graph import gl_graph
from gl_draw_circuit import gl_draw_circuit
from gl_draw_light_profile import gl_draw_light_profile

class open_gl_light:
	def __init__(self):
		self.xyz=[0, 5, -10, 1.0]
		self.number=GL_LIGHT0

if open_gl_ok==True:		
	class glWidget(QGLWidget,shape_layer, gl_lib_ray,gl_objects, gl_text,gl_move_view,gl_mesh,gl_layer_editor,gl_cords,gl_base_widget,gl_main_menu,gl_input, gl_contacts, gl_draw_light_profile, gl_graph, gl_draw_circuit):

		def __init__(self, parent):
			QGLWidget.__init__(self, parent)
			gl_move_view.__init__(self)
			gl_base_widget.__init__(self)
			gl_objects.__init__(self)
			gl_lib_ray.__init__(self)
			gl_text.__init__(self)
			self.lit=True
			self.setAutoBufferSwap(False)

			self.lights=[]

			l=open_gl_light()
			l.xyz=[0, 5, -10, 1.0]
			l.number=GL_LIGHT0
			self.lights.append(l)

			l=open_gl_light()
			l.xyz=[0, 5, 10, 1.0]
			l.number=GL_LIGHT1
			self.lights.append(l)

			self.failed=True
			self.graph_path=None
			self.scene_built=False
			#view pos

			self.selected_layer=""
			self.graph_data=dat_file()


			self.tab_active_layers=True
			self.dy_layer_offset=0.05

			self.draw_electrical_mesh=False
			self.draw_device_cut_through=False
			self.enable_draw_ray_mesh=False
			self.enable_draw_light_source=False
			self.enable_draw_rays=True
			self.enable_cordinates=True
			self.plot_graph=False
			self.plot_circuit=False

			#For image
			#self.render_grid=False
			#self.render_text=False
			#self.tab_active_layers=False
			#self.dy_layer_offset=0.1
			self.font = QFont("Arial")
			self.font.setPointSize(15)
			self.called=False
			self.enable_light_profile=True
			self.build_main_menu()

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
				self.render_text (0.2,0.0,0.0, "x",self.font)
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
				self.render_text (0.2,0.0,0.0, "y",self.font)
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
				self.render_text (-0.2,0.0,0.0, "z",self.font)
			glPopMatrix()

		def draw_photons(self,x0,z0):
			up_photons=False
			device_top=scale_get_device_y()
			if self.light_illuminate_from=="bottom":
				y=-1.5
				up_photons=True
			else:
				y=device_top+0.5

			dx=scale_get_device_x()

			if self.suns!=0:
				if self.suns<=0.01:
					den=dx/5
				elif self.suns<=0.1:
					den=dx/8
				elif self.suns<=1.0:
					den=dx/10
				elif self.suns<=10.0:
					den=dx/20
				else:
					den=dx/25

				x=np.arange(x0+den/2.0, x0+scale_get_device_x() , den)
				z=np.arange(z0+den/2.0, z0+scale_get_device_z() , den)

				for i in range(0,len(x)):
					for ii in range(0,len(z)):
						draw_photon(x[i],y,z[ii],up_photons,color=[0.0, 1.0, 0.0])

			if self.emission==True and self.ray_model==False:
				den=1.2
				#x=np.arange(0, max_gui_device_x , den)
				#y=np.arange(0, max_gui_device_z , den)
				x=np.arange(x0, x0+scale_get_device_x() , den)
				z=np.arange(z0, z0+scale_get_device_z() , den)

				for i in range(0,len(x)):
					for ii in range(0,len(z)):
						draw_photon(x[i]+0.1,y+0.1,z[ii],True,color=[0.0, 0.0, 1.0])


		def bix_axis(self):
			for xx in range(0,10):
				box(0+xx,0,0,0.5,0.5,0.5,1.0,0,0,0.5)

			for yy in range(0,10):
				box(0,0+yy,0,0.5,0.5,0.5,1.0,0,0,0.5)


			for zz in range(0,10):
				box(0,0,0+zz,0.5,0.5,0.5,0.0,0,1,0.5)

		def draw_device2(self,x,z):
			y=scale_get_device_y()


			l=0
			btm_layer=len(epitaxy_get_epi())-1

			for obj in epitaxy_get_epi():
				y_len=obj.dy*scale_get_ymul()
				y=y-y_len
				dy_shrink=y_len*0.1

				name=obj.name
				layer_name="layer:"+name
				display_name=name
				alpha=obj.alpha
				if len(obj.shapes)>0:
					self.shape_layer(obj,obj.shapes, y_padding=dy_shrink/2, name=layer_name)


		def draw_device(self,x,z):
			epi=get_epi()
			y=scale_get_device_y()

			contact_layers=epi.contacts.get_layers_with_contacts()

			l=0
			btm_layer=len(epitaxy_get_epi())-1

			for obj in epi.layers:
				y_len=obj.dy*scale_get_ymul()
				y=y-y_len
				dy_shrink=y_len*0.1

				name=obj.name
				layer_name="layer:"+name
				display_name=name
				alpha=obj.alpha
				if len(obj.shapes)>0:
					alpha=0.5

				contact_layer=False
				if l==0 and "top" in contact_layers:
					contact_layer=True

				if l==len(epi.layers)-1 and "bottom" in contact_layers:
					contact_layer=True

				if name!="air" and contact_layer==False:
					if self.draw_device_cut_through==False and l!=len(epi.layers)-1 :
						box(x,y+dy_shrink/2,z,scale_get_device_x(), y_len-dy_shrink,scale_get_device_z(), obj.r,obj.g,obj.b, alpha,name=[layer_name])
					else:
						box(x,y+dy_shrink/2,z,scale_get_device_x(), y_len-dy_shrink,scale_get_device_z(), obj.r,obj.g,obj.b, alpha,name=[layer_name],cut_through=True)

				if obj.dos_file.startswith("dos")==True:
					tab(x+scale_get_device_x(),y,z,y_len-dy_shrink)
					display_name=display_name+" ("+_("active")+")"

				if self.selected_layer==layer_name:
					box_lines(x,y,z,scale_get_device_x(),y_len,scale_get_device_z())

				if self.view.render_text==True:
					if self.view.zoom<40:
						set_color(1.0,1.0,1.0,"text")
						self.render_text (x+scale_get_device_x()+0.1,y+y_len/2,z, display_name,self.font)

				l=l+1

		def reset(self):
			self.update_real_to_gl_mul()
			self.rebuild_scene()


		def render(self):

			self.update_real_to_gl_mul()

			x=project_m2screen_x(0)
			y=0.0#project_m2screen_y(0)
			z=project_m2screen_z(0)

			clear_color()
			glClearColor(self.view.bg_color[0], self.view.bg_color[1], self.view.bg_color[2], 0.5)
			gl_save_clear()


			self.dos_start=-1
			self.dos_stop=-1



			self.emission=False
			self.ray_model=False
			
			lines=inp_load_file(os.path.join(get_sim_path(),"ray.inp"))

			if lines!=False:
				self.ray_model=val=str2bool(inp_search_token_value(lines, "#ray_auto_run"))

			lines=[]
			epi=get_epi()
			for i in range(0,len(epi.layers)):
				if epi.layers[i].dos_file!="none":
					lines=inp_load_file(os.path.join(get_sim_path(),epi.layers[i].dos_file+".inp"))
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

			#glClearColor(0.92, 0.92, 0.92, 0.5) # Clear to black.

			lines=[]

			self.pos=0.0
			if self.enable_cordinates==True:
				self.draw_cords()

			if self.enable_draw_ray_mesh==True:
				self.draw_ray_mesh()
				
			if self.view.draw_device==True:
				self.draw_device(x,z)

			if self.view.optical_mode==True:
				draw_mode()

			if self.view.render_photons==True:
				self.draw_photons(x,z)

			if self.view.render_grid==True:
				draw_grid()

			if self.view.zoom>self.view.stars_distance:
				draw_stars()


			if self.scene_built==False:
				self.build_scene()

			if self.plot_graph==True:
				self.draw_graph()

			#for l in self.lights:
			#	box(l.xyz[0],l.xyz[1],l.xyz[2],0.5,0.5,0.5,1.0,0,0,0.5)

			self.gl_objects_render()
			#self.text("Hello world!!!! %^&*(")

		def do_draw(self):
			self.render()
			self.swapBuffers()


		def paintGL(self):
			glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
			glLoadIdentity()
			glScalef(1.0, 1.0, -1.0) 

			glTranslatef(self.view.x_pos, self.view.y_pos, self.view.zoom) # Move Into The Screen
			
			glRotatef(self.view.xRot, 1.0, 0.0, 0.0)
			glRotatef(self.view.yRot, 0.0, 1.0, 0.0)
			glRotatef(self.view.zRot, 0.0, 0.0, 1.0)

			glColor3f( 1.0, 1.5, 0.0 )
			glPolygonMode(GL_FRONT, GL_FILL);

			self.bix_axis()
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

			#self.y_mesh=get_mesh().y
			#self.x_mesh=get_mesh().x
			#self.z_mesh=get_mesh().z

			self.x_len=get_mesh().get_xlen()
			if os.path.isdir(os.path.join(os.path.join(get_sim_path(),"ray_trace")))==True:
				self.view.render_photons=False


		#This will rebuild the scene from scratch
		def rebuild_scene(self):
			self.menu_update()
			self.gl_objects_clear()
			self.text_clear_lib()

			x=project_m2screen_x(0)
			z=project_m2screen_z(0)

			if self.enable_draw_rays==True:
				self.draw_rays(self.ray_file)

			if self.enable_draw_light_source==True:

				lines=inp_load_file(os.path.join(get_sim_path(),"ray.inp"))

				if lines!=False:
					point_x=float(inp_search_token_value(lines, "#ray_xsrc"))
					point_y=float(inp_search_token_value(lines, "#ray_ysrc"))
					if point_x==-1.0:
						point_x=0.0
						point_y=0.0
					else:
						point_x=project_m2screen_x(point_x)
						point_y=project_m2screen_y(point_y)

					a=gl_base_object()
					a.id=["ray_src"]
					a.type="box"
					a.x=point_x
					a.y=point_y
					a.z=0.0
					a.dx=0.2
					a.dy=0.2
					a.dz=0.2
					a.r=0.0
					a.g=0.0
					a.b=1.0

					a.moveable=True
					a.selectable=True
					self.gl_objects_add(a)

			if self.draw_electrical_mesh==True:
				self.draw_mesh()

			elif self.view.draw_device==True:
				self.draw_device2(x,z)
				self.draw_contacts()

			if self.plot_circuit==True:
				self.draw_circuit()

			if self.enable_light_profile==True:
				self.draw_light_profile()

			#print("rebuild")


		def build_scene(self):
			self.update_real_to_gl_mul()
			self.scene_built=True
			self.load_data()
			self.update()
			self.rebuild_scene()

		def force_redraw(self):
			self.build_scene()
			self.do_draw()
			self.menu_update()

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
			#try:
			glClearDepth(1.0)              
			glDepthFunc(GL_LESS)
			glEnable(GL_DEPTH_TEST)
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
			glEnable(GL_BLEND);
			glShadeModel(GL_SMOOTH)



				#lightZeroPosition = [0, 0, -10, 1.0]
				#lightZeroColor = [1.0, 1.0, 1.0, 1.0]
				#glLightfv(GL_LIGHT1, GL_POSITION, lightZeroPosition)
				#glLightfv(GL_LIGHT1,  GL_DIFFUSE, lightZeroColor)
				#glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 0.1)
				#glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.05)
				#glEnable(GL_LIGHT1)

				#lightZeroPosition = [10, 10, 0, 1.0]
				#lightZeroColor = [1.0, 1.0, 1.0, 1.0]
				#glLightfv(GL_LIGHT2, GL_POSITION, lightZeroPosition)
				#glLightfv(GL_LIGHT2,  GL_DIFFUSE, lightZeroColor)
				#glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 0.1)
				#glLightf(GL_LIGHT2, GL_LINEAR_ATTENUATION, 0.05)
				#glEnable(GL_LIGHT2)

#GL_DIFFUSE

			#glEnable(GL_FOG);
			#fogColor = [0.5, 0.5, 0.5, 1.0];

			#glFogi (GL_FOG_MODE, GL_EXP);
			#glFogfv (GL_FOG_COLOR, fogColor);
			#glFogf (GL_FOG_DENSITY, 0.35);
			#glHint (GL_FOG_HINT, GL_DONT_CARE);
			#glFogf (GL_FOG_START, 1.0);
			#glFogf (GL_FOG_END, 5.0);
			#self.tex = self.read_texture('/home/rod/images/image.jpg')
			glViewport(0, 0, self.width(), self.height()+100)
			glMatrixMode(GL_PROJECTION)
			glLoadIdentity()
			#glScalef(1.0, 1.0, -1.0)                  
			gluPerspective(45.0,float(self.width()) / float(self.height()+100),0.1, 1000.0) 
			glMatrixMode(GL_MODELVIEW)
			#self.resizeEvent.connect(self.resize)
		
			if self.lit==True:
				for l in self.lights:
					glEnable(GL_LIGHTING)
					lightZeroColor = [1.0, 1.0, 1.0, 1.0]
					print(l.number,GL_LIGHT1)
					glLightfv(l.number, GL_POSITION, [l.xyz[0],-l.xyz[1],-l.xyz[2] ])
					glLightfv(l.number, GL_DIFFUSE, lightZeroColor)
					#glLightfv(l.number, GL_SPOT_DIRECTION, [ 1,1,1]);
					glLightf(l.number, GL_CONSTANT_ATTENUATION, 0.1)
					glLightf(l.number, GL_LINEAR_ATTENUATION, 0.05)
					glEnable(l.number)

			self.failed=False
			global_object_register("gl_force_redraw",self.force_redraw)
			get_watch().add_call_back("light.inp",self.force_redraw)
			get_epi().add_callback(self.force_redraw)
			#get_watch().add_call_back("shape[0-9]+.inp",self.force_redraw)
			#get_epi().changed.connect(self.boom)
			#except:
			#	print("OpenGL failed to load falling back to 2D rendering.",sys.exc_info()[0])

		def boom(self):
			print("cum")
else:
	class glWidget(QWidget):

		def __init__(self, parent):
			QWidget.__init__(self)
			self.failed=True
