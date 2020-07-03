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

## @package gl_lib
#  general backend for the OpenGL viewer.
#

import sys
from gl_save import gl_save_list
from gl_save import gl_save_add

try:
	from OpenGL.GL import *
	from OpenGL.GLU import *
	from PyQt5 import QtOpenGL
	from PyQt5.QtOpenGL import QGLWidget
	from gl_color import set_color
	open_gl_ok=True
except:
	print("opengl error from gl_lib",sys.exc_info()[0])

import random
import numpy as np
from math import pi,acos,sin,cos

from gl_scale import scale_get_xmul
from gl_scale import scale_get_ymul
from gl_scale import scale_get_zmul


stars=[]

def gl_obj_id_starts_with(ids,val):

	found=False
	for id in ids:
		if id.startswith(val)==True:
			found=True
			break
	return found

def gl_obj_id_extract_starts_with(ids,val):
	for id in ids:
		if id.startswith(val)==True:
			return id
	return False

def gl_save_draw():
	save_list=gl_save_list()
	delta=6
	for i in range(0,len(save_list)):
		split=save_list[i].vec.split()
		if "box" in save_list[i].id:
			w=float(split[0])
			h=float(split[1])
			d=float(split[2])
			r=float(split[3])
			g=float(split[4])
			b=float(split[5])
			alpha=float(split[6])
			box(save_list[i].x+delta,save_list[i].y,save_list[i].z,w,h,d,r,g,b,alpha)
		elif "photon" in save_list[i].id:
			x=save_list[i].x
			z=save_list[i].z
			up=bool(split[0])
			draw_photon(x+delta,2.7,z,up)

def draw_stars():
	global stars
	if len(stars)==0:
		
		for i in range(0,5000):
			phi = random.uniform(0,2*pi)
			costheta = random.uniform(-1,1)
			theta = acos( costheta )
			r=70+random.uniform(0,300)
			x = r * sin( theta) * cos( phi )
			y = r * sin( theta) * sin( phi )
			z = r * cos( theta )
			color=random.uniform(0,1.0)
			r=color
			g=color
			b=color
			s=random.uniform(1,3)	
			stars.append([x,y,z,r,g,b,s])
	
		stars.append([x,4,z,0.5,0.0,0.0,5])
		
	for i in range(0,len(stars)):
		glPointSize(stars[i][6])
		set_color(stars[i][3],stars[i][4],stars[i][5],"star")

		glBegin(GL_POINTS)
		glVertex3f(stars[i][0],stars[i][1],stars[i][2])
		#glVertex3f(-1.0,-1.0,0.0)
		glEnd()

def plane(o):
	glColor4f(o.r, o.g, o.b,0.5)
	glBegin(GL_QUADS)

	glVertex3f(o.x, o.y, o.z)
	glVertex3f(o.x+o.dx, o.y+o.dy, o.z)

	glVertex3f(o.x+o.dx, o.y+o.dy, o.z+o.dz)
	glVertex3f(o.x, o.y, o.z+o.dz)

	glEnd()

def draw_grid():
	glLineWidth(1)

	set_color(0.5, 0.5, 0.5,"grid")

	start_x=-18.0
	stop_x=20.0
	n=int(stop_x-start_x)
	dx=1.0#(stop_x-start_x)/n
	pos=start_x
	glBegin(GL_LINES)
	for i in range(0,n+1):
		glVertex3f(start_x, 0.0, pos)
		glVertex3f(stop_x, 0.0, pos)
		pos=pos+dx


	start_z=-18.0
	stop_z=20.0
	dz=1.0#(stop_z-start_z)/n
	pos=start_z
	for i in range(0,n+1):
		glVertex3f(pos, 0, start_z)
		glVertex3f(pos, 0, stop_z)
		pos=pos+dz

	glEnd()



def draw_photon(x,y,z,up,color=[0.0, 1.0, 0.0]):
	gl_save_add("photon",x,-1.0,z,[int(up)])
	glLineWidth(3)
	length=0.9

	set_color(color[0], color[1], color[2],"photon",alpha=0.5)

	wx=np.arange(0, length , 0.025)
	wy=np.sin(wx*3.14159*8)*0.2
	
	start_y=y+length
	stop_y=y

	glBegin(GL_LINES)
	for i in range(1,len(wx)):
		glVertex3f(x, start_y-wx[i-1], z+wy[i-1])
		glVertex3f(x, start_y-wx[i], z+wy[i])

	glEnd()

	if up==False:
		glBegin(GL_TRIANGLES)

		glVertex3f(x-0.1, stop_y,z)
		glVertex3f(x+0.1, stop_y ,z)
		glVertex3f(x,stop_y-0.1 ,z)

		glEnd()
	else:
		glBegin(GL_TRIANGLES)

		glVertex3f(x-0.1, start_y,z)
		glVertex3f(x+0.1, start_y ,z)
		glVertex3f(x,start_y+0.1 ,z)

		glEnd()

def raw_ray(o):
	glLineWidth(5)
	set_color(o.r, o.g, o.b,"rays")
	glBegin(GL_LINES)
	glVertex3f(o.x, o.y, o.z)
	glVertex3f(o.x+o.dx, o.y+o.dy, o.z+o.dz)
	glEnd()

def paint_ball(o):
	glPushMatrix()
	quad=gluNewQuadric()
	glTranslatef(o.x,o.y,o.z)
	set_color(o.r,o.g,o.b,o.id,alpha=o.alpha)
	gluSphere(quad,o.dx,32,32)
	glPopMatrix()

