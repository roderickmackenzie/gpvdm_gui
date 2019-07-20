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
#  An editor for shape files
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
from QWidgetSavePos import QWidgetSavePos
from css import css_apply

from global_objects import global_object_run
from epitaxy import get_epi
from util import wrap_text
from inp import inp_copy_file

from shape import shape
from cal_path import get_sim_path
from inp import inp_get_token_value
from inp import inp_update_token_value
from inp import inp_ls_seq_files
from inp import inp_remove_file

from gui_util import dlg_get_text
from error_dlg import error_dlg
from gui_util import yes_no_dlg
from cal_path import get_default_material_path

articles = []
mesh_articles = []

class shape_editor(QWidgetSavePos):

	def callback_help(self):
		webbrowser.open('http://www.gpvdm.com/man/index.html')

	def __init__(self):
		QWidgetSavePos.__init__(self,"shape_editor")
		self.setMinimumSize(40, 200)
		self.setWindowIcon(icon_get("diode"))

		self.setWindowTitle(_("Micro lens editor")+"  (https://www.gpvdm.com)") 
		

		self.main_vbox = QVBoxLayout()

		toolbar=QToolBar()
		toolbar.setIconSize(QSize(48, 48))

		self.tb_new = QAction(icon_get("document-new"), wrap_text("New shape",2), self)
		self.tb_new.triggered.connect(self.callback_add_shape)

		toolbar.addAction(self.tb_new)

		self.tb_delete = QAction(icon_get("edit-delete"), wrap_text("Delete shape",3), self)
		self.tb_delete.triggered.connect(self.callback_delete_shape)

		toolbar.addAction(self.tb_delete)

		self.tb_rename = QAction(icon_get("rename"), wrap_text("Rename shape",3), self)
		self.tb_rename.triggered.connect(self.callback_rename_shape)
		toolbar.addAction(self.tb_rename)


		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		toolbar.addWidget(spacer)


		self.help = QAction(icon_get("help"), _("Help"), self)
		self.help.setStatusTip(_("Close"))
		self.help.triggered.connect(self.callback_help)
		toolbar.addAction(self.help)

		self.main_vbox.addWidget(toolbar)


		self.notebook = QTabWidget()
		css_apply(self.notebook,"tab_default.css")
		self.notebook.setMovable(True)

		self.main_vbox.addWidget(self.notebook)


		self.setLayout(self.main_vbox)

	def load(self,layer_index):
		self.layer_index=layer_index
		shapes=get_epi().get_shapes(self.layer_index)
		for s in shapes:
			my_tab=tab_class()
			shape_name=inp_get_token_value(s.file_name+".inp", "#shape_name")

			my_tab.init(s.file_name+".inp",s.file_name+".inp")
			self.notebook.addTab(my_tab,shape_name)	

	def callback_add_shape(self):
		new_filename=get_epi().new_shape_file()+".inp"
		orig_filename=os.path.join(get_default_material_path(),"shape.inp")
		inp_copy_file(os.path.join(get_sim_path(),new_filename),os.path.join(get_sim_path(),orig_filename))

		my_shape=shape()
		my_shape.load(new_filename)
		get_epi().layers[self.layer_index].shapes.append(my_shape)
		get_epi().save()

		shape_name=inp_get_token_value(new_filename, "#shape_name")

		my_tab=tab_class()
		my_tab.init(new_filename,new_filename)
		self.notebook.addTab(my_tab,shape_name)
		global_object_run("gl_force_redraw")


	def callback_rename_shape(self):
		tab = self.notebook.currentWidget()
		name=inp_get_token_value(tab.file_name, "#shape_name")

		new_sim_name=dlg_get_text( "Rename the shape:", name,"rename.png")

		new_sim_name=new_sim_name.ret

		if new_sim_name!=None:
			inp_update_token_value(tab.file_name, "#shape_name", new_sim_name)
			index=self.notebook.currentIndex() 
			self.notebook.setTabText(index, new_sim_name)


	def callback_delete_shape(self):
		files=inp_ls_seq_files(os.path.join(get_sim_path(),"sim.gpvdm"),"shape")

		tab = self.notebook.currentWidget()
		name=inp_get_token_value(tab.file_name, "#shape_name")

		response=yes_no_dlg(self,"Do you really want to delete the file: "+name)

		if response == True:
			inp_remove_file(os.path.join(get_sim_path(),tab.file_name))

			index=self.notebook.currentIndex() 
			self.notebook.removeTab(index)

			for i in range(0,len(get_epi().layers[self.layer_index].shapes)):
				if get_epi().layers[self.layer_index].shapes[i].file_name+".inp"==tab.file_name:
					get_epi().layers[self.layer_index].shapes.pop(i)
					get_epi().save()
					break

		global_object_run("gl_force_redraw")

