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

## @package gl_view_point
#  The gl_view_point class for the OpenGL display.
#

import sys
from math import fabs

try:
	from OpenGL.GL import *
	from OpenGL.GLU import *
	from PyQt5 import QtOpenGL
	from PyQt5.QtOpenGL import QGLWidget
	from gl_color import set_color
	from gl_lib import val_to_rgb
	from PyQt5.QtGui import QFont


except:
	pass

from PyQt5.QtCore import QTimer

from gl_scale import scale_get_start_x
from gl_scale import scale_get_start_z

class gl_cords():
	def draw_cords(self):

		font = QFont("Arial")
		font.setPointSize(18)

		width=0.04
		leng=1.0
		start_x=scale_get_start_x()-2.0
		start_z=scale_get_start_z()-2.0
		quad=gluNewQuadric()



		glPushMatrix()
		set_color(0.7,0.7,0.7,"cordinates",alpha=1.0)
		glTranslatef(start_x,0.0,start_z)

		quad=gluNewQuadric()
		glRotatef(90, 0.0, 1.0, 0.0)
		gluCylinder(quad, width, width, leng, 10, 1)
		glTranslatef(0.0,0.0,leng)
		gluCylinder(quad, 0.1, 0.00, 0.2, 10, 1)
		set_color(1.0,1.0,1.0,"cordinates",alpha=1.0)
		if self.view.zoom<20:
			self.render_text (0.2,0.0,0.0, "x",font)
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
		if self.view.zoom<20:
			self.render_text (0.2,0.0,0.0, "y",font)
		glPopMatrix()

		glPushMatrix()
		set_color(0.7,0.7,0.7,"cordinates",alpha=1.0)
		glTranslatef(start_x,0.0,start_z)

		quad=gluNewQuadric()
		glRotatef(0, 0.0, 1.0, 0.0)
		gluCylinder(quad, width, width, leng, 10, 1)
		glTranslatef(0.0,0.0,leng)
		gluCylinder(quad, 0.1, 0.00, 0.2, 10, 1)

		gluSphere(quad,0.08,32,32)
		set_color(1.0,1.0,1.0,"cordinates",alpha=1.0)
		if self.view.zoom<20:
			self.render_text (-0.2,0.0,0.0, "z",font)
		glPopMatrix()
		self.draw_numbers()

	def draw_numbers(self):

		font = QFont("Arial")
		font.setPointSize(18)


		self.render_text (0.0,0.0,0.0, "(0,0,0)",font)
		self.render_text (1.0,0.0,0.0, "(1,0,0)",font)
		self.render_text (0.0,2.0,0.0, "(0,1,0)",font)
		self.render_text (0.0,0.0,1.0, "(0,0,1)",font)


