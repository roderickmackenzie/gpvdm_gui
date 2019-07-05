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

## @package plot_widget
#  The main plot widget.
#

from __future__ import unicode_literals

import os
import io
from numpy import *
from plot_io import plot_load_info
from plot_export import plot_export


#matplotlib
import matplotlib
from matplotlib import cm
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.pyplot import colorbar
from matplotlib.colors import LogNorm

from util import numbers_to_latex
from util import pygtk_to_latex_subscript
from util import fx_with_units
from util import time_with_units

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QTableWidget,QAbstractItemView, QMenuBar,QApplication
from PyQt5.QtGui import QPainter,QIcon,QImage

#calpath
from icon_lib import icon_get
from open_save_dlg import save_as_image
from open_save_dlg import save_as_filter

from dat_file_math import dat_file_max_min
from dat_file_math import dat_file_sub
from dat_file_math import dat_file_mul
from dat_file_math import dat_file_sub_float
from dat_file import dat_file
from dat_file import read_data_2d


from dlg_get_multi_text import dlg_get_multi_text

from mpl_toolkits.mplot3d import Axes3D

from colors import get_color
from colors import get_color_black
from colors import get_marker

from dat_file import dat_file_print
from plot_ribbon import plot_ribbon
from lock import get_lock

class plot_widget(QWidget):

	def keyPressEvent(self, event):
		keyname=event.key()
		if (keyname>64 and keyname<91 ) or (keyname>96 and keyname<123):
			modifiers = event.modifiers()
			keyname=chr(keyname)
			if keyname.isalpha()==True:
				if Qt.ShiftModifier == modifiers:
					keyname=keyname.upper()
				else:
					keyname=keyname.lower()
		else:
			return


		if keyname=="a":
			self.do_plot()
		elif keyname=="q":
			self.destroy()
		elif  modifiers == Qt.ControlModifier and keyname=='c':
			if get_lock().is_trial()==False:
				self.callback_do_clip()

		if len(self.data)>0:
			if keyname=='g':
				if self.data[0].grid==False:
					for i in range(0,len(self.ax)):
						self.ax[i].grid(True)
					self.data[0].grid=True
				else:
					for i in range(0,len(self.ax)):
						self.ax[i].grid(False)
					self.data[0].grid=False
			elif keyname=="r":
				if self.lx==None:
					for i in range(0,len(self.ax)):
						self.lx = self.ax[i].axhline(color='k')
						self.ly = self.ax[i].axvline(color='k')
				self.lx.set_ydata(self.ydata)
				self.ly.set_xdata(self.xdata)

			elif keyname=="l":
				if self.data[0].logdata==True:
					self.data[0].logdata=False
					for i in range(0,len(self.ax)):
						self.ax[i].set_yscale("linear")
				else:
					self.data[0].logdata=True
					for i in range(0,len(self.ax)):
						self.ax[i].set_yscale("log")

			elif keyname=="L":
				if self.data[0].logy==True:
					self.data[0].logy=False
					for i in range(0,len(self.ax)):
						self.ax[i].set_xscale("linear")
				else:
					self.data[0].logy=True
					for i in range(0,len(self.ax)):
						self.ax[i].set_xscale("log")


			self.fig.canvas.draw()

	def callback_do_clip(self):
		buf = io.BytesIO()
		self.fig.savefig(buf)
		QApplication.clipboard().setImage(QImage.fromData(buf.getvalue()))
		buf.close()


	def mouse_move(self,event):
		self.xdata=event.xdata
		self.ydata=event.ydata



	def do_plot(self):
		if len(self.data)==0:
			return
		
		if self.data[0].valid_data==False:
			return

		self.fig.clf()
		self.fig.subplots_adjust(bottom=0.2)
		self.fig.subplots_adjust(bottom=0.2)
		self.fig.subplots_adjust(left=0.1)
		self.fig.subplots_adjust(hspace = .001)
		dim=""
		if self.data[0].x_len==1 and self.data[0].z_len==1:
			dim="linegraph"
		elif self.data[0].x_len>1 and self.data[0].y_len>1 and self.data[0].z_len==1:
			if self.data[0].type=="3d":
				dim="wireframe"
			if self.data[0].type=="heat":
				dim="heat"
		elif self.data[0].x_len>1 and self.data[0].y_len>1 and self.data[0].z_len>1:
			print("ohhh full 3D")
			dim="3d"
		else:
			print(_("I don't know how to process this type of file!"),self.data[0].x_len, self.data[0].y_len,self.data[0].z_len)
			return

		if self.hide_title==False:
			title=self.data[0].title
			if self.data[0].time!=-1.0 and self.data[0].Vexternal!=-1.0:
				mul,unit=time_with_units(self.data[0].time)
				title=self.data[0].title+" V="+str(self.data[0].Vexternal)+" "+_("time")+"="+str(self.data[0].time*mul)+" "+unit

			self.fig.suptitle(title)

			self.setWindowTitle(title+" - www.gpvdm.com")

		self.ax=[]


		for i in range(0,len(self.input_files)):
			if dim=="linegraph":
				self.ax.append(self.fig.add_subplot(111,facecolor='white'))
			elif dim=="wireframe":
				self.ax.append(self.fig.add_subplot(111,facecolor='white' ,projection='3d'))
			elif dim=="heat":
				self.ax.append(self.fig.add_subplot(111,facecolor='white'))
			elif dim=="3d":
				self.ax.append(self.fig.add_subplot(111,facecolor='white' ,projection='3d'))
			#Only place label on bottom plot
			#	if self.data[i].type=="3d":
			#else:
			#	self.ax[i].tick_params(axis='x', which='both', bottom='off', top='off',labelbottom='off') # labels along the bottom edge are off

			#Only place y label on center plot
			if self.data[0].normalize==True or self.data[0].norm_to_peak_of_all_data==True:
				y_text="Normalized "+self.data[0].data_label
				data_units="au"
			else:
				data_text=self.data[i].data_label
				data_units=self.data[i].data_units

			if self.data[0].logy==True:
				self.ax[i].set_xscale("log")

			print(">>>>>>>>",self.data[0].logdata)
			if self.data[0].logdata==True:
				self.ax[i].set_yscale("log")


		all_plots=[]
		files=[]
		my_max=1.0

		if dim=="linegraph":		#This is for the 1D graph case
			self.ax[0].set_xlabel(self.data[0].y_label+" ("+str(self.data[0].y_units)+")")
			self.ax[0].set_ylabel(self.data[0].data_label+" ("+self.data[0].data_units+")")

			for i in range(0,len(self.input_files)):
				cur_plot, = self.ax[i].plot(self.data[i].y_scale,self.data[i].data[0][0], linewidth=3 ,alpha=1.0,color=get_color(i),marker=get_marker(i))

				if self.labels[i]!="":
					files.append("$"+numbers_to_latex(str(self.labels[i]))+" "+pygtk_to_latex_subscript(self.data[0].key_units)+"$")

				all_plots.append(cur_plot)
				
				if len(self.data[i].labels)!=0:
					#we only want this many data labels or it gets crowded
					max_points=12
					n_points=range(0,len(self.data[i].y_scale))
					if len(n_points)>max_points:
						step=int(len(n_points)/max_points)
						n_points=[]
						pos=0
						while(len(n_points)<max_points):
							n_points.append(pos)
							pos=pos+step

					for ii in n_points:
						label_text=self.data[i].labels[ii]
						self.ax[i].annotate(label_text,xy = (self.data[i].y_scale[ii], self.data[i].data[0][0][ii]), xytext = (-20, 20),textcoords = 'offset points', ha = 'right', va = 'bottom',bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))


				#print(self.data[i].labels)
		elif dim=="wireframe":
			self.ax[0].set_xlabel(self.data[0].x_label+" ("+self.data[0].x_units+")")
			self.ax[0].set_ylabel(self.data[0].y_label+" ("+self.data[0].y_units+")")
			my_max,my_min=dat_file_max_min(self.data[0])
			for i in range(0,len(self.input_files)):

				#new_data=[[float for y in range(self.data[0].y_len)] for x in range(self.data[0].x_len)]
				#for x in range(0,self.data[i].x_len):
				#	for y in range(0,self.data[i].y_len):
				#		print(x,y,len(self.data[i].data[0]),len(self.data[i].data[0][0]))
				#		new_data[x][y]=self.data[i].data[0][x][y]
				#z = 10 * outer(ones(size(data.x_scale)), cos(data.y_scale))
				#im=self.ax[0].plot_surface(data.x_scale,data.y_scale,z)
				#print(new_data)
				#print(self.data[i].x_scale)
				#print(self.data[i].y_scale)
				X, Y = meshgrid( self.data[i].y_scale,self.data[i].x_scale)
				Z = self.data[i].data[0]

				# Plot the surface
				self.ax[i].set_zlim(my_min, my_max)
				im=self.ax[i].plot_wireframe( Y,X, Z)

				#pcolor
		elif dim=="heat":
			self.ax[0].set_xlabel(self.data[0].x_label+" ("+self.data[0].x_units+")")
			self.ax[0].set_ylabel(self.data[0].y_label+" ("+self.data[0].y_units+")")
			my_max,my_min=dat_file_max_min(self.data[0])
			for i in range(0,len(self.input_files)):
				if self.data[i].logdata==True:
					if my_min==0:
						my_min=1.0
					im=self.ax[0].pcolor(self.data[i].y_scale,self.data[i].x_scale,self.data[i].data[0], norm=LogNorm(vmin=my_min, vmax=my_max), vmin=my_min, vmax=my_max,cmap="gnuplot")
				else:
					im=self.ax[0].pcolor(self.data[i].y_scale,self.data[i].x_scale,self.data[i].data[0], vmin=my_min, vmax=my_max,cmap="gnuplot")

				self.fig.colorbar(im)

				#pcolor

				#self.fig.colorbar(im, shrink=0.5, aspect=5)
				#self.ax[0].plot_surface(x, y, z, rstride=1, cstride=1, cmap=cm.coolwarm,linewidth=0, antialiased=False)
				#self.ax[0].invert_yaxis()
				#self.ax[0].xaxis.tick_top()
		elif dim=="3d":
			self.ax[0].set_xlabel(self.data[0].x_label+" ("+self.data[0].x_units+")")
			self.ax[0].set_ylabel(self.data[0].y_label+" ("+self.data[0].y_units+")")
			self.ax[0].set_zlabel(self.data[0].z_label+" ("+self.data[0].z_units+")")

			for ii in range(0,len(self.data[i].z_scale)):
				my_max,my_min=dat_file_max_min(self.data[i])
				X, Y = meshgrid( self.data[i].x_scale,self.data[i].y_scale)
				new_data=[[float for y in range(self.data[0].y_len)] for x in range(self.data[0].x_len)]
				for x in range(0,self.data[i].x_len):
					for y in range(0,self.data[i].y_len):
						new_data[x][y]=self.data[i].z_scale[ii]+self.data[i].data[ii][x][y]
				print("max=",my_max)
				self.ax[i].contourf(X, Y, new_data, zdir='z')#

				self.ax[i].set_xlim3d(0, self.data[i].x_scale[-1])
				self.ax[i].set_ylim3d(0, self.data[i].y_scale[-1])
				self.ax[i].set_zlim3d(0, self.data[i].z_scale[-1])

		#setup the key
		if self.data[0].legend_pos=="No key":
			self.ax[i].legend_ = None
		else:
			if len(files)<40:
				self.fig.legend(all_plots, files, self.data[0].legend_pos)

		if get_lock().is_trial()==True:
			x=0
			y=0
			while(x<1.0):
				y=0
				while(y<1.0):
					self.fig.text(x, y, 'gpvdm', fontsize=20, color='gray', ha='right', va='bottom', alpha=self.watermark_alpha)

					y=y+0.1
				x=x+0.15
			#self.fig.text(0.90, 0.1, 'Upgrade to gpvdm proessional today!', fontsize=20, color='blue', ha='right', va='bottom', alpha=0.2)
			#self.fig.text(0.40, 0.80, 'Upgrade to gpvdm proessional.', fontsize=20, color='gray', ha='right', va='bottom', alpha=self.watermark_alpha)
			#self.fig.text(0.40, 0.20, 'Upgrade to gpvdm proessional.', fontsize=20, color='gray', ha='right', va='bottom', alpha=self.watermark_alpha)

		#self.fig.tight_layout(pad=0.0, w_pad=0.0, h_pad=0.0,axes_pad=0.0)
		self.fig.canvas.draw()
		#print("exit do plot")

	def save_imaeg(self):
		self.callback_save_image()

	def callback_save_image(self):
		file_name=save_as_image(self)
		if file_name != None:
			self.fig.savefig(file_name)

	def callback_save_csv(self):
		file_name=save_as_filter(self,"*.csv")
		if file_name != None:
			self.data[0].save_as_csv(file_name)

	def callback_save_txt(self):
		file_name=save_as_filter(self,"*.txt")
		if file_name != None:
			self.data[0].save_as_txt(file_name)

	def set_labels(self,labels):
		self.labels=labels

	def reload(self):
		self.data=[]

		
		for i in range(0,len(self.input_files)):
			dat=dat_file()
			ret=dat.load(self.input_files[i])
			self.data.append(dat)


		self.norm_data()

	def load_data(self,input_files):
		self.lx=None
		self.ly=None
		self.input_files=input_files

		if len(input_files)==0:
			print(_("No files were given to load"))
			return

		self.reload()



	def norm_data(self):
		if len(self.data)>0:
			if self.zero_frame_enable==True:
				if len(self.input_files)>1:
					for i in range(1,len(self.input_files)):
						dat_file_sub(self.data[i],self.data[0])
					
					dat_file_sub(self.data[0],self.data[0])
			for i in range(0,len(self.data)):
				for x in range(0,self.data[i].x_len):
					self.data[i].x_scale[x]=self.data[i].x_scale[x]*self.data[i].x_mul

				for y in range(0,self.data[i].y_len):
					self.data[i].y_scale[y]=self.data[i].y_scale[y]*self.data[i].y_mul

				for z in range(0,self.data[i].z_len):
					self.data[i].z_scale[z]=self.data[i].z_scale[z]*self.data[i].z_mul

				for x in range(0,self.data[i].x_len):
					for y in range(0,self.data[i].y_len):
						for z in range(0,self.data[i].z_len):
							self.data[i].data[z][x][y]=self.data[i].data[z][x][y]*self.data[i].data_mul

			if self.data[0].invert_y==True:
				for i in range(0,len(self.input_files)):
					dat_file_mul(self.data[i],-1)

			if self.data[0].subtract_first_point==True:
				val=self.data[0].data[0][0][0]
				for i in range(0,len(self.input_files)):
					dat_file_sub_float(self.data[i],val)


			if self.data[0].add_min==True:
				my_max,my_min=dat_file_max_min(self.data[0])
				for i in range(0,len(self.input_files)):
					dat_file_sub_float(self.data[i],my_min)


						
						#if data.data[z][x][y]!=0:
			#if self.plot_token.normalize==True:
				#my_max,my_min=dat_file_max_min(self.data[0])
				#for (i in range(0,len(self.input_files)):

								#data.data[z][x][y]=data.data[z][x][y]/my_max
							#else:
								#data.data[z][x][y]=0.0


			#if self.plot_token.ymax!=-1:
				#self.ax[index].set_ylim((self.plot_token.ymin,self.plot_token.ymax))
			#return True
		#else:
			#return False
	
