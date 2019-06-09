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

## @package scan_tab
#  A scan tab - sub widget.
#

import gc
import os
from inp import inp_get_token_value
from plot import check_info_file
from used_files_menu import used_files_menu
from plot_gen import plot_gen
from dat_file import dat_file
from cmp_class import cmp_class
from token_lib import tokens


from scan_plot import scan_gen_plot_data
from server import server_find_simulations_to_run

from gpvdm_open import gpvdm_open
from cal_path import get_exe_command
from icon_lib import icon_get

from util import str2bool

#scan_io
from scan_io import scan_clean_dir
from scan_io import scan_clean_unconverged
from scan_io import scan_build_nested_simulation
from scan_io import scan_push_to_hpc
from scan_io import scan_import_from_hpc
from scan_io import scan_plot_fits
from scan_io import scan_gen_report
from scan_io import build_scan
from scan_io import scan_build_all_nested

#scan_tree
from scan_tree import tree_gen
from scan_tree import tree_load_program
from scan_tree import tree_load_config
from scan_tree import tree_load_flat_list
from scan_tree import tree_save_flat_list

#scan_item
from scan_item import scan_items_get_file
from scan_item import scan_items_get_token
from scan_item import scan_items_get_list
from scan_item import scan_item_save


#qt
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QApplication,QDialog,QSizePolicy,QAction,QTableWidgetItem,QTabWidget,QMenuBar,QStatusBar, QMenu, QTableWidget, QAbstractItemView, QComboBox
from PyQt5.QtGui import QPainter,QIcon,QCursor,QClipboard

#window
from plot_dlg import plot_dlg_class
from scan_select import select_param
#from notes import notes
from gui_util import tab_add
from gui_util import tab_move_down
from gui_util import tab_move_up
from gui_util import tab_remove
from gui_util import tab_get_value
from error_dlg import error_dlg
from gui_util import yes_no_dlg
from gui_util import tab_get_selected
from gui_util import tab_set_value
from gui_util import tab_insert_row

import i18n
_ = i18n.language.gettext

from gpvdm_select import gpvdm_select
from help import help_window
from code_ctrl import enable_betafeatures

from cal_path import get_sim_path

from scan_ml import scan_ml_build_vector

from progress import progress_class
from process_events import process_events

from scan_io import scan_archive

from win_lin import desktop_open

import datetime

class scan_vbox(QWidget):

	def rename(self,new_name):
		self.sim_name=os.path.basename(new_name)
		self.sim_dir=new_name

		self.status_bar.showMessage(self.sim_dir)
		self.load()
		#self.plotted_graphs.init(self.sim_dir,self.callback_last_menu_click)

	def callback_notes(self, widget, data=None):
		note=notes()
		note.init(self.sim_dir)
		note.show()

	def callback_move_down(self):
		tab_move_down(self.tab)

	def callback_move_up(self):
		tab_move_up(self.tab)

	def callback_insert_command(self):
		a=self.tab.selectionModel().selectedRows()

		if len(a)>0:
			a=a[0].row()
			tab_set_value(self.tab,a,3,"str(round(random.uniform(1.0, 9.9),2))+\"e-\"+str(randint(1, 9))")
			tab_set_value(self.tab,a,4,"python_code")


	def add_line(self,data):
		help_window().help_set_help(["list-add.png",_("<big><b>The scan window</b></big><br> Now using the drop down menu in the prameter to change 'column', select the device parameter you wish to vary, an example may be dos0/Electron Mobility. Now enter the values you would like it to scan oveer in the  'Values', an example could be '1e-3 1e-4 1e-5 1e-6'.  And hit the double arrorw to run the simulation.")])

		self.insert_row(self.tab.rowCount(),data[0],data[1],data[2],data[3],data[4])
		
		self.rebuild_op_type_widgets()
		
		self.save_combo()


	def callback_add_item(self, widget, data=None):
		self.add_line(["File","token",_("Select parameter"), "0.0 0.0", "scan",True])


	def callback_copy_item(self):
		data=tab_get_selected(self.tab)
		combine=';'.join(data)
		
		cb = QApplication.clipboard()
		cb.clear(mode=cb.Clipboard )
		cb.setText(combine, mode=cb.Clipboard)

	def callback_paste_item(self, widget, data=None):
		cb = QApplication.clipboard()
		text=cb.text()
		lines=text.rstrip().split(';')
		#print("text=",lines)
		tab_add(self.tab,lines)
		self.save_combo()
