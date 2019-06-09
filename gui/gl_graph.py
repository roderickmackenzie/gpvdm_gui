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

import os
import sys
from math import fabs
from cal_path import get_sim_path

from dat_file import dat_file

try:
	from OpenGL.GL import *
	from OpenGL.GLU import *
	from PyQt5 import QtOpenGL
	from PyQt5.QtOpenGL import QGLWidget
	from gl_color import set_color
	from gl_lib import val_to_rgb

except:
	pass

def draw_mode(x,y,z,z_size):
	glLineWidth(5)
	set_color(1.0, 1.0, 1.0,"mode")
	glBegin(GL_LINES)
	t=[]
	s=[]

	data=dat_file()
			
	path=os.path.join(get_sim_path(),"optical_output","light_1d_photons_tot_norm.dat")
	if data.load(path)==True:
		array_len=data.y_len
		s=data.data[0][0]
		s.reverse()
		#print(path)
		#print(data.data)
		for i in range(1,array_len):
			glVertex3f(x, y+(z_size*(i-1)/array_len), z-s[i-1]*0.5)
			glVertex3f(x, y+(z_size*i/array_len), z-s[i]*0.5)

	glEnd()


def graph(xstart,ystart,z,w,h,z_range,graph_data):
	xpoints=graph_data.x_len
	ypoints=graph_data.y_len
	
	if xpoints>0 and ypoints>0:
		
		dx=w/xpoints
		dy=h/ypoints

		glBegin(GL_QUADS)


		if z_range==0.0:
			z_range=1.0

		for x in range(0,xpoints):
			for y in range(0,ypoints):
				r,g,b=val_to_rgb(graph_data.data[0][x][y]/z_range)
				glColor4f(r,g,b, 0.7)
				glVertex3f(xstart+dx*x,ystart+y*dy, z)
				glVertex3f(xstart+dx*(x+1),ystart+y*dy, z)
				glVertex3f(xstart+dx*(x+1),ystart+dy*(y+1), z)
				glVertex3f(xstart+dx*x, ystart+dy*(y+1), z) 


		glEnd()
	
