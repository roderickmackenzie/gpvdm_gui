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

## @package shape_editor
#  The shape editor
#

import os
from tab import tab_class
from icon_lib import icon_get

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget
from PyQt5.QtGui import QPainter,QIcon,QPixmap,QPen,QColor

#python modules
import webbrowser

from help import help_window

from plot_widget import plot_widget
from win_lin import desktop_open

from ref import get_ref_text
from QWidgetSavePos import QWidgetSavePos

from ribbon_shape_import import ribbon_shape_import

from import_data import import_data

from ref import ref_window
from ref import get_ref_text
from ref_io import ref

from inp import inp_get_token_value
from triangle_xy_editor import triangle_xy_editor
from open_save_dlg import open_as_filter

from shutil import copyfile
from dat_file import dat_file

from triangle import triangle
from triangle_io import triangles_get_min
from triangle_io import triangles_get_max

class image_widget(QWidget):
	def __init__(self,path):
		super().__init__()
		self.path=path
		self.image_path=os.path.join(self.path,"image.png")
		self.setGeometry(30, 30, 500, 300)
		self.len_x=800e-9
		self.len_y=800e-9
		self.len_z=800e-9

		self.triangles=[]
		self.build_mesh()

	def m2px_x(self,x):
		ret=self.im.width()*(x/self.len_x)
		if ret>=self.im.width():
			return self.im.width()-1
		return int(ret)

	def m2px_z(self,z):
		ret=self.im.height()*(z/self.len_z)

		if ret>=self.im.height():
			return self.im.height()-1

		return int(ret)

	def force_update(self):
		self.build_mesh()
		self.repaint()

	def save_mesh(self):
		d=dat_file()
		d.title="title Ray trace triange file"
		d.type="poly"
		d.x_label="Position"
		d.z_label="Position"
		d.data_label="Position"
		d.x_units="m"
		d.z_units="m"
		d.data_units="m"

		d.x_len=3
		d.y_len=len(self.triangles)
		d.z_len=0

		d.data=[]

		for t in self.triangles:
			d.data.append(t)

		d.save(os.path.join(self.path,"shape.inp"))

	def get_color(self,x,z):
		c = self.im.pixel(self.m2px_x(x),self.m2px_z(z))
		colors = QColor(c).getRgbF()
		return (colors[0]+colors[1]+colors[2])/3.0

	def build_mesh(self):
		if os.path.isfile(self.image_path)==False:
			return

		pixmap = QPixmap(self.image_path)

		self.im=pixmap.toImage()
		print(os.path.join(self.path,"shape_import.inp"))
		x_segs=int(inp_get_token_value(os.path.join(self.path,"shape_import.inp"),"#x_trianges"))
		z_segs=int(inp_get_token_value(os.path.join(self.path,"shape_import.inp"),"#y_trianges"))
		dx=self.len_x/x_segs
		dz=self.len_z/z_segs

		x=0
		z=0
		self.triangles=[]
		ix=0
		iz=0
		for ix in range(0,x_segs):
			z=0
			for iz in range(0,z_segs):
				t0=triangle()

				t0.xyz0.x=x
				t0.xyz0.y=self.len_y*self.get_color(x,z)
				t0.xyz0.z=z
				
				t0.xyz1.x=x
				t0.xyz1.y=self.len_y*self.get_color(x,z+dz)
				t0.xyz1.z=z+dz

				t0.xyz2.x=x+dx
				t0.xyz2.y=self.len_y*self.get_color(x+dx,z)
				t0.xyz2.z=z

				t1=triangle()

				t1.xyz0.x=x
				t1.xyz0.y=self.len_y*self.get_color(x,z+dz)
				t1.xyz0.z=z+dz

				t1.xyz1.x=x+dx
				t1.xyz1.y=self.len_y*self.get_color(x+dx,z+dz)
				t1.xyz1.z=z+dz

				t1.xyz2.x=x+dx
				t1.xyz2.y=self.len_y*self.get_color(x+dx,z)
				t1.xyz2.z=z



				self.triangles.append(t0)
				self.triangles.append(t1)

				z=z+dz
			x=x+dx

		min=triangles_get_min(self.triangles)
		max=triangles_get_max(self.triangles)

		for t in self.triangles:
			if t.xyz0.x==min.x:
				t.xyz0.y=0

			if t.xyz1.x==min.x:
				t.xyz1.y=0

			if t.xyz2.x==min.x:
				t.xyz2.y=0

			if t.xyz0.x==max.x:
				t.xyz0.y=0

			if t.xyz1.x==max.x:
				t.xyz1.y=0

			if t.xyz2.x==max.x:
				t.xyz2.y=0

			if t.xyz0.z==min.z:
				t.xyz0.y=0

			if t.xyz1.z==min.z:
				t.xyz1.y=0

			if t.xyz2.z==min.z:
				t.xyz2.y=0

			if t.xyz0.z==max.z:
				t.xyz0.y=0

			if t.xyz1.z==max.z:
				t.xyz1.y=0

			if t.xyz2.z==max.z:
				t.xyz2.y=0

	def paintEvent(self, event):
		painter = QPainter(self)

		if os.path.isfile(self.image_path)==False:
			return

		pixmap = QPixmap(self.image_path)
		self.im=pixmap.toImage()
		x_mul=self.width()/pixmap.width()
		z_mul=self.height()/pixmap.height()

		painter.drawPixmap(self.rect(), pixmap)
		pen = QPen(Qt.red, 3)
		painter.setPen(pen)

		for b in self.triangles:
			painter.drawLine(self.m2px_x(b.xyz0.x)*x_mul, self.m2px_z(b.xyz0.z)*z_mul, self.m2px_x(b.xyz1.x)*x_mul, self.m2px_z(b.xyz1.z)*z_mul)
			painter.drawLine(self.m2px_x(b.xyz1.x)*x_mul, self.m2px_z(b.xyz1.z)*z_mul, self.m2px_x(b.xyz2.x)*x_mul, self.m2px_z(b.xyz2.z)*z_mul)
			painter.drawLine(self.m2px_x(b.xyz2.x)*x_mul, self.m2px_z(b.xyz2.z)*z_mul, self.m2px_x(b.xyz0.x)*x_mul, self.m2px_z(b.xyz0.z)*z_mul)