#		row=self.tab.selectionModel().selectedRows()
#		if len(row)>0:
#			row=row[0].row()
#			if len(lines)>=4:
#				for i in range(0,len(lines)):
#					tab_set_value(self.tab,row,i,lines[i])

	def callback_show_list(self):
		self.select_param_window=select_param(self.tab)
		self.select_param_window.set_save_function(self.save_combo)
		self.select_param_window.show()

	def callback_delete_item(self):
		tab_remove(self.tab)
		self.rebuild_op_type_widgets()
		self.save_combo()

	def plot_results(self,plot_token):
		plot_token.key_units=self.get_units()
		#print("scanning",self.sim_dir)
		plot_files, plot_labels, config_file = scan_gen_plot_data(plot_token,self.sim_dir)
		#print(plot_files, plot_labels)
		plot_gen(plot_files,plot_labels,config_file)

		self.last_plot_data=plot_token
		return

	def get_units(self):
		token=""
		for i in range(0,self.tab.rowCount()):
			if tab_get_value(self.tab,i,4)=="scan":
				for ii in range(0,len(self.param_list)):
					if tab_get_value(self.tab,i,2)==self.param_list[ii].human_label:
						token=self.param_list[ii].token
				break
		if token!="":
			found_token=self.tokens.find(token)
			if type(found_token)!=bool:
				return found_token.units

		return ""

	def gen_report(self):
		scan_gen_report(self.sim_dir)

	def make_sim_dir(self):
		if os.path.isdir(self.sim_dir)==False:
			os.makedirs(self.sim_dir)



	def clean_scan_dir(self):
		scan_clean_dir(self.sim_dir,parent_window=self)

	def scan_clean_unconverged(self):
		scan_clean_unconverged(self,self.sim_dir)

	def scan_clean_simulation_output(self):
		scan_clean_dir(self.sim_dir,parent_window=self)

	def import_from_hpc(self):
		scan_import_from_hpc(self.sim_dir)

	def scan_tab_ml_build_vector(self):
		scan_ml_build_vector(self.sim_dir)

	def plot_fits(self):
		scan_plot_fits(self.sim_dir)

	def push_to_hpc(self):
		scan_push_to_hpc(self.sim_dir,False)

	def push_unconverged_to_hpc(self):
		scan_push_to_hpc(self.sim_dir,True)

	def nested_simulation(self):
		scan_build_all_nested(self.sim_dir,parent_window=self)

		#self.send_commands_to_server(commands,"")

	def scan_run(self,args=""):
		commands=tree_load_flat_list(self.sim_dir)
		if commands==False:
			error_dlg(self,_("I can't load flat_list.inp.  This usually means there is a problem with how you have set up your scan."))
			return
		self.send_commands_to_server(commands,args)

	def scan_archive(self):
		scan_archive(self.sim_dir)

	def simulate(self,run_simulation,generate_simulations,args=""):

		run=True

		if self.tab.rowCount() == 0:
			error_dlg(self,_("You have not selected any parameters to scan through.  Use the add button."))
			return


		if self.sim_name=="":
			error_dlg(self,_("No sim dir name"))
			return

		self.make_sim_dir()

		tree_load_config(self.sim_dir)
		if generate_simulations==True:
			build_scan(self.sim_dir,get_sim_path(),parent_window=self)

		if run_simulation==True:
			self.scan_run(args=args)

		self.save_combo()
		os.chdir(get_sim_path())
		gc.collect()

	def build_scan(self):
		build_scan(self.sim_dir,get_sim_path())

	def send_commands_to_server(self,commands,args):
