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

from ref import get_ref_text
from QWidgetSavePos import QWidgetSavePos

from ribbon_shape import ribbon_shape

from import_data import import_data

from ref import ref_window
from ref import get_ref_text
from ref_io import ref

from gl import glWidget
from shape_import import shape_import

articles = []
mesh_articles = []

class shape_editor(QWidgetSavePos):

	def changed_click(self):

		if self.notebook.tabText(self.notebook.currentIndex()).strip()==_("Refractive index"):
			text=get_ref_text(os.path.join(self.path,"n.ref"))
			if text==None:
				text=""
			help_window().help_set_help(["n.png",_("<big><b>Refractive index</b></big><br>"+text)])

	def callback_help(self):
		webbrowser.open("https://www.gpvdm.com/docs.html")

	def callback_import_image(self):
		self.shape_import=shape_import(self.path)
		self.shape_import.show()

	def __init__(self,path):
		QWidgetSavePos.__init__(self,"spectra_main")
		self.path=path
		self.setMinimumSize(900, 600)
		self.setWindowIcon(icon_get("shape"))

		self.setWindowTitle(_("Shape editor")+" (https://www.gpvdm.com)"+" "+os.path.basename(self.path)) 
		

		self.main_vbox = QVBoxLayout()

		self.ribbon=ribbon_shape()
		

		#self.ribbon.import_data.secure_click.connect(self.callback_import)
		#self.ribbon.tb_ref.triggered.connect(self.callback_ref)
		self.ribbon.tb_import.triggered.connect(self.callback_import_image)

		self.ribbon.help.triggered.connect(self.callback_help)


		self.main_vbox.addWidget(self.ribbon)

		self.notebook = QTabWidget()

		self.notebook.setMovable(True)

		self.main_vbox.addWidget(self.notebook)


		self.three_d_shape=glWidget(self)
		self.three_d_shape.bing=False
		self.three_d_shape.draw_electrical_mesh=False
		self.three_d_shape.enable_draw_device=False
		self.three_d_shape.draw_ray_mesh=True
		self.three_d_shape.enable_draw_light_source=False
		self.three_d_shape.enable_draw_rays=False
		self.notebook.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.ribbon.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		#self.alpha.init(enable_toolbar=False)
		#self.alpha.set_labels([_("Spectra")])
		#self.alpha.load_data([fname])

		#self.alpha.do_plot()
		self.notebook.addTab(self.three_d_shape,_("Shape"))

		self.setLayout(self.main_vbox)
		
		self.notebook.currentChanged.connect(self.changed_click)