def paint_line(o):
	glLineWidth(1)
	set_color(o.r,o.g,o.b,o.id,alpha=o.alpha)
	glBegin(GL_LINES)
	glVertex3f(o.x, o.y, o.z)
	glVertex3f(o.x+o.dx, o.y+o.dy, o.z+o.dz)
	glEnd()

def paint_resistor(o):
	glLineWidth(4)
	set_color(o.r,o.g,o.b,o.id,alpha=o.alpha)
	glBegin(GL_LINES)
	glVertex3f(o.x, o.y, o.z)
	glVertex3f(o.x+o.dx, o.y+o.dy, o.z+o.dz)
	glEnd()


	glLineWidth(10)
	set_color(0.0,0.0,1.0,o.id,alpha=o.alpha)
	glBegin(GL_LINES)
	glVertex3f(o.x+o.dx*0.3, o.y+o.dy*0.3, o.z+o.dz*0.3)
	glVertex3f(o.x+o.dx*0.7, o.y+o.dy*0.7, o.z+o.dz*0.7)
	glEnd()

def paint_diode(o):
	glLineWidth(4)
	set_color(o.r,o.g,o.b,o.id,alpha=o.alpha)
	glBegin(GL_LINES)
	glVertex3f(o.x, o.y, o.z)
	glVertex3f(o.x+o.dx, o.y+o.dy, o.z+o.dz)
	glEnd()


	glLineWidth(7)
	set_color(0.0,1.0,0.0,o.id,alpha=o.alpha)
	glBegin(GL_LINES)
	#arrow btm
	glVertex3f(o.x-0.1, o.y+o.dy*0.3, o.z)
	glVertex3f(o.x+0.1, o.y+o.dy*0.3, o.z)
	#bar top
	glVertex3f(o.x-0.1, o.y+o.dy*0.7, o.z)
	glVertex3f(o.x+0.1, o.y+o.dy*0.7, o.z)

	#arrow left
	glVertex3f(o.x-0.1, o.y+o.dy*0.3, o.z)
	glVertex3f(o.x, o.y+o.dy*0.7, o.z)

	#arrow right
	glVertex3f(o.x+0.1, o.y+o.dy*0.3, o.z)
	glVertex3f(o.x, o.y+o.dy*0.7, o.z)

	glEnd()

def box_lines(x,y,z,w,h,d):

	glLineWidth(10)

	set_color(1.0, 1.0, 0.0,"box_lines")

	glBegin(GL_LINES)

	#btm

	glVertex3f(x+0.0,y+0.0,z+0.0)
	glVertex3f(x+w,y+ 0.0,z+0.0)

	glVertex3f(x+w,y+ 0.0,z+0.0)
	glVertex3f(x+w,y+ 0.0,z+d)

	glVertex3f(x+w,y+ 0.0,z+d)
	glVertex3f(x+ 0.0, y+0.0,z+ d) 


	#
	glVertex3f(x+0.0,y+h,z+0.0)
	glVertex3f(x+w,y+ h,z+0.0)


	glVertex3f(x+w,y+ h,z+0.0)
	glVertex3f(x+w,y+ h,z+d)
	
	glVertex3f(x+w,y+ h,z+d)	
	glVertex3f(x+ 0.0, y+h,z+ d) 

	#right

	glVertex3f(x+w,y,z)
	glVertex3f(x+w,y+ h,z)

	glVertex3f(x+w,y+ h,z)
	glVertex3f(x+w,y+ h,z+d)

	glVertex3f(x+w,y+ h,z+d)	
	glVertex3f(x+w, y,z+d) 

	#left

	glVertex3f(x,y,z)
	glVertex3f(x,y+ h,z)

	glVertex3f(x,y+ h,z)
	glVertex3f(x,y+ h,z+d)
	
	glVertex3f(x,y+ h,z+d)
	glVertex3f(x, y,z+d) 


#
	glVertex3f(x,y,z+d)
	glVertex3f(x+w,y,z+d)

	glVertex3f(x+w,y,z+d)
	glVertex3f(x+w,y+h,z+d)

	glVertex3f(x+w,y+h,z+d)	
	glVertex3f(x, y+h,z+d) 


	#top
	glVertex3f(x,y+h,z)
	glVertex3f(x+w,y+ h,z)

	glVertex3f(x+w,y+ h,z)
	glVertex3f(x+w,y+ h,z+ d)
	
	glVertex3f(x+w,y+ h,z+ d)
	glVertex3f(x, y+h,z+ d) 

	glEnd()

def val_to_rgb(v):
	if v>1.0:
		v=0.99

	mesh=[   0.0, 0.5, 1.0]
	colors = [(0, 0, 1.0), (0, 1.0, 0), (1.0, 0, 0)]
	i0=0
	while(1):
		if mesh[i0]<v:
			i0=i0+1
		else:
			i0=i0-1
			break

	i1 = i0+1
	dx=1.0/(len(colors)-1)
	#print(i0,v)

	f=(v-mesh[i0])/dx
	#print(i0)
	#print(i1)
	#print(f)
	#print(i_f)
	#print(v)
	#print(len(colors)-1)
	#print(i)
	#print(f)
	(r0, g0, b0) = colors[i0]
	(r1, g1, b1) = colors[i1]
	#print(i0,i1,f,v,mesh[i0])
	return r0 + f*(r1-r0), g0 + f*(g1-g0), b0 + f*(b1-b0)

