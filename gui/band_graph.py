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

## @package band_graph
#  Band diagram graph
#


import os
import io
import sys
from numpy import *

#matplotlib
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import zipfile
from util import lines_to_xyz
from dat_file import dat_file


from matplotlib.figure import Figure
from plot_io import get_plot_file_info

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QSystemTrayIcon,QMenu,QApplication
from PyQt5.QtGui import QIcon,QPixmap,QImage

#epitaxy
from epitaxy import epitaxy_get_layers
from epitaxy import epitaxy_get_mat_file
from epitaxy import epitaxy_get_electrical_layer
from epitaxy import epitaxy_get_width
from epitaxy import epitaxy_get_name

#inp
from inp import inp_load_file
from inp import inp_search_token_value
from inp import inp_get_token_value
#calpath
from icon_lib import icon_get

from open_save_dlg import save_as_filter
from cal_path import get_sim_path
from cal_path import get_materials_path
from cal_path import get_default_material_path

class band_graph(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		self.main_vbox = QVBoxLayout()

		self.my_figure=Figure(figsize=(5,4), dpi=100)
		self.canvas = FigureCanvas(self.my_figure)
		self.canvas.mpl_connect('key_press_event', self.press)
		self.canvas.setFocusPolicy( Qt.ClickFocus )
		self.canvas.setFocus()
		self.canvas.figure.patch.set_facecolor('white')
		#self.canvas.set_size_request(600, 400)
		self.canvas.show()

		self.main_vbox.addWidget(self.canvas)

		#self.canvas.connect('key_press_event', self.on_key_press_event)

		self.setLayout(self.main_vbox)


#	def keyPressEvent(self, event):
#		pritn("oh")
#
#		keyname = ''
#		key = event.key()
#		modifiers = int(event.modifiers())
#		if (Qt.CTRL & modifiers)==modifiers and key==67:
#			self.do_clip()
#			self.canvas.draw()

	def press(self,event):
		#print('press', event.key)
		sys.stdout.flush()
		if event.key == "ctrl+c":
			self.do_clip()


	def do_clip(self):
		buf = io.BytesIO()
		self.my_figure.savefig(buf)
		QApplication.clipboard().setImage(QImage.fromData(buf.getvalue()))
		buf.close()

	def save_image(self):
		response=save_as_filter(self,"png (*.png);;jpg (*.jpg);;svg (*.svg)")
		if response != None:
			print(response)
			self.my_figure.savefig(response)

	def set_data_file(self,file):
		self.data_file=file

	def draw_graph(self):

		self.my_figure.clf()
		self.layer_end=[]
		self.layer_name=[]
		self.optical_mode_file=os.path.join(get_sim_path(),"light_dump",self.data_file)

		self.my_figure.clf()
		ax1 = self.my_figure.add_subplot(111)
		ax2 = ax1.twinx()
		x_pos=0.0
		layer=0
		color =['r','g','b','y','o','r','g','b','y','o','r','g','b','y','o','r','g','b','y','o']
		start=0.0

		for i in range(0,epitaxy_get_layers()):
			if epitaxy_get_electrical_layer(i).startswith("dos")==False:
				start=start-epitaxy_get_width(i)
			else:
				break

		start=start*1e9

		x_pos=start
		for i in range(0,epitaxy_get_layers()):

#			label=epitaxy_get_mat_file(i)
			layer_ticknes=epitaxy_get_width(i)
			layer_material=epitaxy_get_mat_file(i)
			lumo=0.0
			homo=0.0
			
			delta=float(layer_ticknes)*1e9
			#print(epitaxy_get_electrical_layer(i))
			lines=[]
			#we could have zipped the file
			mat_file=os.path.join(get_materials_path(),layer_material,'mat.inp')
			archive=os.path.basename(os.path.dirname(mat_file))+".zip"

			material_type=inp_get_token_value(mat_file, "#material_type",archive=archive)
			unknown_lumo_eg=False

			if epitaxy_get_electrical_layer(i).startswith("dos")==False:
				dos_file=os.path.join(get_materials_path(),layer_material,'dos.inp')
				if os.path.isfile(dos_file)==False:
					unknown_lumo_eg=True
					dos_file=os.path.join(get_default_material_path(),"dos.inp")

				lines=inp_load_file(dos_file,archive=archive)
				#print("rod",lines,dos_file,material_type,os.path.join(get_materials_path(),layer_material,'mat.inp'))
				if lines!=False:
					lumo=-float(inp_search_token_value(lines, "#Xi"))
					Eg=float(inp_search_token_value(lines, "#Eg"))
			else:
				lines=inp_load_file(os.path.join(get_sim_path(),epitaxy_get_electrical_layer(i)+".inp"))
				#print(lines)
				if lines!=False:
					lumo=-float(inp_search_token_value(lines, "#Xi"))
					Eg=float(inp_search_token_value(lines, "#Eg"))
					#print("b")

			x = [x_pos,x_pos+delta,x_pos+delta,x_pos]

			#print("lumo=",lumo)
			lumo_delta=lumo-0.1

			homo=lumo-Eg
			homo_delta=homo-0.1

			draw_homo=True
			y_name_pos=lumo-Eg/2

			if Eg==0.0 or material_type=="metal":
				lumo_delta=-7.0
				draw_homo=False
				y_name_pos=lumo-1.0

			x_pos=x_pos+delta
			self.layer_end.append(x_pos)
			self.layer_name.append(layer_material)

			rot=0
			if epitaxy_get_layers()>5:
				rot=90
			item=ax2.text(x_pos-delta/1.5, y_name_pos, epitaxy_get_name(i), rotation=rot)
			item.set_fontsize(15)

			lumo_shape = [lumo,lumo,lumo_delta,lumo_delta]
			ax2.fill(x,lumo_shape, color[layer],alpha=0.4)
			if unknown_lumo_eg==False:
				item=ax2.text(x_pos-delta/1.5, lumo+0.1, "%.2f eV" % lumo)
				item.set_fontsize(15)

			if draw_homo==True:
				homo_shape = [homo,homo,homo_delta,homo_delta]
				ax2.fill(x,homo_shape, color[layer],alpha=0.4)
				if unknown_lumo_eg==False:
					item=ax2.text(x_pos-delta/1.5, lumo-Eg-0.4, "%.2f eV" % homo)
					item.set_fontsize(15)

			layer=layer+1

		state=dat_file()
		if state.load(self.optical_mode_file)==True:
			ax1.set_ylabel(state.data_label+" ("+state.data_units+")")
			ax1.set_xlabel(_("Position")+" (nm)")
			ax2.set_ylabel(_("Energy")+" (eV)")
			ax2.set_xlim([start, x_pos])
			#ax2.axis(max=)#autoscale(enable=True, axis='x', tight=None)

			for i in range(0,len(state.y_scale)):
				state.y_scale[i]=state.y_scale[i]*1e9
			
			ax1.plot(state.y_scale,state.data[0][0], 'black', linewidth=3 ,alpha=0.5)



		self.my_figure.tight_layout()

		self.canvas.draw()

