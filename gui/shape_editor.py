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
from PyQt5.QtGui import QPainter,QIcon

#python modules
import webbrowser

from help import help_window

from plot_widget import plot_widget
from win_lin import desktop_open

from QWidgetSavePos import QWidgetSavePos

from ribbon_shape import ribbon_shape

from import_data import import_data

from ref import ref_window

from gl import glWidget
from shape_import import shape_import
from dat_file import dat_file

from bibtex import bibtex

from gl_list import gl_base_object
from gl_scale import project_trianges_m2screen
from triangle_io import triangles_get_min
from triangle_io import triangles_sub_vec
from triangle_io import triangles_get_max
from triangle_io import triangles_div_vec
from triangle_io import triangles_flip
from triangle_io import triangles_scale_for_gl
from triangle_io import triangles_print
from triangle import vec


class shape_editor(QWidgetSavePos):

	def changed_click(self):

		if self.notebook.tabText(self.notebook.currentIndex()).strip()==_("Shape"):
			b=bibtex()
			if b.load(os.path.join(self.path,"shape.bib"))!=False:
				text=b.get_text()
				help_window().help_set_help(["shape.png",_("<big><b>Shape file</b></big><br>"+text)])

	def callback_help(self):
		webbrowser.open("https://www.gpvdm.com/docs.html")

	def callback_import_image(self):
		self.shape_import=shape_import(self.path)
		self.shape_import.show()
		self.shape_import.discretizer.changed.connect(self.reload)

	def reload(self):
		self.load_data()
		self.three_d_shape.do_draw()

	def load_data(self):
		data=dat_file()

		if data.load(os.path.join(self.path,"shape.inp"))==True:
			self.three_d_shape.gl_objects_remove_regex("bing")
			a=gl_base_object()
			a.id=["bing"]
			a.type="solid_and_mesh_color"
			a.r=data.r
			a.g=data.g
			a.b=data.b

			a.triangles=triangles_scale_for_gl(data.data)
			if a.triangles!=False:
				self.three_d_shape.gl_objects_add(a)
				self.three_d_shape.scene_built=True

	def __init__(self,path):
		QWidgetSavePos.__init__(self,"spectra_main")
		self.path=path
		self.setMinimumSize(900, 600)
		self.setWindowIcon(icon_get("shape"))

		self.setWindowTitle(os.path.basename(self.path)+" "+_("Shape editor")) 
		

		self.main_vbox = QVBoxLayout()

		self.ribbon=ribbon_shape()
		

		#self.ribbon.import_data.clicked.connect(self.callback_import)
		#self.ribbon.tb_ref.triggered.connect(self.callback_ref)
		self.ribbon.tb_import.triggered.connect(self.callback_import_image)

		self.ribbon.help.triggered.connect(self.callback_help)


		self.main_vbox.addWidget(self.ribbon)

		self.notebook = QTabWidget()

		self.notebook.setMovable(True)

		self.main_vbox.addWidget(self.notebook)


		self.three_d_shape=glWidget(self)
		self.three_d_shape.triangle_file=""

		self.three_d_shape.draw_electrical_mesh=False
		self.three_d_shape.view.draw_device=False
		self.three_d_shape.enable_draw_ray_mesh=True
		self.three_d_shape.enable_draw_light_source=False
		self.three_d_shape.enable_draw_rays=False
		self.three_d_shape.view.render_photons=False

		self.load_data()

		self.notebook.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.ribbon.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		#self.alpha.init(enable_toolbar=False)
		#self.alpha.set_labels([_("Spectra")])
		#self.alpha.load_data([fname])

		#self.alpha.do_plot()
		self.notebook.addTab(self.three_d_shape,_("Shape"))

		self.setLayout(self.main_vbox)
		
		self.notebook.currentChanged.connect(self.changed_click)



