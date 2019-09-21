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

## @package triangle_xy_editor
#  A window to edit the dimentions of the device.
#

import os
from str2bool import str2bool
from inp import inp_search_token_value
from scan_item import scan_item_add
from scan_item import scan_remove_file
from icon_lib import icon_get
from gpvdm_open import gpvdm_open
from cal_path import get_materials_path
from global_objects import global_object_get
from help import help_window

#inp
from inp import inp_isfile
from inp import inp_copy_file
from inp import inp_update_token_value
from inp import inp_load_file
from inp import inp_lsdir
from inp import inp_remove_file

#windows
from gui_util import yes_no_dlg
from error_dlg import error_dlg


#qt
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon,QPalette
from PyQt5.QtWidgets import QWidget, QVBoxLayout,QPushButton,QLineEdit,QLabel,QDesktopWidget,QToolBar,QHBoxLayout,QAction, QSizePolicy, QTableWidgetItem,QComboBox

from PyQt5.QtCore import pyqtSignal

from PyQt5.QtWidgets import QWidget

import i18n
_ = i18n.language.gettext


from QWidgetSavePos import QWidgetSavePos

from inp import inp_get_token_value
from inp import inp_update_token_value

class triangle_xy_editor(QWidgetSavePos):
	changed = pyqtSignal()

	def __init__(self,path):
		QWidgetSavePos.__init__(self,"triangle_xy_editor")

		self.setWindowTitle(_("Triangle editor")+" https://www.gpvdm.com")
		self.setWindowIcon(icon_get("shape"))
		self.resize(400,200)

		self.cost_window=False
		self.path=path

		self.main_vbox=QVBoxLayout()

		self.toolbar=QToolBar()
		self.toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		self.toolbar.setIconSize(QSize(42, 42))

		spacer = QWidget()


		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.toolbar.addWidget(spacer)

		self.help = QAction(icon_get("internet-web-browser"), _("Help"), self)
		self.toolbar.addAction(self.help)
		
		self.main_vbox.addWidget(self.toolbar)
	
		self.widget0 = QWidget()
		self.widget0_hbox=QHBoxLayout()
		self.widget0.setLayout(self.widget0_hbox)

		self.widget0_label=QLabel("x triangles:")
		self.widget0_hbox.addWidget(self.widget0_label)

		self.widget0_edit=QLineEdit()
		self.widget0_edit.setText(inp_get_token_value(os.path.join(self.path,"shape_import.inp"),"#x_trianges"))
		self.widget0_hbox.addWidget(self.widget0_edit)

		self.main_vbox.addWidget(self.widget0)

		self.widget1 = QWidget()
		self.widget1_hbox=QHBoxLayout()
		self.widget1.setLayout(self.widget1_hbox)
		self.widget1_label=QLabel("y triangles:")
		self.widget1_hbox.addWidget(self.widget1_label)
		self.widget1_edit=QLineEdit()
		self.widget1_edit.setText(inp_get_token_value(os.path.join(self.path,"shape_import.inp"),"#y_trianges"))
		self.widget1_hbox.addWidget(self.widget1_edit)

		self.main_vbox.addWidget(self.widget1)


		button_box=QHBoxLayout()

		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		button_box.addWidget(spacer)
		self.ok=QPushButton("OK", self)
		self.ok.clicked.connect(self.callback_ok)
		button_box.addWidget(self.ok)

		button_box_widget=QWidget()
		button_box_widget.setLayout(button_box)
		self.main_vbox.addWidget(button_box_widget)

		#self.tab.itemSelectionChanged.connect(self.callback_tab_selection_changed)

		self.setLayout(self.main_vbox)

		#self.tab.itemSelectionChanged.connect(self.layer_selection_changed)


	def callback_ok(self):
		inp_update_token_value(os.path.join(self.path,"shape_import.inp"), "#x_trianges", self.widget0_edit.text())
		inp_update_token_value(os.path.join(self.path,"shape_import.inp"), "#y_trianges", self.widget1_edit.text())
		self.changed.emit()
		self.close()