##norm stuff
			#all_max=1.0
			#if self.plot_token.norm_to_peak_of_all_data==True:
				#my_max=-1e40
				#for i in range(0, len(self.input_files)):
					#local_max,my_min=dat_file_max_min(self.data[i])
					#if local_max>my_max:
						#my_max=local_max
				#all_max=my_max

			#for i in range(0, len(self.input_files)):
				#if all_max!=1.0:
					#for x in range(0,data.x_len):
						#for y in range(0,data.y_len):
							#for z in range(0,data.z_len):
								#data.data[z][x][y]=data.data[z][x][y]/all_max



	def callback_black(self):
		if len(self.data)>0:
			self.do_plot()

	def callback_rainbow(self):
		if len(self.data)>0:
			self.do_plot()


	def callback_key(self):
		if len(self.data)>0:
			self.data[0].legend_pos=widget.get_label()
			self.do_plot()

	def callback_units(self):
		if len(self.data)>0:
			units=dlg_get_text( "Units:", self.data[0].key_units)
			if units!=None:
				self.data[0].key_units=units
			self.do_plot()


	def callback_autoscale_y(self):
		if len(self.data)>0:
			if self.data[0].ymax==-1:
				xmin, xmax, ymin, ymax = self.ax[0].axis()
				self.data[0].ymax=ymax
				self.data[0].ymin=ymin
			else:
				self.data[0].ymax=-1
				self.data[0].ymin=-1

	def callback_normtoone_y(self):
		if len(self.data)>0:
			self.data[0].normalize= not self.data[0].normalize
			self.norm_data()
			self.do_plot()

	def callback_norm_to_peak_of_all_data(self):
		if len(self.data)>0:
			self.data[0].norm_to_peak_of_all_data=not self.data[0].norm_to_peak_of_all_data
			self.norm_data()
			self.do_plot()

	def callback_toggle_log_scale_y(self):
		if len(self.data)>0:
			self.data[0].logy=not self.data[0].logy
			self.norm_data()
			self.do_plot()

	def callback_toggle_log_scale_x(self):
		if len(self.data)>0:
			self.data[0].logx=not self.data[0].logx
			self.norm_data()
			self.do_plot()

	def callback_toggle_label_data(self):
		if len(self.data)>0:
			self.data[0].label_data=not self.data[0].label_data
			self.do_plot()

	def callback_set_heat_map(self):
		if len(self.data)>0:
			self.data[0].type="heat"
			self.do_plot()

	def callback_heat_map_edit(self):
		ret = dlg_get_multi_text([["x start",str(self.data[0].x_start)],["x stop",str(self.data[0].x_stop)],["x points",str(self.data[0].x_points)],["y start",str(self.data[0].y_start)],["y stop",str(self.data[0].y_stop)],["y points",str(self.data[0].y_points)]],title="2D plot editor")
		ret.run()
		ret=ret.get_values()
		if ret!=False:
			[a,b,c,d,e,f] = ret
			#print("---------",a,b,c,d,e,f)
			self.data[0].x_start=float(a)
			self.data[0].x_stop=float(b)
			self.data[0].x_points=float(c)

			self.data[0].y_start=float(d)
			self.data[0].y_stop=float(e)
			self.data[0].y_points=float(f)

			self.do_plot()


	def callback_toggle_invert_y(self):
		if len(self.data)>0:
			self.data[0].invert_y=not self.data[0].invert_y
			self.norm_data()
			self.do_plot()

	def callback_toggle_subtract_first_point(self):
		if len(self.data)>0:
			self.data[0].subtract_first_point=not self.data[0].subtract_first_point
			self.norm_data()
			self.do_plot()

	def callback_toggle_add_min(self):
		if len(self.data)>0:
			self.data[0].add_min=not self.data[0].add_min
			self.norm_data()
			self.do_plot()

	def update(self):
		self.load_data(self.input_files)
		self.do_plot()

	def callback_refresh(self):
		self.update()

	def __init__(self):
		self.watermark_alpha=0.05
		self.data=[]
		self.input_files=[]
		self.hide_title=False
		QWidget.__init__(self)
		self.setWindowIcon(icon_get("plot"))

	def init(self,enable_toolbar=True):
		self.main_vbox = QVBoxLayout()
		self.labels=[]
		self.fig = Figure(figsize=(2.5,2), dpi=100)
		self.canvas = FigureCanvas(self.fig)  # a gtk.DrawingArea

		self.zero_frame_enable=False
		self.zero_frame_list=[]


		if enable_toolbar==True:
			self.plot_ribbon=plot_ribbon()
			self.plot_ribbon.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

			self.plot_ribbon.tb_export_as_jpg.secure_click.connect(self.callback_save_image)
			self.plot_ribbon.tb_export_as_csv.secure_click.connect(self.callback_save_csv)
			self.plot_ribbon.tb_export_as_txt.secure_click.connect(self.callback_save_txt)

			self.plot_ribbon.tb_copy.secure_click.connect(self.callback_do_clip)

			#self.plot_ribbon.tb_export_as_jpg.triggered.connect(self.save_image)


			self.tb_refresh = QAction(icon_get("view-refresh"), _("Refresh graph"), self)
			self.tb_refresh .triggered.connect(self.callback_refresh)
			self.plot_ribbon.plot_toolbar.addAction(self.tb_refresh )



			nav_bar=NavigationToolbar(self.canvas,self)
			actions = nav_bar.findChildren(QAction)
			for a in actions:
				if a.text() == 'Save':
					nav_bar.removeAction(a)
					break

			nav_bar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
			nav_bar.setIconSize(QSize(42, 42))
			self.plot_ribbon.plot_toolbar.addWidget(nav_bar)

			self.fig.canvas.mpl_connect('motion_notify_event', self.mouse_move)

			self.plot_ribbon.tb_color_black.triggered.connect(self.callback_black)
			self.plot_ribbon.tb_color_rainbow.triggered.connect(self.callback_rainbow)

			self.plot_ribbon.tb_scale_autoscale.triggered.connect(self.callback_autoscale_y)
			self.plot_ribbon.tb_scale_log_y.triggered.connect(self.callback_toggle_log_scale_y)
			self.plot_ribbon.tb_scale_log_x.triggered.connect(self.callback_toggle_log_scale_x)


			self.plot_ribbon.math_subtract_first_point.triggered.connect(self.callback_toggle_subtract_first_point)
			self.plot_ribbon.math_add_min_point.triggered.connect(self.callback_toggle_add_min)
			self.plot_ribbon.math_invert_y_axis.triggered.connect(self.callback_toggle_invert_y)
			self.plot_ribbon.math_norm_y_to_one.triggered.connect(self.callback_normtoone_y)
			self.plot_ribbon.math_norm_to_peak_of_all_data.triggered.connect(self.callback_norm_to_peak_of_all_data)
			self.plot_ribbon.math_heat_map.triggered.connect(self.callback_set_heat_map)
			self.plot_ribbon.math_heat_map_edit.triggered.connect(self.callback_heat_map_edit)


			self.main_vbox.addWidget(self.plot_ribbon)


		self.canvas.figure.patch.set_facecolor("white")
		self.canvas.setMinimumSize(800, 350)
		self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.main_vbox.addWidget(self.canvas)

		self.setLayout(self.main_vbox)