class shape_import(QWidgetSavePos):

	def callback_help(self):
		webbrowser.open("https://www.gpvdm.com/docs.html")

	def update(self):
		self.alpha.update()

	def callback_xy_triangles(self):
		self.xy_triangles=triangle_xy_editor(self.path)
		self.xy_triangles.show()
		self.xy_triangles.changed.connect(self.image_widget.force_update)

	def callback_open_image(self):
		file_name=open_as_filter(self,"png (*.png)",path=self.path)
		copyfile(file_name, os.path.join(self.path,"image.png"))
		self.image_widget.self.build_mesh()

	def __init__(self,path):
		QWidgetSavePos.__init__(self,"shape_import")
		self.path=path
		self.setMinimumSize(900, 600)
		self.setWindowIcon(icon_get("shape"))

		self.setWindowTitle(_("Import microscope image")+" (https://www.gpvdm.com)") 
		



		self.main_vbox = QVBoxLayout()

		self.ribbon=ribbon_shape_import()

		self.ribbon.xy_triangles.triggered.connect(self.callback_xy_triangles)
		self.ribbon.import_image.triggered.connect(self.callback_open_image)
		self.ribbon.save_data.triggered.connect(self.callback_import)


		#self.ribbon.help.triggered.connect(self.callback_help)

		self.main_vbox.addWidget(self.ribbon)

		self.notebook = QTabWidget()

		self.notebook.setMovable(True)

		self.main_vbox.addWidget(self.notebook)

		self.notebook.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.ribbon.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)


		#self.alpha.init(enable_toolbar=False)
		#self.alpha.set_labels([_("Spectra")])
		#self.alpha.load_data([fname])

		#self.alpha.do_plot()
		self.image_widget=image_widget(self.path)
		self.notebook.addTab(self.image_widget,_("Image"))

		self.setLayout(self.main_vbox)
		
		#self.notebook.currentChanged.connect(self.changed_click)

	def callback_import(self):
		self.image_widget.save_mesh()

