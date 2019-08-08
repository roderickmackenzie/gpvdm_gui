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

## @package gl_layer_editor
#  An OpenGL layer editor.
#

import sys
from math import fabs

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtOpenGL
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtWidgets import QMenu
from gl_color import set_color
from gl_lib import val_to_rgb
from object_editor import object_editor


from PyQt5.QtCore import QTimer

from epitaxy import get_epi
from gui_util import dlg_get_text

class gl_layer_editor():

	def menu_layer(self,event):
		view_menu = QMenu(self)
		

		menu = QMenu(self)

		action=menu.addAction(_("Move up"))
		action.triggered.connect(self.layer_move_up)

		action=menu.addAction(_("Move down"))
		action.triggered.connect(self.layer_move_down)

		action=menu.addAction(_("Delete"))
		action.triggered.connect(self.layer_delete)

		action=menu.addAction(_("Add"))
		action.triggered.connect(self.layer_add)

		action=menu.addAction(_("Rename"))
		action.triggered.connect(self.layer_rename)

		action=menu.addAction(_("Object editor"))
		action.triggered.connect(self.layer_object_editor)

		menu.addSeparator()

		#action=menu.addAction(_("Set layer active"))
		#action=menu.addAction(_("Thickness"))

		#action=menu.addAction(_("Optical properties"))
		#action=menu.addAction(_("Electrical properties"))


		#action.triggered.connect(self.layer_move_down)

		#menu.addSeparator()
		menu.exec_(event.globalPos())

	def layer_move_up(self):
		epi=get_epi()
		epi.move_up(self.selected_layer[len("layer:"):])
		epi.save()
		#print("layer_move_up",self.selected_layer[len("layer:"):])
		self.do_draw() 

	def layer_add(self):
		epi=get_epi()
		pos=self.selected_layer[len("layer:"):]
		#print(pos)
		epi.add_layer(pos=pos)
		epi.save()
		
	def layer_move_down(self):
		epi=get_epi()
		epi.move_down(self.selected_layer[len("layer:"):])
		epi.save()
		#print("layer_move_down",self.selected_layer[len("layer:"):])
		self.do_draw()

	def layer_delete(self):
		epi=get_epi()
		epi.remove_layer(self.selected_layer[len("layer:"):])
		epi.save()
		self.do_draw()

	def layer_rename(self):
		old_name=self.selected_layer[len("layer:"):]

		name=dlg_get_text( _("Rename the layer:"), old_name,"rename.png")

		name=name.ret

		if name!=None:
			epi=get_epi()
			epi.rename_layer(old_name,name)
			epi.save()

		self.do_draw()

	def layer_object_editor(self):
		name=self.selected_layer[len("layer:"):]
		epi=get_epi()
		index=epi.layer_to_index(name)
		
		print(">>>>>>>loading shapes for >>>>",index)
		self.shape_edit=object_editor()
		self.shape_edit.load(index)
		self.shape_edit.show()
		#epi.save()

		#self.do_draw()
