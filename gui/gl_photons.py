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

## @package gl_photons
#  Shows photons on the device
#

import sys

try:
	from OpenGL.GL import *
	from OpenGL.GLU import *
	from PyQt5 import QtOpenGL
	from PyQt5.QtOpenGL import QGLWidget
	from gl_shapes import pyrmid
	open_gl_ok=True
except:
	print("opengl error from gl_lib",sys.exc_info()[0])

import random
import numpy as np
from math import pi,acos,sin,cos

from gl_scale import scale_get_xmul
from gl_scale import scale_get_ymul
from gl_scale import scale_get_zmul

from gl_base_object import gl_base_object
from triangle import vec

from gl_scale import scale_get_device_y
from gl_scale import scale_get_device_x
from gl_scale import scale_get_device_z

class gl_photons():

	def draw_photons(self,x0,z0):
		if self.false_color==True:
			return

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
					self.draw_photon(x[i],y,z[ii],up_photons,0.0,1.0,0.0)

		if self.emission==True and self.ray_model==False:
			den=1.2
			#x=np.arange(0, max_gui_device_x , den)
			#y=np.arange(0, max_gui_device_z , den)
			x=np.arange(x0, x0+scale_get_device_x() , den)
			z=np.arange(z0, z0+scale_get_device_z() , den)

			for i in range(0,len(x)):
				for ii in range(0,len(z)):
					self.draw_photon(x[i]+0.1,y+0.1,z[ii],True,0.0, 0.0, 1.0)

