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

## @package shape_import
#  Import shapes into the database
#

import os
from tab import tab_class
from icon_lib import icon_get

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget, QDialog
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

from image_discretizer import image_discretizer
from scripts import scripts

class shape_import(QWidgetSavePos):

	def callback_help(self):
		webbrowser.open("https://www.gpvdm.com/docs.html")

	def update(self):
		self.alpha.update()

	def callback_norm_y(self):
		f=inp()
		f.load(os.path.join(self.path,"shape_import.inp"))
		f.replace("#shape_import_y_norm",str(self.ribbon.tb_norm_y.isChecked()))
		f.save()
		self.discretizer.force_update()

	def callback_norm_z(self):
		f=inp()
		f.load(os.path.join(self.path,"shape_import.inp"))
		f.replace("#shape_import_z_norm",str(self.ribbon.tb_norm_z.isChecked()))
		f.save()
		self.discretizer.force_update()

	def callback_blur_enable(self):
		f=inp()
		f.load(os.path.join(self.path,"shape_import.inp"))
		f.replace("#shape_import_blur_enabled",str(self.ribbon.tb_blur.isChecked()))
		f.save()
		self.discretizer.force_update()

	def callback_menu_blur(self):
		f=inp()
		f.load(os.path.join(self.path,"shape_import.inp"))
		blur=f.get_token("#shape_import_blur")

		self.a=inp_dialog(title=_("Gaussian blur editor"),icon="blur")
		ret=self.a.run(["#shape_import_blur",blur,"#end"])
		if ret==QDialog.Accepted:
			f.replace("#shape_import_blur",self.a.tab.f.get_token("#shape_import_blur"))

			f.save()
			self.discretizer.force_update()

	def callback_mesh_editor(self):
		f=inp()
		f.load(os.path.join(self.path,"shape_import.inp"))
		x_triangles=f.get_token("#x_triangles")
		y_triangles=f.get_token("#y_triangles")

		self.a=inp_dialog(title=_("Triangle editor"),icon="shape")
		ret=self.a.run(["#x_triangles",x_triangles,"#y_triangles",y_triangles,"#end"])
		if ret==QDialog.Accepted:
			f.replace("#x_triangles",self.a.tab.f.get_token("#x_triangles"))
			f.replace("#y_triangles",self.a.tab.f.get_token("#y_triangles"))

			f.save()
			self.discretizer.force_update()

	def callback_edit_norm_y(self):
		f=inp()
		f.load(os.path.join(self.path,"shape_import.inp"))
		shape_import_y_norm_percent=f.get_token("#shape_import_y_norm_percent")

		self.a=inp_dialog(title=_("Normalization editor"),icon="shape")
		ret=self.a.run(["#shape_import_y_norm_percent",shape_import_y_norm_percent,"#end"])
		if ret==QDialog.Accepted:
			f.replace("#shape_import_y_norm_percent",self.a.tab.f.get_token("#shape_import_y_norm_percent"))
			f.save()
			self.discretizer.force_update()


	def callback_open_image(self):
		file_name=open_as_filter(self,"png (*.png);;jpg (*.jpg)",path=self.path)
		if file_name!=None:
			im = Image.open(file_name)
			im.save(os.path.join(self.path,"image.png"))
			self.discretizer.load_image()
			self.discretizer.build_mesh()

	def callback_script(self):
		self.scripts.show()

	def __init__(self,path):
		QWidgetSavePos.__init__(self,"shape_import")
		self.path=path
		self.discretizer=image_discretizer(self.path)

		self.setMinimumSize(900, 900)
		self.setWindowIcon(icon_get("shape"))

		self.setWindowTitle(_("Import microscope image")+" (https://www.gpvdm.com)") 
		
		self.scripts=scripts(path=self.path,api_callback=self.discretizer.force_update)

		self.scripts.ribbon.help.setVisible(False)
		self.scripts.ribbon.plot.setVisible(False)
		self.scripts.ribbon.hashtag.setVisible(False)

		self.main_vbox = QVBoxLayout()

		self.ribbon=ribbon_shape_import()

		f=inp()
		f.load(os.path.join(self.path,"shape_import.inp"))
		self.ribbon.tb_norm_y.setChecked(str2bool(f.get_token("#shape_import_y_norm")))
		self.ribbon.tb_norm_z.setChecked(str2bool(f.get_token("#shape_import_z_norm")))
		self.ribbon.tb_blur.setChecked(str2bool(f.get_token("#shape_import_blur_enabled")))

		#self.ribbon.xy_triangles.clicked.connect(self.callback_mesh_editor)
		self.ribbon.edit_mesh.triggered.connect(self.callback_mesh_editor)
		self.ribbon.edit_norm_y.triggered.connect(self.callback_edit_norm_y)
		self.ribbon.menu_blur.triggered.connect(self.callback_menu_blur)
		self.ribbon.tb_norm_y.triggered.connect(self.callback_norm_y)
		self.ribbon.tb_norm_z.triggered.connect(self.callback_norm_z)
		self.ribbon.tb_blur.triggered.connect(self.callback_blur_enable)

		self.ribbon.import_image.clicked.connect(self.callback_open_image)
		self.ribbon.save_data.clicked.connect(self.callback_import)
		self.ribbon.show_mesh.clicked.connect(self.callback_show_mesh)

		self.ribbon.tb_script.clicked.connect(self.callback_script)
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
		self.notebook.addTab(self.discretizer,_("Image"))

		self.setLayout(self.main_vbox)
		
		#self.notebook.currentChanged.connect(self.changed_click)

	def callback_show_mesh(self):
		self.discretizer.show_mesh=self.ribbon.show_mesh.isChecked()
		self.discretizer.repaint()

	def callback_import(self):
		self.discretizer.save_mesh()

