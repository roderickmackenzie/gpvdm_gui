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

class tri():
	def __init__(self):
		self.x0=0.0
		self.y0=0.0
		self.z0=0.0


		self.x1=0.0
		self.y1=0.0
		self.z1=0.0

		self.x2=0.0
		self.y2=0.0
		self.z2=0.0

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

	def m2px_y(self,y):
		ret=self.im.height()*(y/self.len_y)

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
		d.y_label="Position"
		d.data_label="Position"
		d.x_units="m"
		d.y_units="m"
		d.data_units="m"

		d.data=[]

		for t in self.triangles:
			d.data.append([[t.x0,t.y0,t.z0],[t.x1,t.y1,t.z1],[t.x2,t.y2,t.z2]])

		d.save(os.path.join(self.path,"shape.inp"))

	def build_mesh(self):
		if os.path.isfile(self.image_path)==False:
			return

		pixmap = QPixmap(self.image_path)

		self.im=pixmap.toImage()
		print(os.path.join(self.path,"shape_import.inp"))
		x_segs=int(inp_get_token_value(os.path.join(self.path,"shape_import.inp"),"#x_trianges"))
		y_segs=int(inp_get_token_value(os.path.join(self.path,"shape_import.inp"),"#y_trianges"))
		dx=self.len_x/x_segs
		dy=self.len_y/y_segs

		x=0
		self.triangles=[]

		while(x<self.len_x):
			y=0
			while(y<self.len_y):
				t=tri()

				c = self.im.pixel(self.m2px_x(x),self.m2px_y(y))
				colors = QColor(c).getRgbF()

				t.x0=x
				t.y0=y
				t.z0=self.len_z*(colors[0]+colors[1]+colors[2])/3.0
				

				c = self.im.pixel(self.m2px_x(x),self.m2px_y(y+dy))
				colors = QColor(c).getRgbF()

				t.x1=x
				t.y1=y+dy
				t.z1=self.len_z*(colors[0]+colors[1]+colors[2])/3.0

				c = self.im.pixel(self.m2px_x(x+dx),self.m2px_y(y+dy))
				colors = QColor(c).getRgbF()

				t.x2=x+dx
				t.y2=y+dy
				t.z2=self.len_z*(colors[0]+colors[1]+colors[2])/3.0

				self.triangles.append(t)

				y=y+dy
			x=x+dx

	def paintEvent(self, event):
		painter = QPainter(self)

		if os.path.isfile(self.image_path)==False:
			return

		pixmap = QPixmap(self.image_path)
		self.im=pixmap.toImage()
		x_mul=self.width()/pixmap.width()
		y_mul=self.height()/pixmap.height()

		painter.drawPixmap(self.rect(), pixmap)
		pen = QPen(Qt.red, 3)
		painter.setPen(pen)
		x_segs=40
		y_segs=40
		dx=self.len_x/x_segs
		dy=self.len_y/y_segs

		x=0

		for b in self.triangles:
			painter.drawLine(self.m2px_x(b.x0)*x_mul, self.m2px_y(b.y0)*y_mul, self.m2px_x(b.x1)*x_mul, self.m2px_y(b.y1)*y_mul)
			painter.drawLine(self.m2px_x(b.x1)*x_mul, self.m2px_y(b.y1)*y_mul, self.m2px_x(b.x2)*x_mul, self.m2px_y(b.y2)*y_mul)
			painter.drawLine(self.m2px_x(b.x2)*x_mul, self.m2px_y(b.y2)*y_mul, self.m2px_x(b.x0)*x_mul, self.m2px_y(b.y0)*y_mul)


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

