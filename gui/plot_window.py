# -*- coding: utf-8 -*-
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

## @package plot_window
#  A plot window which uses the plot widget.
#


import os
#import shutil
#from token_lib import tokens
from plot_widget import plot_widget
from PyQt5.QtWidgets import QWidget

class plot_window():
	def __init__(self):
		self.shown=False

	def destroy(self):
		self.shown=False
		self.window.destroy()

	def callback_destroy(self,widget):
		self.destroy()

	def init(self,input_files,plot_labels,config_file):
		self.shown=True

		self.plot=plot_widget()
		self.plot.init()

		print("labels",plot_labels)
		if len(plot_labels)==0:
			for i in range(0,len(input_files)):
				plot_labels.append(os.path.basename(input_files[i]).replace("_","\_"))

		#print plot_labels
		for i in range(0,len(plot_labels)):
			if len(plot_labels[i])>0:
				if plot_labels[i][0]=="\\":
					plot_labels[i]=plot_labels[i][1:]
			plot_labels[i].replace("\\","/")

		self.plot.set_labels(plot_labels)
		self.plot.load_data(input_files)

		self.plot.do_plot()
		self.plot.show()



