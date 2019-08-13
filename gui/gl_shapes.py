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

from gl_scale import scale_m2screen_x
from gl_scale import scale_m2screen_y
from gl_scale import scale_m2screen_z

from gl_scale import scale_get_xmul
from gl_scale import scale_get_ymul
from gl_scale import scale_get_zmul

def pyrmid(o):
	x=o.x
	y=o.y
	z=o.z
	dx=o.dx
	dy=o.dy
	dz=o.dz
	segs=40
	delta=180/segs
	theata=0
	theta_rad=(theata/360)*2*3.141592653
	set_color(o.r,o.g,o.b,o.id,alpha=o.alpha)

	#top

	glBegin(GL_TRIANGLES)
	glVertex3f(x,y,z)
	glVertex3f(x+dx,y,z)
	glVertex3f(x+dx/2,y+dy,z+dz/2)
	glEnd()

	glBegin(GL_TRIANGLES)
	glVertex3f(x+dx,y,z)
	glVertex3f(x+dx,y,z+dz)
	glVertex3f(x+dx/2,y+dy,z+dz/2)
	glEnd()

	glBegin(GL_TRIANGLES)
	glVertex3f(x+dx,y,z+dz)
	glVertex3f(x,y,z+dz)
	glVertex3f(x+dx/2,y+dy,z+dz/2)
	glEnd()

	glBegin(GL_TRIANGLES)
	glVertex3f(x,y,z)
	glVertex3f(x,y,z+dz)
	glVertex3f(x+dx/2,y+dy,z+dz/2)
	glEnd()

def paint_from_array(o):
	set_color(o.r,o.g,o.b,o.id,alpha=o.alpha)

	dx=o.dx/2
	dy=o.dy/2
	dz=o.dz/2
	
	x=o.x
	y=o.y
	z=o.z

	for t in o.triangles.data:
		glBegin(GL_TRIANGLES)
		glVertex3f(o.x+t.xyz0.x*scale_get_xmul(),o.y+t.xyz0.y*scale_get_ymul(),o.z+t.xyz0.z*scale_get_zmul())
		glVertex3f(o.x+t.xyz1.x*scale_get_xmul(),o.y+t.xyz1.y*scale_get_ymul(),o.z+t.xyz1.z*scale_get_zmul())
		glVertex3f(o.x+t.xyz2.x*scale_get_xmul(),o.y+t.xyz2.y*scale_get_ymul(),o.z+t.xyz2.z*scale_get_zmul())
		glEnd()

def paint_open_triangles_from_array(o):
	set_color(o.r,o.g,o.b,o.id,alpha=o.alpha)

	dx=o.dx/2
	dy=o.dy/2
	dz=o.dz/2
	
	x=o.x
	y=o.y
	z=o.z

	glLineWidth(5)

	for t in o.triangles.data:
		glBegin(GL_LINES)
		glVertex3f(o.x+scale_m2screen_x(t.xyz0.x),o.y+scale_m2screen_y(t.xyz0.y),o.z+scale_m2screen_z(t.xyz0.z))
		glVertex3f(o.x+scale_m2screen_x(t.xyz1.x),o.y+scale_m2screen_y(t.xyz1.y),o.z+scale_m2screen_z(t.xyz1.z))
		glEnd()

		glBegin(GL_LINES)
		glVertex3f(o.x+scale_m2screen_x(t.xyz1.x),o.y+scale_m2screen_y(t.xyz1.y),o.z+scale_m2screen_z(t.xyz1.z))
		glVertex3f(o.x+scale_m2screen_x(t.xyz2.x),o.y+scale_m2screen_y(t.xyz2.y),o.z+scale_m2screen_z(t.xyz2.z))
		glEnd()

		glBegin(GL_LINES)
		glVertex3f(o.x+scale_m2screen_x(t.xyz2.x),o.y+scale_m2screen_y(t.xyz2.y),o.z+scale_m2screen_z(t.xyz2.z))
		glVertex3f(o.x+scale_m2screen_x(t.xyz0.x),o.y+scale_m2screen_y(t.xyz0.y),o.z+scale_m2screen_z(t.xyz0.z))
		glEnd()


