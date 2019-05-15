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


## @package cmp_class
#  Compare simulation results window as a function of time.
#

import os
from inp import inp_update_token_value
from inp import inp_save
from inp import inp_load_file
from inp import inp_search_token_value
from plot_widget import plot_widget
from dat_file_class import dat_file
from plot_io import plot_load_info
from cal_path import get_exe_command
from icon_lib import icon_get
import webbrowser

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QHBoxLayout,QLabel,QComboBox
from PyQt5.QtGui import QPainter,QIcon

from snapshot_slider import snapshot_slider

from open_save_dlg import save_as_filter

from PyQt5.QtWidgets import QApplication

from help import help_window
from QWidgetSavePos import QWidgetSavePos
from cal_path import get_sim_path

class cmp_class(QWidgetSavePos):
	mix_y=None
	max_y=None
	max_z=1e24

	def check_2d_file(self,name):
		mapfiles=["pt_map","nt_map"]
		filename=os.path.basename(name)
		for i in range(len(filename)-1,0,-1):
			if filename[i]=="_":
				break
		data=filename[:i]
		count=mapfiles.count(data)
		if count==1:
			return True
		else:
			return False


	def do_clip(self):

		snap = self.canvas.get_snapshot()
		pixbuf = gtk.gdk.pixbuf_get_from_drawable(None, snap, snap.get_colormap(),0,0,0,0,snap.get_size()[0], snap.get_size()[1])
		clip = gtk.Clipboard()
		clip.set_image(pixbuf)


	def on_key_press_event(self,widget, event):
		#keyname = gtk.gdk.keyval_name(event.keyval)
		if gtk.gdk.keyval_name(event.keyval) == "c":
			if event.state == gtk.gdk.CONTROL_MASK:
				self.do_clip()

	def update(self):
		file_name=self.slider.get_file_name()
		if file_name!=None:
			self.plot.set_labels(["data"])
			config_file=os.path.splitext(file_name)[0]+".oplot"
			self.plot.load_data([file_name],config_file)
			self.plot.do_plot()


	def callback_scale(self, adj):
		self.update(self.adj1.value)

		if plot_load_info(self.plot_token,self.file_names[0])==True:
			self.plot.do_plot()


	def callback_edit(self,data):
		lines=[]
		lines.append("#entry0")
		lines.append(self.entry0.get_active_text())
		lines.append("#entry1")
		lines.append(self.entry1.get_active_text())
		lines.append("#entry2")
		lines.append(self.entry2.get_text())
		lines.append("#entry3")
		lines.append(self.entry3.get_text())
		inp_save("gui_cmp_config.inp",lines)
		self.plot.gen_colors(2)
		self.count_dumps()

	def config_load(self):
		lines=inp_load_file("gui_cmp_config.inp")
		if lines!=False:

			if self.snapshot_list.count(inp_search_token_value(lines, "#entry0"))!=0:
				self.entry0.set_active(self.snapshot_list.index(inp_search_token_value(lines, "#entry0")))
			else:
				self.entry0.set_active(0)

			if self.snapshot_list.count(inp_search_token_value(lines, "#entry1"))!=0:
				self.entry1.set_active(self.snapshot_list.index(inp_search_token_value(lines, "#entry1")))
			else:
				self.entry1.set_active(0)

			self.entry2.set_text(inp_search_token_value(lines, "#entry2"))
			self.entry3.set_text(inp_search_token_value(lines, "#entry3"))

		else:
			self.entry0.set_active(0)
			self.entry1.set_active(0)
			self.entry2.set_text("n p")
			self.entry3.set_text("")

	def save_image(self,file_name):
		file_ext="jpg"
		types=self.plot.fig.canvas.get_supported_filetypes()
		if "jpg" in types:
			file_ext="jpg"
		elif "png" in  types:
			file_ext="png"

		dir_name, ext = os.path.splitext(file_name)

		if (ext=="."+file_ext):
			self.plot.fig.savefig(file_name)
		elif ext==".avi":

			if os.path.isdir(dir_name)==False:
				os.mkdir(dir_name)

			jpgs=""
			for i in range(0,self.slider.slider_max):
				self.slider.slider0.setValue(i)
				QApplication.processEvents()
				self.update()
				self.plot.do_plot()
				image_name=os.path.join(dir_name,"image_"+str(i)+"."+file_ext)
				print(image_name)
				self.plot.fig.savefig(image_name)
				jpgs=jpgs+" mf://"+image_name

			os.system("mencoder "+jpgs+" -mf type="+file_ext+":fps=1.0 -o "+file_name+" -ovc lavc -lavcopts vcodec=mpeg1video:vbitrate=800")
			#msmpeg4v2
		else:
			print("Unknown file extension")

	def callback_save(self, widget, data=None):
		file_name=save_as_filter(self,"avi (*.avi)")
		if file_name!=None:
			self.save_image(file_name)

	def callback_help(self, widget, data=None):
		webbrowser.open('http://www.gpvdm.com/man/gpvdm.html')


	def callback_toggle_subtract(self, widget, data):
		self.plot.zero_frame_enable=data.get_active()
		self.update(self.adj1.value)
		print("CONVERTh!!!!!!!!!!!",type(self.plot.plot_token.key_units))
		self.plot.do_plot()

	def callback_multi_plot(self, data, widget):
		if widget.get_active()==True:
			self.multi_plot=True
		else:
			self.multi_plot=False
		self.update(self.adj1.value)
		self.plot.do_plot()

	def find_snapshots(self):

		matches = []
		for root, dirnames, filenames in os.walk(get_sim_path()):
			for filename in filenames:
				my_file=os.path.join(root,filename)
				if my_file.endswith("snapshots.inp")==True:
					matches.append( os.path.dirname(my_file))

		return matches

	def callback_snapshots_combobox(self):
		self.slider.set_path(self.snapshots_combobox.currentText())
		
	def __init__(self,path=None):
		QWidgetSavePos.__init__(self,"cmpclass")
		self.snapshots_widget=None
		self.setWindowTitle(_("Examine simulation results in time domain")) 
		self.setWindowIcon(icon_get("cover_flow"))

		self.snapshot_dirs=[]

		if path==None:
			self.snapshots_hbox = QHBoxLayout()
			self.snapshots_label= QLabel("Snapshots")
			self.snapshots_hbox.addWidget(self.snapshots_label)
			self.snapshots_combobox=QComboBox()
			self.snapshots_hbox.addWidget(self.snapshots_combobox)
			self.snapshots_widget=QWidget()
			self.snapshot_dirs=self.find_snapshots()
			for i in range(0,len(self.snapshot_dirs)):
				self.snapshots_combobox.addItem(self.snapshot_dirs[i])
			self.snapshots_combobox.currentIndexChanged.connect(self.callback_snapshots_combobox)
			self.snapshots_widget.setLayout(self.snapshots_hbox)

		else:
			self.snapshot_dirs.append(path)

		self.main_vbox = QVBoxLayout()

		self.slider=snapshot_slider()


		if len(self.snapshot_dirs)!=0:
			self.slider.set_path(os.path.join(get_sim_path(),self.snapshot_dirs[0]))


		self.slider.changed.connect(self.update)
		self.plot=plot_widget()
		self.plot.init()



		self.tb_video = QAction(icon_get("video"), _("Save video"), self)
		self.tb_video.triggered.connect(self.callback_save)
		self.plot.plot_ribbon.file_toolbar.addAction(self.tb_video)
		self.plot.plot_ribbon.plot_toolbar.addAction(self.slider.tb_play)

		self.main_vbox.addWidget(self.plot)

		if self.snapshots_widget!=None:
			self.main_vbox.addWidget(self.snapshots_widget)
		
		self.main_vbox.addWidget(self.slider)

		self.setLayout(self.main_vbox)

		if os.path.isfile(os.path.join(get_sim_path(),"snapshots","0","Ec.dat"))==False:
			help_window().help_append(["warning.png",_("No electrical slice data has been stored in the snapshots directory.  To turn this on set Simulation->Configure->Dump->Dump 1D Slices to on.  This will dump a lot of data and slow down your simulations.")])
		
		#self.light.currentIndexChanged.connect(self.call_back_light_changed)
		self.update()

	def closeEvent(self, event):
		self.slider.anim_stop()
		event.accept()

