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

## @package display
#  The display widget, this either displays the 3D OpenGL image of the device or the fallback non OpenGL widget.
#

import os

#inp
from inp import inp_get_token_value

#path
from cal_path import get_materials_path

from gl import glWidget
from gl_fallback import gl_fallback
#qt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QSizePolicy,QVBoxLayout,QPushButton,QDialog,QFileDialog,QToolBar,QMessageBox, QLineEdit,QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal

from icon_lib import icon_get

from help import help_window
from gl_cmp import gl_cmp

from str2bool import str2bool
from fx_selector import fx_selector

from cal_path import get_sim_path
from global_objects import global_object_register
from global_objects import global_object_run

from mesh import get_mesh
from circuit_editor import circuit_editor
from cal_path import get_sim_path
from epitaxy import get_epi
from inp import inp

class display_mesh(QWidget):


	def __init__(self):
		QWidget.__init__(self)
		self.complex_display=False

		self.hbox=QVBoxLayout()

		mesh=get_mesh()
		if mesh.y.circuit_model==True and mesh.x.tot_points==1 and mesh.z.tot_points==1:
			self.display=circuit_editor()

			epi=get_epi()
			pos=3
			self.display.ersatzschaltbild.add_object(pos,3,pos+1,3,"bat")
			pos=pos+1

			for l in epi.layers:
				f=inp()
				f.load(os.path.join(get_sim_path(),l.electrical_file+".inp"))
				component=f.get_token("#electrical_component")
				if component=="resistance":
					self.display.ersatzschaltbild.add_object(pos,3,pos+1,3,"resistor")
				if component=="diode":
					self.display.ersatzschaltbild.add_object(pos,3,pos+1,3,"diode")

				pos=pos+1
			self.display.ersatzschaltbild.add_object(pos,3,pos+1,3,"ground")
			self.display.ersatzschaltbild.objects_push()

			if inp().isfile(os.path.join(get_sim_path(),"diagram.inp"))==True:
				self.display.ersatzschaltbild.load()
		else:
			toolbar=QToolBar()
			toolbar.setIconSize(QSize(42, 42))

			spacer = QWidget()
			spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
			toolbar.addWidget(spacer)

			self.xy = QAction(icon_get("xy"), _("xy"), self)
			self.xy.triggered.connect(self.callback_xy)
			toolbar.addAction(self.xy)

			self.yz = QAction(icon_get("yz"), _("yz"), self)
			self.yz.triggered.connect(self.callback_yz)
			toolbar.addAction(self.yz)

			self.xz = QAction(icon_get("xz"), _("xz"), self)
			self.xz.triggered.connect(self.callback_xz)
			toolbar.addAction(self.xz)
			
			self.tb_rotate = QAction(icon_get("rotate.png"), _("Rotate"), self)
			self.tb_rotate.triggered.connect(self.tb_rotate_click)
			toolbar.addAction(self.tb_rotate)
			self.tb_rotate.setEnabled(True)


			self.hbox.addWidget(toolbar)
			
			self.display=glWidget(self)
			self.display.draw_electrical_mesh=True
			self.display.enable_draw_device=False
			self.display.enable_cordinates=False
			self.display.view.render_photons=False
			#self.display.force_redraw()
			global_object_register("display_mesh_recalculate",self.recalculate)

		self.hbox.addWidget(self.display)
			
		self.setLayout(self.hbox)


	def callback_xy(self):
		self.display.xy()

	def callback_yz(self):
		self.display.yz()
		
	def callback_xz(self):
		self.display.xz()

	def tb_rotate_click(self):
		self.display.start_rotate()

	#This will reclaculate all the display elements in the display widget.
	def recalculate(self):
		self.display.force_redraw()
		
	def update(self):
		self.display.reset()


