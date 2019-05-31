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
	from PyQt5.QtWidgets import QMenu
	from gl_scale import scale_get_xmul
	from gl_scale import scale_get_ymul
	from gl_scale import scale_get_zmul
	from gl_scale import scale_get_start_x
	from gl_scale import scale_get_start_z

except:
	pass

from PyQt5.QtCore import QTimer
from inp import inp_update_token_value


class gl_mesh():
	def draw_mesh(self):


		set_color(1.0,0.0,0.0,"mesh",alpha=0.5)

		x=[]
		y=[]
		z=[]

		for z0 in self.z_mesh.points:
			z.append(scale_get_start_z()+z0*scale_get_zmul())

		for x0 in self.x_mesh.points:
			x.append(scale_get_start_x()+x0*scale_get_xmul())

		for y0 in self.y_mesh.points:
			y.append(y0*scale_get_ymul()*3)

		
		glLineWidth(3)
		#print(x_mesh.points)
		for zi in range(0,len(z)):
			for xi in range(0,len(x)):
				for yi in range(0,len(y)):

					#box(dx*x,self.pos+y*(dy),z*dz,dx*xshrink,dy*0.8,dz*zshrink,1.0,0.0,0.0,1.0)

					name="mesh:"+str(xi)+":"+str(yi)+":"+str(zi)
					if yi==self.dump_energy_slice_ypos and xi==self.dump_energy_slice_xpos and zi==self.dump_energy_slice_zpos:
						glPushMatrix()
						quad=gluNewQuadric()
						glTranslatef(x[xi],y[yi],z[zi])
						set_color(0.0,1.0,0.0,name,alpha=0.9)
						gluSphere(quad,0.08,32,32)
						glPopMatrix()
					elif xi==self.dump_1d_slice_xpos and zi==self.dump_1d_slice_zpos:
						glPushMatrix()
						quad=gluNewQuadric()
						glTranslatef(x[xi],y[yi],z[zi])
						set_color(0.0,0.0,1.0,name,alpha=0.9)
						gluSphere(quad,0.05,32,32)
						glPopMatrix()
					else:
						glPushMatrix()
						quad=gluNewQuadric()
						glTranslatef(x[xi],y[yi],z[zi])
						if self.dump_verbose_electrical_solver_results==False:
							set_color(1.0,0.0,0.0,name,alpha=0.5)
						else:
							set_color(1.0,0.0,0.0,name,alpha=0.9)

						gluSphere(quad,0.05,32,32)
						glPopMatrix()

					if yi!=0:
						set_color(1.0,0.0,0.0,"line",alpha=0.5)
						glBegin(GL_LINES)
						glVertex3f(x[xi], y[yi-1], z[zi])
						glVertex3f(x[xi], y[yi], z[zi])
						glEnd()


					if xi!=0:
						set_color(1.0,0.0,0.0,"line",alpha=0.5)
						glBegin(GL_LINES)
						glVertex3f(x[xi-1], y[yi], z[zi])
						glVertex3f(x[xi], y[yi], z[zi])
						glEnd()

					if zi!=0:
						set_color(1.0,0.0,0.0,"line",alpha=0.5)
						glBegin(GL_LINES)
						glVertex3f(x[xi], y[yi], z[zi-1])
						glVertex3f(x[xi], y[yi], z[zi])
						glEnd()

						#glTranslatef(0.0,0.0,0.0);

	
	def mesh_menu(self,event):
		view_menu = QMenu(self)
		

		menu = QMenu(self)

		view=menu.addMenu(_("Dump"))

		action=view.addAction(_("Set/Unset energy slice dump"))
		action.triggered.connect(self.menu_energy_slice_dump)

		action=view.addAction(_("Set/Unset dumping 1D slice"))
		action.triggered.connect(self.menu_1d_slice_dump)

		action=view.addAction(_("Set/Unset verbose electrical solver dumping"))
		action.triggered.connect(self.menu_dump_verbose_electrical_solver_results)



		menu.exec_(event.globalPos())

	def menu_energy_slice_dump(self):
		s=self.obj.split(":")
		x=int(s[1])
		y=int(s[2])
		z=int(s[3])

		if self.dump_energy_slice_xpos==x and self.dump_energy_slice_ypos==y and self.dump_energy_slice_zpos==z:
			self.dump_energy_slice_xpos=-1
			self.dump_energy_slice_ypos=-1
			self.dump_energy_slice_zpos=-1
		else:
			self.dump_energy_slice_xpos=x
			self.dump_energy_slice_ypos=y
			self.dump_energy_slice_zpos=z

		inp_update_token_value("dump.inp","#dump_energy_slice_xpos",str(x))
		inp_update_token_value("dump.inp","#dump_energy_slice_ypos",str(len(self.y_mesh.points)-1-y))
		inp_update_token_value("dump.inp","#dump_energy_slice_zpos",str(z))

		self.do_draw()

	def menu_1d_slice_dump(self):
		s=self.obj.split(":")
		x=int(s[1])
		y=int(s[2])
		z=int(s[3])

		if self.dump_1d_slice_xpos==x and self.dump_1d_slice_zpos==z:
			self.dump_1d_slice_xpos=-1
			self.dump_1d_slice_zpos=-1
		else:
			self.dump_1d_slice_xpos=x
			self.dump_1d_slice_zpos=z

		inp_update_token_value("dump.inp","#dump_1d_slice_xpos",str(self.dump_1d_slice_xpos))
		inp_update_token_value("dump.inp","#dump_1d_slice_zpos",str(self.dump_1d_slice_zpos))

		self.do_draw()

	def menu_dump_verbose_electrical_solver_results(self):
		self.dump_verbose_electrical_solver_results = not self.dump_verbose_electrical_solver_results 
		inp_update_token_value("dump.inp","#dump_verbose_electrical_solver_results",str(self.dump_verbose_electrical_solver_results))
		self.do_draw()