def dome(o):
	set_color(o.r,o.g,o.b,o.id,alpha=o.alpha)

	dx0=o.dx/2
	dy0=o.dy/2
	dz0=o.dz/2
	
	x=o.x+dx0
	y=o.y
	z=o.z+dz0

	#top
	theta=0.0
	theta_max=2.0*3.1415
	dtheta=theta_max/10.0

	phi=0.0
	phi_max=3.1415/2.0
	dphi=phi_max/10.0

	while(phi<phi_max):
		theta=0
		while (theta<theta_max):
			glBegin(GL_QUADS)

			dx=dx0*cos(theta)*cos(phi)
			dz=dz0*sin(theta)*cos(phi)
			dy=dy0*sin(phi)

			#print(dx,dy,dz)
			glVertex3f(x+dx,y+dy,z+dz)

			dx=dx0*cos(theta)*cos(phi+dphi)
			dz=dz0*sin(theta)*cos(phi+dphi)
			dy=dy0*sin(phi+dphi)

			#print(dx,dy,dz)
			glVertex3f(x+dx,y+dy,z+dz)

			dx=dx0*cos(theta+dtheta)*cos(phi+dphi)
			dz=dz0*sin(theta+dtheta)*cos(phi+dphi)
			dy=dy0*sin(phi+dphi)

			#print(dx,dy,dz)
			glVertex3f(x+dx,y+dy,z+dz)

			dx=dx0*cos(theta+dtheta)*cos(phi)
			dz=dz0*sin(theta+dtheta)*cos(phi)
			dy=dy0*sin(phi)

			#print(dx,dy,dz)
			glVertex3f(x+dx,y+dy,z+dz)


			theta=theta+dtheta

			glEnd()

		phi=phi+dphi

def half_cyl(x0,y0,z0,dx,dy0,dz,name="name"):
	r=dx/2
	x=x0+r
	y=y0
	z=z0
	alpha=0.2
	segs=40
	delta=180/segs
	theata=0
	theta_rad=(theata/360)*2*3.141592653

	set_color(1.0,0.0,0.0,name,alpha=alpha)

	#top
	while (theata<180):


		glBegin(GL_QUADS)
		dx=r*cos(theta_rad)
		dy=dy0*sin(theta_rad)

		glVertex3f(x+dx,y+dy,z+0.0)
		glVertex3f(x+dx,y+dy,z+dz)

		theata=theata+delta			
		theta_rad=(theata/360)*2*3.141592653

		dx=r*cos(theta_rad)
		dy=dy0*sin(theta_rad)

		glVertex3f(x+dx,y+dy,z+dz)
		glVertex3f(x+dx,y+dy,z)

		glEnd()

	theata=0
	theta_rad=(theata/360)*2*3.141592653

	set_color(1.0,0.0,0.0,name,alpha=alpha)

	while (theata<180):


		glBegin(GL_TRIANGLES)
		dx=r*cos(theta_rad)
		dy=dy0*sin(theta_rad)

		glVertex3f(x+dx,y+dy,z)

		theata=theata+delta			
		theta_rad=(theata/360)*2*3.141592653

		dx=r*cos(theta_rad)
		dy=dy0*sin(theta_rad)

		glVertex3f(x+dx,y+dy,z)

		glVertex3f(x,y,z)

		glEnd()

	theata=0
	theta_rad=(theata/360)*2*3.141592653

	while (theata<180):


		glBegin(GL_TRIANGLES)
		dx=r*cos(theta_rad)
		dy=dy0*sin(theta_rad)

		glVertex3f(x+dx,y+dy,z+dz)

		theata=theata+delta			
		theta_rad=(theata/360)*2*3.141592653

		dx=r*cos(theta_rad)
		dy=dy0*sin(theta_rad)

		glVertex3f(x+dx,y+dy,z+dz)

		glVertex3f(x,y,z+dz)

		glEnd()


def box(x,y,z,w,h,d,r,g,b,alpha,name="box"):
	gl_save_add("box",x,y,z,[w,h,d,r,g,b,alpha])
	red=r
	green=g
	blue=b


	#btm
	set_color(red,green,blue,name,alpha=alpha)
	glBegin(GL_QUADS)
	glVertex3f(x+0.0,y+0.0,z+0.0)
	glVertex3f(x+w,y+ 0.0,z+0.0)
	glVertex3f(x+w,y+ 0.0,z+d)
	glVertex3f(x+ 0.0, y+0.0,z+ d) 
	glEnd()
	
	#top
	glBegin(GL_QUADS)
	glVertex3f(x+0.0,y+h,z+0.0)
	glVertex3f(x+w,y+ h,z+0.0)
	glVertex3f(x+w,y+ h,z+d)
	glVertex3f(x+ 0.0, y+h,z+ d) 
	glEnd()

	#right

	glBegin(GL_QUADS)
	glVertex3f(x+w,y,z)
	glVertex3f(x+w,y+ h,z)
	glVertex3f(x+w,y+ h,z+d)
	glVertex3f(x+w, y,z+d) 
	glEnd()

	#left

	glBegin(GL_QUADS)
	glVertex3f(x,y,z)
	glVertex3f(x,y+ h,z)
	glVertex3f(x,y+ h,z+d)
	glVertex3f(x, y,z+d) 
	glEnd()
	
	#front
	
	glBegin(GL_QUADS)
	glVertex3f(x,y,z+d)
	glVertex3f(x+w,y,z+d)
	glVertex3f(x+w,y+h,z+d)
	glVertex3f(x, y+h,z+d) 
	glEnd()

	#back

	glBegin(GL_QUADS)
	glVertex3f(x,y,z)
	glVertex3f(x,y+ h,z)
	glVertex3f(x+w,y+ h,z)
	glVertex3f(x+w, y,z) 
	glEnd()

