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
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget, QDialog, QMenu
from PyQt5.QtGui import QPainter,QIcon,QPixmap,QPen,QColor

#python modules
import webbrowser

from help import help_window

from plot_widget import plot_widget
from win_lin import desktop_open

from QWidgetSavePos import QWidgetSavePos

from ribbon_shape_import import ribbon_shape_import

from import_data import import_data

from open_save_dlg import open_as_filter

from shutil import copyfile
from dat_file import dat_file

from triangle import triangle
from triangle_io import triangles_get_min
from triangle_io import triangles_get_max

from PyQt5.QtCore import pyqtSignal
from PIL import Image, ImageFilter,ImageOps 
from PIL.ImageQt import ImageQt
from inp import inp
from inp_dialog import inp_dialog
from str2bool import str2bool

from PyQt5.QtWidgets import QApplication
import time

class image_discretizer(QWidget):
	changed = pyqtSignal()

	def __init__(self,path):
		super().__init__()
		self.path=path
		self.image_path=os.path.join(self.path,"image.png")
		self.setGeometry(30, 30, 500, 300)
		self.len_x=800e-9
		self.len_y=800e-9
		self.len_z=800e-9
		self.im=None

		self.triangles=[]
		self.show_mesh=True
		self.gaussian_blur=0
		self.blur_enable=False
		self.y_norm=False
		self.x_norm=False
		self.z_norm=False

		self.load_image()
		self.build_mesh()

	def m2px_x(self,x):
		width, height = self.im.size
		ret=width*(x/self.len_x)
		if ret>=width:
			return width-1
		return int(ret)

	def m2px_z(self,z):
		width, height = self.im.size

		ret=height*(z/self.len_z)

		if ret>=height:
			return height-1

		return int(ret)

	def force_update(self):
		self.load_image()
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
		d.r=1.0
		d.g=0.0
		d.b=0.0

		d.x_len=3
		d.y_len=len(self.triangles)

		d.data=[]

		for t in self.triangles:
			d.data.append(t)

		d.save(os.path.join(self.path,"shape.inp"))

		self.changed.emit()

	def get_color(self,x,z):
		colors = self.im.getpixel((self.m2px_x(x),self.m2px_z(z)))
		c=(colors[0]+colors[1]+colors[2])/3.0
		if c<self.y_min:
			self.y_min=c

		if c>self.y_max:
			self.y_max=c

		return c

	def load_image(self):
		if os.path.isfile(self.image_path)==False:
			self.im=None
			return

		img=Image.open(self.image_path)

		f=inp()
		f.load(os.path.join(self.path,"shape_import.inp"))
		self.x_segs=int(f.get_token("#x_triangles"))
		self.z_segs=int(f.get_token("#y_triangles"))
		self.gaussian_blur=int(f.get_token("#shape_import_blur"))
		self.y_norm=str2bool(f.get_token("#shape_import_y_norm"))
		self.z_norm=str2bool(f.get_token("#shape_import_z_norm"))
		self.blur_enable=str2bool(f.get_token("#shape_import_blur_enabled"))
		self.y_norm_percent=int(f.get_token("#shape_import_y_norm_percent"))

		if self.blur_enable==True:
			img = img.filter(ImageFilter.GaussianBlur(radius = self.gaussian_blur))

		if self.z_norm==True:
			img2 = img.resize((1, 1))
			color = img2.getpixel((0, 0))
			avg_pixel=(color[0]+color[1]+color[2])/3
			width, height = img.size
			for z in range(0,height):
				x_avg=0
				for x in range(0,width):
					color=img.getpixel((x, z))
					c=(color[0]+color[1]+color[2])/3
					x_avg=x_avg+c
				x_avg=x_avg/width
				delta=avg_pixel-x_avg
				for x in range(0,width):
					color=img.getpixel((x, z))
					c=(color[0]+color[1]+color[2])/3
					img.putpixel((x,z),(int(c+delta),int(c+delta),int(c+delta)))

				#print(x_avg)

			#print("avg color>>",c)

		if self.y_norm==True:
			img=ImageOps.autocontrast(img, cutoff=self.y_norm_percent, ignore=None)


		self.im = img.convert('RGB')


	def build_mesh(self):
		if self.im==None:
			return

		self.y_min=255
		self.y_max=0

		dx=self.len_x/self.x_segs
		dz=self.len_z/self.z_segs

		#add top
		x=0
		z=0
		self.triangles=[]
		ix=0
		iz=0
		for ix in range(0,self.x_segs):
			z=0
			for iz in range(0,self.z_segs):
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
				self.triangles.append(t0)

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
				self.triangles.append(t1)

				if iz==self.z_segs-1 or iz==0:
					zadd=0.0
					if iz==self.z_segs-1:
						zadd=dz

					td0=triangle()

					td0.xyz0.x=x
					td0.xyz0.y=self.len_y*self.get_color(x,z+zadd)
					td0.xyz0.z=z+zadd
					
					td0.xyz1.x=x+dx
					td0.xyz1.y=self.len_y*self.get_color(x+dx,z+zadd)
					td0.xyz1.z=z+zadd

					td0.xyz2.x=x
					td0.xyz2.y=0.0
					td0.xyz2.z=z+zadd
					self.triangles.append(td0)


					td0=triangle()

					td0.xyz0.x=x+dx
					td0.xyz0.y=self.len_y*self.get_color(x+dx,z+zadd)
					td0.xyz0.z=z+zadd
					
					td0.xyz1.x=x
					td0.xyz1.y=0.0
					td0.xyz1.z=z+zadd

					td0.xyz2.x=x+dx
					td0.xyz2.y=0.0
					td0.xyz2.z=z+zadd
					self.triangles.append(td0)

				if ix==0 or ix==self.x_segs-1:
					xadd=0.0
					if ix==self.x_segs-1:
						xadd=dx

					td0=triangle()

					td0.xyz0.x=x+xadd
					td0.xyz0.y=self.len_y*self.get_color(x+xadd,z)
					td0.xyz0.z=z
					
					td0.xyz1.x=x+xadd
					td0.xyz1.y=self.len_y*self.get_color(x+xadd,z+dz)
					td0.xyz1.z=z+dz

					td0.xyz2.x=x+xadd
					td0.xyz2.y=0.0
					td0.xyz2.z=z
					self.triangles.append(td0)

					td1=triangle()

					td1.xyz0.x=x+xadd
					td1.xyz0.y=self.len_y*self.get_color(x+xadd,z+dz)
					td1.xyz0.z=z+dz
					
					td1.xyz1.x=x+xadd
					td1.xyz1.y=0
					td1.xyz1.z=z

					td1.xyz2.x=x+xadd
					td1.xyz2.y=0.0
					td1.xyz2.z=z+dz
					self.triangles.append(td1)


				z=z+dz
			x=x+dx


		self.add_base()
		#self.zero_edges()		#will force edges to zero
		#self.squaer_sides()
		#add base


	def add_base(self):
		min=triangles_get_min(self.triangles)
		max=triangles_get_max(self.triangles)
		a=triangle()
		a.xyz0.x=min.x
		a.xyz0.y=0
		a.xyz0.z=min.z

		a.xyz1.x=min.x
		a.xyz1.y=0
		a.xyz1.z=max.z

		a.xyz2.x=max.x
		a.xyz2.y=0
		a.xyz2.z=max.z
		self.triangles.append(a)

		a=triangle()
		a.xyz0.x=min.x
		a.xyz0.y=0
		a.xyz0.z=min.z

		a.xyz1.x=max.x
		a.xyz1.y=0
		a.xyz1.z=min.z

		a.xyz2.x=max.x
		a.xyz2.y=0
		a.xyz2.z=max.z
		self.triangles.append(a)

		


	def zero_edges(self):
		#sides
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

		if self.im==None:
			return

		qim = ImageQt(self.im)
		pixmap = QPixmap.fromImage(qim)
		#pixmap = QPixmap(self.image_path)
		#self.im=pixmap.toImage()
		x_mul=self.width()/pixmap.width()
		z_mul=self.height()/pixmap.height()

		painter.drawPixmap(self.rect(), pixmap)
		pen = QPen(Qt.red, 3)
		painter.setPen(pen)

		if self.show_mesh==True:
			for b in self.triangles:
				painter.drawLine(self.m2px_x(b.xyz0.x)*x_mul, self.m2px_z(b.xyz0.z)*z_mul, self.m2px_x(b.xyz1.x)*x_mul, self.m2px_z(b.xyz1.z)*z_mul)
				painter.drawLine(self.m2px_x(b.xyz1.x)*x_mul, self.m2px_z(b.xyz1.z)*z_mul, self.m2px_x(b.xyz2.x)*x_mul, self.m2px_z(b.xyz2.z)*z_mul)
				painter.drawLine(self.m2px_x(b.xyz2.x)*x_mul, self.m2px_z(b.xyz2.z)*z_mul, self.m2px_x(b.xyz0.x)*x_mul, self.m2px_z(b.xyz0.z)*z_mul)

	def callback_copy(self,event):
		self.menu.close()
		time.sleep(0.1)
		QApplication.processEvents()
		screen = QApplication.primaryScreen()
		QApplication.clipboard().setImage(screen.grabWindow(self.winId()).toImage())



	def contextMenuEvent(self, event):
		self.menu = QMenu(self)

		export=self.menu.addMenu(_("Export"))

		action=export.addAction(_("Copy"))
		action.triggered.connect(self.callback_copy)
		self.menu.exec_(event.globalPos())


