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

## @package layer_widget
#  The window to select and build the device structure.
#


import os
from util import str2bool
from icon_lib import icon_get
from cal_path import get_materials_path
from global_objects import global_object_get

#inp
from inp import inp_update_token_value

#epitaxy
from epitaxy import epitaxy_get_layers

#windows
from gui_util import tab_move_down
from gui_util import tab_move_up
from gui_util import tab_remove
from gui_util import tab_get_value
from gui_util import tab_set_value
from gui_util import tab_insert_row
from error_dlg import error_dlg

#qt
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout , QDialog,QToolBar,QAction, QSizePolicy, QTableWidget, QTableWidgetItem,QAbstractItemView

from global_objects import global_object_run

from global_objects import global_isobject
from global_objects import global_object_get

from QComboBoxLang import QComboBoxLang

import i18n
_ = i18n.language.gettext


from gpvdm_select_material import gpvdm_select_material

from code_ctrl import enable_betafeatures
from cal_path import get_sim_path
from QWidgetSavePos import QWidgetSavePos

from epitaxy_mesh_update import epitaxy_mesh_update
from epitaxy import get_epi

from error_dlg import error_dlg

from inp import inp_callback_add_write_hook



class layer_widget(QWidgetSavePos):

	
	def callback_tab_selection_changed(self):
		#self.tab_changed(0,0)
		self.emit_change()

	def cell_changed(self, y,x):
		epi=get_epi()

		if x==0:
			epi.layers[y].name=tab_get_value(self.tab,y,x)
		elif x==1:
			ret=epi.layers[y].set_width(tab_get_value(self.tab,y,x))
			if ret==False:
				error_dlg(self,_("You have entered a non numeric value."))
		self.save_model()
		self.emit_structure_changed()
		
	def emit_change(self):
		global_object_run("gl_force_redraw")
		
	def emit_structure_changed(self):		#This will emit when there has been an edit
		global_object_run("mesh_update")
		global_object_run("optics_force_redraw")
		global_object_run("gl_force_redraw")

	def layer_type_edit(self):
		self.tab.blockSignals(True)

		epi=get_epi()
		for i in range(0,self.tab.rowCount()):
			epi.update_layer_type(i,tab_get_value(self.tab,i,3).lower())
			tab_set_value(self.tab,i,4,epi.layers[i].electrical_layer)
			tab_set_value(self.tab,i,5,epi.layers[i].pl_file)

		self.tab.blockSignals(False)

		self.save_model()
		self.emit_change()
		global_object_run("dos_update")
		global_object_run("pl_update")

	def on_move_down(self):
		layer=tab_move_down(self.tab)
		epi=get_epi()
		epi.move_down(layer)

		self.save_model()
		self.emit_change()
		self.emit_structure_changed()

	def on_move_up(self):
		layer=tab_move_up(self.tab)
		epi=get_epi()
		epi.move_up(layer)
		self.save_model()
		self.emit_change()
		self.emit_structure_changed()

	def __init__(self):
		QWidgetSavePos.__init__(self,"layer_widget")

		self.setWindowTitle(_("Layer editor")+" https://www.gpvdm.com")
		self.setWindowIcon(icon_get("layers"))
		self.resize(800,500)

		self.cost_window=False

		self.main_vbox=QVBoxLayout()

		self.toolbar=QToolBar()
		self.toolbar.setIconSize(QSize(32, 32))

		self.tb_add = QAction(icon_get("list-add"), _("Add device layer"), self)
		self.tb_add.triggered.connect(self.on_add_item_clicked)
		self.toolbar.addAction(self.tb_add)

		self.tb_remove = QAction(icon_get("list-remove"), _("Delete device layer"), self)
		self.tb_remove.triggered.connect(self.on_remove_item_clicked)
		self.toolbar.addAction(self.tb_remove)


		self.tb_down= QAction(icon_get("go-down"), _("Move device layer"), self)
		self.tb_down.triggered.connect(self.on_move_down)
		self.toolbar.addAction(self.tb_down)

		self.tb_up= QAction(icon_get("go-up"), _("Move device layer"), self)
		self.tb_up.triggered.connect(self.on_move_up)
		self.toolbar.addAction(self.tb_up)
		
		self.main_vbox.addWidget(self.toolbar)
	
		self.tab = QTableWidget()
		#self.tab.resizeColumnsToContents()


		self.tab.verticalHeader().setVisible(False)
		self.create_model()

		self.tab.cellChanged.connect(self.cell_changed)
		self.tab.itemSelectionChanged.connect(self.callback_tab_selection_changed)
		self.main_vbox.addWidget(self.tab)

		self.setLayout(self.main_vbox)

		self.tab.itemSelectionChanged.connect(self.layer_selection_changed)

		inp_callback_add_write_hook(os.path.join(get_sim_path(),"epitaxy.inp"),self.create_model,"layer_widget")

	def create_model(self):
		self.tab.blockSignals(True)
		self.tab.clear()
		self.tab.setColumnCount(6)
		#if enable_betafeatures()==False:
		#	self.tab.setColumnHidden(4, True)
		#	self.tab.setColumnHidden(5, True)

		self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tab.setHorizontalHeaderLabels([_("Layer name"), _("Thicknes"), _("Optical material"), _("Layer type"), _("DoS file"), _("PL file")])
		self.tab.setColumnWidth(2, 250)
		self.tab.setRowCount(epitaxy_get_layers())

		epi=get_epi()
		i=0
		for l in epi.layers:
			self.add_row(i,l.width,l.mat_file,l.electrical_layer,l.pl_file,l.name)
			i=i+1

		self.tab.blockSignals(False)

	def add_row(self,i,thick,material,dos_layer,pl_file,name):

		self.tab.blockSignals(True)

		dos_file=""
		
		if dos_layer.startswith("dos")==True:
			dos_file="active layer"
		else:
			dos_file=dos_layer

		item1 = QTableWidgetItem(str(name))
		self.tab.setItem(i,0,item1)

		item2 = QTableWidgetItem(str(thick))
		self.tab.setItem(i,1,item2)


		combobox = gpvdm_select_material()
		combobox.setText(material)
		combobox.changed.connect(self.callback_material_select)
		
		self.tab.setCellWidget(i,2, combobox)

		combobox_layer_type = QComboBoxLang()

		combobox_layer_type.addItemLang("contact",_("contact"))
		combobox_layer_type.addItemLang("active layer",_("active layer"))
		combobox_layer_type.addItemLang("other",_("other"))

		self.tab.setCellWidget(i,3, combobox_layer_type)
		combobox_layer_type.setValue_using_english(str(dos_file).lower())

		item3 = QTableWidgetItem(str(dos_layer))
		self.tab.setItem(i,4,item3)

		item3 = QTableWidgetItem(str(pl_file))
		self.tab.setItem(i,5,item3)

		combobox_layer_type.currentIndexChanged.connect(self.layer_type_edit)

		self.tab.blockSignals(False)

	def callback_material_select(self):
		epi=get_epi()
		for i in range(0,self.tab.rowCount()):
			epi.layers[i].set_mat_file(self.tab.cellWidget(i, 2).text())

		self.emit_structure_changed()
		self.save_model()
		#self.emit_change()

	def on_remove_item_clicked(self):
		pos=tab_remove(self.tab)
		if pos>0:
			epi=get_epi()
			epi.remove_layer(pos)
			epi.save()
			epi.clean_unused_files()
			#self.emit_change()

	def on_add_item_clicked(self):
		row=tab_insert_row(self.tab)
		print(row)
		epi=get_epi()
		a=epi.add_layer(pos=row)
		self.add_row(row,str(a.width),a.mat_file,a.electrical_layer,a.pl_file,a.name)
		epi.save()
		#self.emit_change()
		return

	def save_model(self):
		epi=get_epi()
		epi.save()

		epitaxy_mesh_update()

	def layer_selection_changed(self):
		a=self.tab.selectionModel().selectedRows()

		if len(a)>0:
			y=a[0].row()
			y="layer:"+str(tab_get_value(self.tab,y, 0))
		else:
			y=-1
		
		if global_isobject("display_set_selected_layer")==True:
			global_object_get("display_set_selected_layer")(y)
		global_object_run("gl_force_redraw")

		#self.three_d.set_selected_layer(y)
		#self.three_d.update()
