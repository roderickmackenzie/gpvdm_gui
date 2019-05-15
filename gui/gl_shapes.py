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

def pyrmid(x,y,z,height,width,name="name"):
	alpha=0.2
	segs=40
	delta=180/segs
	theata=0
	theta_rad=(theata/360)*2*3.141592653
	dz=0.5
	dx=width
	dy=height
	set_color(1.0,0.0,0.0,name,alpha=alpha)

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

def dome(x,y,z,height,width,name="name"):
	alpha=0.2
	segs=40
	delta=180/segs
	theata=0
	theta_rad=0
	dz=0.5
	r=width/2.0
	set_color(1.0,0.0,0.0,name,alpha=alpha)

	x=x+width/2
	y=y
	z=z+width/2

	#top
	phi=0.0
	phi_rad=0.0
	dphi=40
	dphi_rad=(dphi/360)*2*3.141592653
	dtheta=40
	dtheta_rad=(dtheta/360)*2*3.141592653
	while(phi<90):
		theata=0
		theta_rad=0
		while (theata<360):

			glBegin(GL_QUADS)

			dx=r*cos(theta_rad)*cos(phi_rad)
			dz=r*sin(theta_rad)*cos(phi_rad)
			dy=r*sin(phi_rad)

			#print(dx,dy,dz)
			glVertex3f(x+dx,y+dy,z+dz)

			dx=r*cos(theta_rad)*cos(phi_rad+dphi_rad)
			dz=r*sin(theta_rad)*cos(phi_rad+dphi_rad)
			dy=r*sin(phi_rad+dphi_rad)

			#print(dx,dy,dz)
			glVertex3f(x+dx,y+dy,z+dz)

			dx=r*cos(theta_rad+dtheta_rad)*cos(phi_rad+dphi_rad)
			dz=r*sin(theta_rad+dtheta_rad)*cos(phi_rad+dphi_rad)
			dy=r*sin(phi_rad+dphi_rad)

			#print(dx,dy,dz)
			glVertex3f(x+dx,y+dy,z+dz)

			dx=r*cos(theta_rad+dtheta_rad)*cos(phi_rad)
			dz=r*sin(theta_rad+dtheta_rad)*cos(phi_rad)
			dy=r*sin(phi_rad)

			#print(dx,dy,dz)
			glVertex3f(x+dx,y+dy,z+dz)


			theata=theata+dtheta			
			theta_rad=(theata/360)*2*3.141592653

			glEnd()
		phi=phi+dphi
		phi_rad=(phi/360)*2*3.141592653
		#print(phi)

		#break
