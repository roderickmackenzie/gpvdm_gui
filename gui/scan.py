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

## @package scan
#  Them main scan material parameter window.
#

import os
import shutil
from icon_lib import icon_get
from gui_util import dlg_get_text
from util import gpvdm_delete_file
from util import copy_scan_dir
from search import return_file_list
import webbrowser
from search import find_fit_log
from scan_io import get_scan_dirs
from code_ctrl import enable_betafeatures
from inp import inp_update_token_value
from inp import inp_get_token_value
from gui_util import yes_no_dlg
from util import wrap_text

import i18n
_ = i18n.language.gettext

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QMenuBar,QStatusBar
from PyQt5.QtGui import QPainter,QIcon

#window
from scan_tab import scan_vbox
from QHTabBar import QHTabBar

from global_objects import global_object_get

from cal_path import get_sim_path
from QWidgetSavePos import QWidgetSavePos
from scan_ribbon import scan_ribbon
from css import css_apply
from error_dlg import error_dlg
from scan_item import scan_items_populate_from_files

class scan_class(QWidgetSavePos):

	def callback_report(self):
		tab = self.notebook.currentWidget()
		tab.gen_report()

	def callback_change_dir(self):
		dialog = gtk.FileChooserDialog(_("Change directory"),
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OK, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		dialog.set_action(gtk.FILE_CHOOSER_ACTION_CREATE_FOLDER)

		filter = gtk.FileFilter()
		filter.set_name(_("All files"))
		filter.add_pattern("*")
		dialog.add_filter(filter)


		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.sim_dir=dialog.get_filename()

			a = open("scan_window.inp", "w")
			a.write(self.sim_dir)
			a.close()

			self.clear_pages()
			self.load_tabs()
			dialog.destroy()

		return True

	def callback_help(self):
		webbrowser.open('http://www.gpvdm.com/man/index.html')

	def callback_add_page(self):
		new_sim_name=dlg_get_text( _("New simulation name:"), _("Simulation ")+str(self.notebook.count()+1),"document-new.png")
		new_sim_name=new_sim_name.ret

		if new_sim_name!=None:
			new_sim_name=self.remove_invalid(new_sim_name)
			name=os.path.join(os.getcwd(),new_sim_name)
			self.add_page(name)

	def callback_cluster_fit_log(self):
		tab = self.notebook.currentWidget()
		index=self.notebook.currentIndex()
		name=self.notebook.tabText(index)
		path=os.path.join(self.sim_dir,name)
		find_fit_log("./fit.dat",path)
		os.system("gnuplot -persist ./fit.dat &\n")


	def callback_copy_page(self):
		tab = self.notebook.currentWidget()
		index=self.notebook.currentIndex()
		name=self.notebook.tabText(index)
		old_dir=os.path.join(self.sim_dir,name)
		new_sim_name=dlg_get_text( _("Clone the current simulation to a new simulation called:"), name,"clone.png")
		new_sim_name=new_sim_name.ret

		if new_sim_name!=None:
			new_sim_name=self.remove_invalid(new_sim_name)
			new_dir=os.path.join(self.sim_dir,new_sim_name)
			if os.path.isdir(new_dir)==True:
				error_dlg(self,_("This directory already exists."))
				return

			copy_scan_dir(new_dir,old_dir)
			self.add_page(new_sim_name)

	def callback_run_simulation(self):
		tab = self.notebook.currentWidget()
		tab.simulate(True,False,"")

	def callback_build_scan(self):
		tab = self.notebook.currentWidget()
		tab.build_scan()

	def callback_scan_run(self):
		tab = self.notebook.currentWidget()
		tab.scan_run()

	def callback_scan_archive(self):
		tab = self.notebook.currentWidget()
		tab.scan_archive()

	def callback_run_single_fit(self):
		tab = self.notebook.currentWidget()
		tab.simulate(True,False,"--1fit")

	def callback_run_simulation_nogen(self):
		tab = self.notebook.currentWidget()
		tab.simulate(True,False,"")

	def callback_plot_fits(self):
		tab = self.notebook.currentWidget()
		tab.plot_fits()

	def callback_nested_simulation(self):
		tab = self.notebook.currentWidget()
		tab.nested_simulation()


	def callback_clean_simulation(self):
		tab = self.notebook.currentWidget()
		tab.clean_scan_dir()

	def callback_clean_unconverged_simulation(self):
		tab = self.notebook.currentWidget()
		tab.scan_clean_unconverged()

	def callback_clean_simulation_output(self):
		tab = self.notebook.currentWidget()
		tab.scan_clean_simulation_output()


	def callback_push_unconverged_to_hpc(self):
		tab = self.notebook.currentWidget()
		tab.push_unconverged_to_hpc()

	def remove_invalid(self,input_name):
		return input_name.replace (" ", "_")

	def callback_rename_page(self):
		tab = self.notebook.currentWidget()

		index=self.notebook.currentIndex()
		name=self.notebook.tabText(index)
		old_dir=os.path.join(self.sim_dir,name)

		new_sim_name=dlg_get_text( _("Rename the simulation to be called:"), name,"rename.png")
		new_sim_name=new_sim_name.ret

		if new_sim_name!=None:
			new_sim_name=self.remove_invalid(new_sim_name)
			new_dir=os.path.join(self.sim_dir,new_sim_name)
			shutil.move(old_dir, new_dir)
			tab.rename(new_dir)
			index=self.notebook.currentIndex() 
			self.notebook.setTabText(index, new_sim_name)

	def callback_delete_page(self):
		tab = self.notebook.currentWidget()
		index=self.notebook.currentIndex()
		name=self.notebook.tabText(index)
		
		dir_to_del=os.path.join(self.sim_dir,name)

		response=yes_no_dlg(self,_("Should I remove the simulation directory ")+dir_to_del)

		if response==True:
			index=self.notebook.currentIndex() 
			self.notebook.removeTab(index)
			gpvdm_delete_file(dir_to_del)


	def callback_run_all_simulations(self):
		for i in range(0,self.notebook.count()):
			tab = self.notebook.widget(i)
			tab.simulate(True,True,"")

	def callback_stop_simulation(self,widget):
		tab = self.notebook.currentWidget()
		tab.stop_simulation()

	def load_tabs(self):
		sim_dirs=[]

		get_scan_dirs(sim_dirs,self.sim_dir)


		if len(sim_dirs)==0:
			sim_dirs.append("scan1")
		else:
			for i in range(0,len(sim_dirs)):
				sim_dirs[i]=sim_dirs[i]

		for i in range(0,len(sim_dirs)):
			self.add_page(sim_dirs[i])

		if self.notebook.count()!=0:
			self.ribbon.goto_page(_("Simulations"))

	def clear_pages(self):
		self.notebook.clear()

	def add_page(self,name):
		tab=scan_vbox(self.myserver,self.status_bar,self.sim_dir,name)
		self.notebook.addTab(tab,os.path.basename(name))

	def callback_mb_build_vectors(self):
		tab = self.notebook.currentWidget()
		tab.scan_tab_ml_build_vector()

	def callback_notes(self):
		tab = self.notebook.currentWidget()
		tab.callback_notes()

	def __init__(self,my_server):
		QWidgetSavePos.__init__(self,"scan_window")
		self.myserver=my_server
		self.setMinimumSize(1000,500)
		self.setWindowTitle(_("Parameter scan - gpvdm"))
		self.setWindowIcon(icon_get("scan"))

		self.rod=[]
		self.sim_dir=get_sim_path()

		self.main_vbox = QVBoxLayout()
		self.ribbon=scan_ribbon()
		self.main_vbox.addWidget(self.ribbon)

		self.ribbon.menu_plot_fits.triggered.connect(self.callback_plot_fits)

		self.ribbon.menu_run_nested.triggered.connect(self.callback_nested_simulation)

		self.ribbon.sim_no_gen.triggered.connect(self.callback_run_simulation_nogen)

		self.ribbon.single_fit.triggered.connect(self.callback_run_single_fit)

		self.ribbon.tb_clean.triggered.connect(self.callback_clean_simulation)

		self.ribbon.clean_unconverged.triggered.connect(self.callback_clean_unconverged_simulation)

		self.ribbon.clean_sim_output.triggered.connect(self.callback_clean_simulation_output)

		self.ribbon.push_unconverged_to_hpc.triggered.connect(self.callback_push_unconverged_to_hpc)

		self.ribbon.change_dir.triggered.connect(self.callback_change_dir)
		
		self.ribbon.report.triggered.connect(self.callback_report)


		self.ribbon.tb_new.triggered.connect(self.callback_add_page)

		self.ribbon.tb_delete.triggered.connect(self.callback_delete_page)

		self.ribbon.tb_clone.triggered.connect(self.callback_copy_page)

		self.ribbon.tb_rename.triggered.connect(self.callback_rename_page)
		
		self.ribbon.tb_simulate.start_sim.connect(self.callback_run_simulation)

		self.ribbon.tb_build.triggered.connect(self.callback_build_scan)

		self.ribbon.tb_rerun.triggered.connect(self.callback_scan_run)

		self.ribbon.tb_zip.triggered.connect(self.callback_scan_archive)

		self.ribbon.tb_run_all.triggered.connect(self.callback_run_all_simulations)

		self.ribbon.tb_plot.triggered.connect(self.callback_plot)
	
		self.ribbon.tb_plot_time.triggered.connect(self.callback_examine)

		self.ribbon.tb_ml_build_vectors.triggered.connect(self.callback_mb_build_vectors)

		self.ribbon.tb_notes.triggered.connect(self.callback_notes)


		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


		self.notebook = QTabWidget()
		self.notebook.setTabBar(QHTabBar())
		css_apply(self.notebook,"style_h.css")

		self.notebook.setTabPosition(QTabWidget.West)
		self.notebook.setMovable(True)


		self.main_vbox.addWidget(self.notebook)


		self.status_bar=QStatusBar()
		self.main_vbox.addWidget(self.status_bar)		

		self.load_tabs()

		scan_items_populate_from_files()
		self.setLayout(self.main_vbox)

	def callback_plot(self):
		tab = self.notebook.currentWidget()
		tab.callback_gen_plot_command()
	
	def callback_examine(self):
		tab = self.notebook.currentWidget()
		tab.callback_examine()
		
	def callback_run_simulation(self):
		tab = self.notebook.currentWidget()
		tab.callback_run_simulation()

	def callback_stop_simulation(self):
		self.myserver.killall()