#		self.myserver.init(self.sim_dir)

		for i in range(0, len(commands)):
			self.myserver.add_job(commands[i],args)
			#print("Adding job"+commands[i])

		self.myserver.start()

	def callback_plot_results(self, widget, data=None):
		self.plot_results(self.last_plot_data)

	def callback_last_menu_click(self, widget, data):
		#print("here one!")
		self.plot_results(data)

	def callback_reopen_xy_window(self, widget, data=None):
		if len(self.plotted_graphs)>0:
			pos=len(self.plotted_graphs)-1
			plot_data=dat_file()
			plot_data.file0=self.plotted_graphs[pos].file0
			plot_xy_window=plot_dlg_class(plot_data)
			plot_xy_window.run()
			plot_now=plot_xy_window.ret

			if plot_now==True:
				self.plot_results(plot_data)
				self.plotted_graphs.refresh()

	def callback_gen_plot_command(self):
		dialog=gpvdm_open(self.sim_dir,act_as_browser=False)
		ret=dialog.exec_()

		if ret==QDialog.Accepted:
			full_file_name=dialog.get_filename()
			#dialog.destroy()
			#print cur_dir=os.getcwd()
			#print full_file_name
			file_name=os.path.basename(full_file_name)

			plot_data=dat_file()
			plot_data.path=self.sim_dir
			plot_data.example_file0=full_file_name
			plot_data.example_file1=full_file_name

			plot_now=False
			if check_info_file(file_name)==True:
				plot_data.file0=file_name
				plot_xy_window=plot_dlg_class(plot_data)
				plot_xy_window.run()
				plot_now=plot_xy_window.ret
			else:
				plot_data.file0=file_name
				plot_data.tag0=""
				plot_data.file1=""
				plot_data.tag1=""
				plot_now=True

			if plot_now==True:
				self.plot_results(plot_data)

				#self.plotted_graphs.refresh()


	def save_combo(self):
		self.make_sim_dir()
		a = open(os.path.join(self.sim_dir,"gpvdm_gui_config.inp"), "w")
		a.write(str(self.tab.rowCount())+"\n")

		#print(self.tab.rowCount())
		
		for i in range(0,self.tab.rowCount()):
			#print(i)
			a.write(tab_get_value(self.tab,i,0)+"\n")
			a.write(tab_get_value(self.tab,i,1)+"\n")
			a.write(tab_get_value(self.tab,i,2)+"\n")
			a.write(tab_get_value(self.tab,i,3)+"\n")
			a.write(tab_get_value(self.tab,i,4)+"\n")
			a.write("notused\n")
		a.close()

		if os.path.isfile(os.path.join(self.sim_dir,"scan_config.inp"))==False:
			a = open(os.path.join(self.sim_dir,"scan_config.inp"), "w")
			a.write("#scan_config_args\n")
			a.write("\n")
			a.write("#scan_config_compress\n")
			a.write("false\n")
			a.write("#end\n")

			a.close()

	def tab_changed(self):
		self.rebuild_op_type_widgets()
		self.save_combo()

	def combo_duplicate_changed(self):
		#print("combo changed")
		for i in range(0,self.tab.rowCount()):
			found=False
			value=tab_get_value(self.tab,i,4)

			if value == "constant":
				found=True
				if tab_get_value(self.tab,i,3)=="duplicate":
					tab_set_value(self.tab,i,3,"0.0")
	
			if value == "scan":
				found=True
				if tab_get_value(self.tab,i,3)=="duplicate":
					tab_set_value(self.tab,i,3,"0.0 0.0 0.0")

			if value == "python_code":
				found=True
				if tab_get_value(self.tab,i,3)=="duplicate":
					tab_set_value(self.tab,i,3,"0.0")

			if value == "random_file_name":
				found=True
				tab_set_value(self.tab,i,0,"not needed")
				tab_set_value(self.tab,i,1,"not needed")
				tab_set_value(self.tab,i,2,"not needed")
				if tab_get_value(self.tab,i,3)=="duplicate":
					tab_set_value(self.tab,i,3,"10")

			if found==False:
				tab_set_value(self.tab,i,3,"duplicate")

		self.save_combo()

	def toggled_cb( self, cell, path, model ):
		model[path][3] = not model[path][3]
		#print(model[path][2],model[path][3])
		self.save_combo()
		return

	def insert_row(self,i,v0,v1,v2,v3,v4):
		self.tab.blockSignals(True)
		self.tab.insertRow(i)

		item = QTableWidgetItem(v0)
		self.tab.setItem(i,0,item)

		item = QTableWidgetItem(v1)
		self.tab.setItem(i,1,item)


		self.item = gpvdm_select()
		self.item.setText(v2)
		self.item.button.clicked.connect(self.callback_show_list)

		self.tab.setCellWidget(i,2,self.item)

		item = QTableWidgetItem(v3)
		self.tab.setItem(i,3,item)

		item = QTableWidgetItem(v4)
		self.tab.setItem(i,4,item)
		self.tab.blockSignals(False)

	def load(self):
		self.tab.blockSignals(True)
		self.tab.clear()
		self.tab.setRowCount(0)
		self.tab.setHorizontalHeaderLabels([_("File"), _("Token"), _("Parameter to change"), _("Values"), _("Opperation")])
		self.tab.blockSignals(False)
		
		file_name=os.path.join(self.sim_dir,'gpvdm_gui_config.inp')

		if os.path.isfile(file_name)==True:
			f=open(file_name)
			config = f.readlines()
			f.close()

			for ii in range(0, len(config)):
				config[ii]=config[ii].rstrip()

			pos=0
			mylen=int(config[0])
			pos=pos+1
			
			#print(config)

			for i in range(0, mylen):
				self.insert_row(i,config[pos+0],config[pos+1],config[pos+2],config[pos+3],config[pos+4])

				pos=pos+6


		
		self.rebuild_op_type_widgets()



	def contextMenuEvent(self, event):
		self.popMenu.popup(QCursor.pos())


	def rebuild_op_type_widgets(self):
		self.tab.blockSignals(True)
		items=[]
		items.append("scan")
		items.append("constant")
		items.append("python_code")
		items.append("random_file_name")

		for i in range(0,self.tab.rowCount()):
			items.append(str(tab_get_value(self.tab,i,2)))

		for i in range(0,self.tab.rowCount()):
			save_value=tab_get_value(self.tab,i,4)
			
			combobox = QComboBox()
			for a in items:
				combobox.addItem(a)

			self.tab.setCellWidget(i,4, combobox)
			
			tab_set_value(self.tab,i,4,save_value)
			combobox.currentIndexChanged.connect(self.combo_duplicate_changed)
		self.tab.blockSignals(False)

	def set_tab_caption(self,name):
		mytext=name
		if len(mytext)<10:
			for i in range(len(mytext),10):
				mytext=mytext+" "
		self.tab_label.set_text(mytext)


	def callback_run_simulation(self):
		args=inp_get_token_value(os.path.join(self.sim_dir,"scan_config.inp"),"#scan_config_args")
		if args==None:
			args=""
		self.simulate(True,True,args)


	def callback_examine(self):
		mycmp=cmp_class()
		#ret=mycmp.init(self.sim_dir,get_exe_command())
		ret=mycmp.init()
		if ret==False:
			error_dlg(self,_("Re-run the simulation with 'dump all slices' set to one to use this tool."))
			return

	def callback_notes(self):
		notes_path=os.path.join(self.sim_dir,"notes.txt")
		if os.path.isfile(notes_path)==False:
			out = open(notes_path, 'w')
			out.write("Notes on the simulation: "+os.path.basenam(self.sim_dir)+"\n")
			out.write("Date: "+datetime.datetime.today().strftime('%Y-%m-%d')+"\n")
			out.write("Generated by: "+os.getusername()+"\n")
			out.write("\n")
			out.close()
		else:
			out = open(notes_path, 'a')
			out.write("\n"+datetime.datetime.today().strftime('%Y-%m-%d')+":\n")
			out.close()


		desktop_open(notes_path)

	def __init__(self,myserver,status_bar,scan_root_dir,sim_name):
		QWidget.__init__(self)
		self.main_vbox = QVBoxLayout()

		self.tokens=tokens()
		self.sim_name=sim_name
		self.myserver=myserver
		self.status_bar=status_bar
		self.param_list=scan_items_get_list()
		#self.tab_label=tab_label

		self.sim_dir=os.path.join(scan_root_dir,sim_name)


		
		toolbar=QToolBar()
		toolbar.setIconSize(QSize(32, 32))

		self.tb_add = QAction(icon_get("list-add"), _("Add parameter to scan"), self)
		self.tb_add.triggered.connect(self.callback_add_item)
		toolbar.addAction(self.tb_add)

		self.tb_minus = QAction(icon_get("list-remove"), _("Delete item"), self)
		self.tb_minus.triggered.connect(self.callback_delete_item)
		toolbar.addAction(self.tb_minus)

		self.tb_down = QAction(icon_get("go-down"), _("Move down"), self)
		self.tb_down.triggered.connect(self.callback_move_down)
		toolbar.addAction(self.tb_down)

		self.tb_up = QAction(icon_get("go-up"), _("Move up"), self)
		self.tb_up.triggered.connect(self.callback_move_up)
		toolbar.addAction(self.tb_up)
		
		#self.tb_notes = QAction(icon_get("go-down.png"), _("Notes"), self)
		#self.tb_notes.triggered.connect(self.callback_notes)
		#toolbar.addAction(self.tb_notes)

		#self.tb_notes = QAction(icon_get("select"), _("Select parameter to change"), self)
		#self.tb_notes.triggered.connect(self.callback_show_list)
		#toolbar.addAction(self.tb_notes)

		self.tb_command = QAction(icon_get("utilities-terminal"), _("Insert python command"), self)
		self.tb_command.triggered.connect(self.callback_insert_command)
		toolbar.addAction(self.tb_command)

		self.main_vbox.addWidget(toolbar)

		self.tab = QTableWidget()
		#self.tab.resizeColumnsToContents()

		
		self.tab.verticalHeader().setVisible(False)


		
		self.tab.setColumnCount(5)
		#if enable_betafeatures()==False:
		#	self.tab.setColumnHidden(0, True)
		#	self.tab.setColumnHidden(1, True)

		self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tab.setColumnWidth(2, 300)
		self.tab.setColumnWidth(3, 200)
		self.load()

		self.tab.cellChanged.connect(self.tab_changed)

		self.main_vbox.addWidget(self.tab)

		self.popMenu = QMenu(self)

		#self.mp_show_list=QAction(_("Select parameter to scan"), self)
		#self.mp_show_list.triggered.connect(self.callback_show_list)
		#self.popMenu.addAction(self.mp_show_list)

		self.popMenu.addSeparator()

		self.mp_delete=QAction(_("Delete item"), self)
		self.mp_delete.triggered.connect(self.callback_delete_item)
		self.popMenu.addAction(self.mp_delete)

		self.mp_copy=QAction(_("Copy"), self)
		self.mp_copy.triggered.connect(self.callback_copy_item)
		self.popMenu.addAction(self.mp_copy)

		self.mp_paste=QAction(_("Paste"), self)
		self.mp_paste.triggered.connect(self.callback_paste_item)
		self.popMenu.addAction(self.mp_paste)

		self.popMenu.addSeparator()

		self.mp_add=QAction(_("Add item"), self)
		self.mp_add.triggered.connect(self.callback_add_item)
		self.popMenu.addAction(self.mp_add)

		self.mp_down=QAction(_("Move down"), self)
		self.mp_down.triggered.connect(self.callback_move_down)
		self.popMenu.addAction(self.mp_down)

		self.mp_down=QAction(_("Move down"), self)
		self.mp_down.triggered.connect(self.callback_move_down)
		self.popMenu.addAction(self.mp_down)

		self.popMenu.addSeparator()
		self.setMinimumSize(700,500)
		
		self.setLayout(self.main_vbox)


