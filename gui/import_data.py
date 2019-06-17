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

## @package import_data
#  Import data window.
#


import os
from tab import tab_class
from icon_lib import icon_get

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QSpinBox,QToolBar,QSizePolicy,QAction,QTabWidget,QTextEdit,QComboBox,QLabel,QLineEdit,QDialog,QCheckBox
from PyQt5.QtGui import QPainter,QIcon

#python modules
import webbrowser

#windows
from tab import tab_class
from tab_lang import language_tab_class

from PyQt5.QtCore import pyqtSignal

from open_save_dlg import open_as_filter

from plot_io import plot_load_info
from dat_file import dat_file


from PyQt5.QtCore import pyqtSignal

from window_list import resize_window_to_be_sane
from mesh import mesh_get_xlen
from mesh import mesh_get_zlen

from QWidgetSavePos import QWidgetSavePos
from dat_file import dat_file_import_filter

from util import wrap_text
from plot_gen import plot_gen
from cal_path import get_sim_path
from inp import inp_save
from inp import inp_load_file
from inp import inp_get_token_value_from_list

from ribbon_import import ribbon_import

from util import str2bool

articles = []
mesh_articles = []


class import_data(QDialog):

	changed = pyqtSignal()

	def populate_boxes(self):
		self.x_label=self.items[self.x_combo.currentIndex()][2]
		self.x_units=self.items[self.x_combo.currentIndex()][3]
		self.x_mul_to_si=self.items[self.x_combo.currentIndex()][4]
		self.x_disp_mul=self.items[self.x_combo.currentIndex()][5]

		self.data_label=self.items[self.data_combo.currentIndex()][2]
		self.data_units=self.items[self.data_combo.currentIndex()][3]
		self.data_mul_to_si=self.items[self.data_combo.currentIndex()][4]
		self.data_disp_mul=self.items[self.data_combo.currentIndex()][5]

		self.set_xlabel(self.items[self.x_combo.currentIndex()][2])
		self.set_data_label(self.items[self.data_combo.currentIndex()][2])
		self.set_title(self.items[self.x_combo.currentIndex()][2]+" - "+self.items[self.data_combo.currentIndex()][2])

		if self.items[self.data_combo.currentIndex()][6]==True or self.items[self.x_combo.currentIndex()][6]==True:
			self.area_widget.show()
		else:
			self.area_widget.hide()

	def add_units(self,box):
		for i in range(0,len(self.items)):
			box.addItem(self.items[i][0]+" ("+self.items[i][1]+")")

	def callback_edited(self):
		self.populate_boxes()
		self.save_config()
		self.update()

	def get_area(self):
		try:
			val=float(self.area_entry.text())/100/100
			if val==0:
				val=1.0
		except:
			val=1.0
		return val

	def save_config(self):
		lines=[]
		lines.append("#import_file_path")
		lines.append(self.file_name)
		lines.append("#import_x_combo_pos")
		lines.append(str(self.x_combo.currentIndex()))
		lines.append("#import_data_combo_pos")
		lines.append(str(self.data_combo.currentIndex()))
		lines.append("#import_x_spin")
		lines.append(str(self.x_spin.value()))
		lines.append("#import_data_spin")
		lines.append(str(self.data_spin.value()))
		lines.append("#import_title")
		lines.append(self.title_entry.text())
		lines.append("#import_xlabel")
		lines.append(self.xlabel_entry.text())
		lines.append("#import_data_label")
		lines.append(self.data_label_entry.text())
		lines.append("#import_area")
		lines.append(self.area_entry.text())
		lines.append("#import_data_invert")
		lines.append(str(self.data_invert.isChecked()))
		lines.append("#import_x_invert")
		lines.append(str(self.x_invert.isChecked()))

		lines.append("#ver")
		lines.append("#1.0")
		lines.append("#end")
		inp_save(self.config_file_path,lines)

	def load_config(self):
		lines=[]
		lines=inp_load_file(self.config_file_path)
		if lines!=False:
			self.file_name=inp_get_token_value_from_list(lines,"#import_file_path")
			if os.path.isfile(self.file_name)==False:
				return False
			self.x_combo.setCurrentIndex(int(inp_get_token_value_from_list(lines,"#import_x_combo_pos")))
			self.data_combo.setCurrentIndex(int(inp_get_token_value_from_list(lines,"#import_data_combo_pos")))
			
			self.title_entry.setText(inp_get_token_value_from_list(lines,"#import_title"))
			self.xlabel_entry.setText(inp_get_token_value_from_list(lines,"#import_xlabel"))
			self.data_label_entry.setText(inp_get_token_value_from_list(lines,"#import_data_label"))
			self.area_entry.setText(inp_get_token_value_from_list(lines,"#import_area"))

			self.x_spin.setValue(int(inp_get_token_value_from_list(lines,"#import_x_spin")))
			self.data_spin.setValue(int(inp_get_token_value_from_list(lines,"#import_data_spin")))

			self.x_invert.setChecked(str2bool(inp_get_token_value_from_list(lines,"#import_x_invert")))
			self.data_invert.setChecked(str2bool(inp_get_token_value_from_list(lines,"#import_data_invert")))

			return True
		else:
			return False
		
	def set_xlabel(self,text):
		self.xlabel_entry.blockSignals(True)
		self.xlabel_entry.setText(text)
		self.xlabel_entry.blockSignals(False)

	def set_data_label(self,text):
		self.data_label_entry.blockSignals(True)
		self.data_label_entry.setText(text)
		self.data_label_entry.blockSignals(False)

	def set_title(self,text):
		self.title_entry.blockSignals(True)
		self.title_entry.setText(text)
		self.title_entry.blockSignals(False)

	def enable_units(self,val):
		self.x_combo.setEnabled(val)
		self.data_combo.setEnabled(val)

	def get_title(self):
		return self.title_entry.text()

	def get_xlabel(self):
		return self.xlabel_entry.text()

	def get_data_label(self):
		return self.data_label_entry.text()
	
	def callback_tab_changed(self):
		self.update()

	def __init__(self,out_file,config_file):
		QDialog.__init__(self)
		self.out_file=out_file
		self.config_file_path=config_file
		self.path=os.path.dirname(self.out_file)
		self.file_name=None
		resize_window_to_be_sane(self,0.6,0.7)
		self.data=dat_file()

		#self.setFixedSize(900, 600)
		self.setWindowIcon(icon_get("import"))

		self.setWindowTitle(_("Import data")+" (https://www.gpvdm.com)") 

		self.main_vbox = QVBoxLayout()
	
		self.ribbon=ribbon_import()
		
		self.ribbon.open_data.triggered.connect(self.callback_open)

		self.ribbon.import_data.triggered.connect(self.callback_import)

		self.ribbon.plot.triggered.connect(self.callback_plot)
				
		self.ribbon.tb_help.triggered.connect(self.callback_help)

		self.main_vbox.addWidget(self.ribbon)
		
		self.input_output_hbox=QHBoxLayout()

		self.raw_data_widget=QWidget()
		self.raw_data_hbox=QVBoxLayout()
		self.raw_data_widget.setLayout(self.raw_data_hbox)
		self.raw_data = QTextEdit(self)
		self.raw_data.setReadOnly(True)
		self.raw_data.setLineWrapMode(QTextEdit.NoWrap)
		font = self.raw_data.font()
		font.setFamily("Courier")
		font.setPointSize(10)
		self.raw_data_label=QLabel(_("The file to import:"))
		self.raw_data_hbox.addWidget(self.raw_data_label)
		self.raw_data_hbox.addWidget(self.raw_data)
		self.raw_data_path=QLabel()
		self.raw_data_hbox.addWidget(self.raw_data_path)

		self.out_data_widget=QWidget()
		self.out_data_hbox=QVBoxLayout()
		self.out_data_widget.setLayout(self.out_data_hbox)
		self.out_data = QTextEdit(self)
		self.out_data.setReadOnly(True)
		self.out_data.setLineWrapMode(QTextEdit.NoWrap)
		font = self.out_data.font()
		font.setFamily("Courier")
		font.setPointSize(10)
		self.out_data_label=QLabel(_("The imported file, the numbers should now be in SI units"))
		self.out_data_hbox.addWidget(self.out_data_label)

		self.out_data_hbox.addWidget(self.out_data)

		self.out_data_path=QLabel()
		self.out_data_hbox.addWidget(self.out_data_path)
		
		self.input_output_hbox.addWidget(self.raw_data_widget)
		self.input_output_hbox.addWidget(self.out_data_widget)
		self.input_output_widget=QWidget()
		self.input_output_widget.setLayout(self.input_output_hbox)

		###################
		self.build_top_widget()
		###################

		self.main_vbox.addWidget(self.top_widget)
		self.main_vbox.addWidget(self.input_output_widget)		
		self.input_output_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.setLayout(self.main_vbox)

		self.out_data_path.setText(self.out_file)
		if self.load_config()==False:
			self.open_file()
		self.load_file()
		self.update()

	def callback_help(self,widget):
		webbrowser.open('https://www.gpvdm.com/man/index.html')

	def build_top_widget(self):
		self.items=[]
		#input description+units	//output label // Output unit// equation to si //mull si to display //Need area
		self.items.append([_("Wavelength"),"nm",_("Wavelength"),"nm","1e-9",1e9,False])
		self.items.append([_("Wavelength"),"um",_("Wavelength"),"nm","1e-6",1e9,False])
		self.items.append([_("Wavelength"),"cm",_("Wavelength"),"nm","1e-3",1e9,False])
		self.items.append([_("Wavelength"),"m",_("Wavelength"),"nm","1.0",1e9,False])
		self.items.append([_("J"),"mA/cm2",_("J"),"A/m2","10000.0/1000.0",1.0,False])
		self.items.append([_("J"),"A/m2",_("J"),"A/m2","1.0",1.0,False])
		self.items.append([_("Amps"),"A",_("J"),"A/m2","1.0/(self.get_area())",1.0,True])
		self.items.append([_("Voltage"),"V",_("Voltage"),"V","1.0",1.0,False])
		self.items.append([_("-Voltage"),"V",_("Voltage"),"V","-1.0",1.0,False])
		self.items.append([_("Voltage"),"mV",_("Voltage"),"V","1e-3",1.0,False])


		self.items.append([_("Refractive index"),"au",_("Refractive index"),"au","1.0",1.0,False])
		self.items.append([_("Absorption"),"m^{-1}",_("Absorption"),"m^{-1}","1.0",1.0,False])
		self.items.append([_("Absorption"),"m^{-cm}",_("Absorption"),"m^{-1}","1.0",1e2,False])
		self.items.append([_("Attenuation coefficient"),"au",_("Absorption"),"m^{-1}","4*3.14159/y",1.0,False])

		self.items.append([_("Time"),"s",_("Time"),"s","1.0",1.0,False])
		self.items.append([_("Suns"),"Suns",_("Suns"),"Suns","1.0",1.0,False])

		self.items.append([_("Intensity"),"um^{-1}.Wm^{-2}",_("Intensity"),"m^{-1}.Wm^{-2}","1e6",1.0,False])
		self.items.append([_("Charge density"),"m^{-3}",_("Charge density"),"m^{-3}","1.0",1.0,False])
		
		i=0
		self.x_label=self.items[i][2]
		self.x_units=self.items[i][3]
		self.x_mul_to_si=self.items[i][4]
		self.x_disp_mul=self.items[i][5]

		self.data_label=self.items[i][2]
		self.data_units=self.items[i][3]
		self.data_mul_to_si=self.items[i][4]
		self.data_disp_mul=self.items[i][5]

		self.top_widget=QWidget()
		self.top_vbox=QVBoxLayout()
		self.x_combo=QComboBox()
		self.add_units(self.x_combo)
		self.data_combo=QComboBox()
		self.add_units(self.data_combo)
		
		self.units_x_label=QLabel(_("x units:"))
		self.units_data_label=QLabel(_("y units:"))
		

		self.x_combo.currentIndexChanged.connect(self.callback_edited)
		self.data_combo.currentIndexChanged.connect(self.callback_edited)

		self.title_widget=QWidget()
		self.title_hbox=QHBoxLayout()
		self.title_label=QLabel(_("Title:"))
		self.title_entry=QLineEdit()
		self.title_hbox.addWidget(self.title_label)
		self.title_hbox.addWidget(self.title_entry)
		self.title_widget.setLayout(self.title_hbox)
		self.top_vbox.addWidget(self.title_widget)



		self.xlabel_widget=QWidget()
		self.xlabel_hbox=QHBoxLayout()
		self.xlabel_label=QLabel(_("x-label:"))
		self.xlabel_entry=QLineEdit()
		self.x_column_label=QLabel(_("x-column:"))
		self.x_spin=QSpinBox()
		self.x_spin.setValue(0)
		self.x_spin.valueChanged.connect(self.callback_edited)

		self.x_invert=QCheckBox("invert")
		
		self.xlabel_hbox.addWidget(self.xlabel_label)
		self.xlabel_hbox.addWidget(self.xlabel_entry)
		self.xlabel_hbox.addWidget(self.x_column_label)
		self.xlabel_hbox.addWidget(self.x_spin)
		self.xlabel_hbox.addWidget(self.units_x_label)
		self.xlabel_hbox.addWidget(self.x_combo)
		self.xlabel_hbox.addWidget(self.x_invert)
		self.xlabel_widget.setLayout(self.xlabel_hbox)
		self.top_vbox.addWidget(self.xlabel_widget)

		self.data_label_widget=QWidget()
		self.data_label_hbox=QHBoxLayout()
		self.data_label_label=QLabel(_("y-label:"))
		self.data_label_entry=QLineEdit()
		self.data_column_label=QLabel(_("y-column:"))
		self.data_spin=QSpinBox()
		self.data_spin.setValue(1)
		self.data_spin.valueChanged.connect(self.callback_edited)

		self.data_invert=QCheckBox("invert")

		self.data_label_hbox.addWidget(self.data_label_label)
		self.data_label_hbox.addWidget(self.data_label_entry)
		self.data_label_hbox.addWidget(self.data_column_label)
		self.data_label_hbox.addWidget(self.data_spin)
		self.data_label_hbox.addWidget(self.units_data_label)
		self.data_label_hbox.addWidget(self.data_combo)
		self.data_label_hbox.addWidget(self.data_invert)
		self.data_label_widget.setLayout(self.data_label_hbox)
		self.top_vbox.addWidget(self.data_label_widget)

		self.area_widget=QWidget()
		self.area_hbox=QHBoxLayout()
		self.area_label=QLabel(_("device area:"))
		self.area_hbox.addWidget(self.area_label)
		self.area_entry=QLineEdit()
		self.area_entry.setText(str(round(mesh_get_xlen()*mesh_get_zlen()*100*100, 3)))
		self.area_hbox.addWidget(self.area_entry)
		self.area_units=QLabel("cm2")
		self.area_hbox.addWidget(self.area_units)
		self.area_widget.setLayout(self.area_hbox)
		self.top_vbox.addWidget(self.area_widget)

		self.area_widget.hide()
		
		self.xlabel_entry.textEdited.connect(self.callback_edited)
		self.data_label_entry.textEdited.connect(self.callback_edited)
		self.title_entry.textEdited.connect(self.callback_edited)
		self.area_entry.textEdited.connect(self.callback_edited)
		self.x_invert.stateChanged.connect(self.callback_edited)
		self.data_invert.stateChanged.connect(self.callback_edited)
		self.top_widget.setLayout(self.top_vbox)

	def gen_output(self):
		text="\n".join(self.data.gen_output_data())
		self.out_data.setText(text)

	def update(self):
		ret=dat_file_import_filter(self.data,self.file_name,x_col=self.x_spin.value(),y_col=self.data_spin.value())
		if ret==True:
			self.populate_boxes()
		else:
			return False

		self.data.title=self.get_title()

		self.data.y_label=self.get_xlabel()
		self.data.data_label=self.get_data_label()

		self.data.y_units=self.x_units
		self.data.data_units=self.data_units
		
		self.data.y_mul=self.x_disp_mul
		self.data.data_mul=self.data_disp_mul

		self.data.x_len=self.data.x_len
		self.data.y_len=self.data.y_len
		self.data.z_len=self.data.z_len


		#rescale the data
		for i in range(0,self.data.y_len):
			y=0
			y_command="self.data.y_scale[i]*"+self.x_mul_to_si
			y=eval(y_command)

			data_command="self.data.data[0][0][i]*"+self.data_mul_to_si
			data=eval(data_command)

			if self.x_invert.isChecked() == True:
				y=y*-1

			if self.data_invert.isChecked() == True:
				data=data*-1

			self.data.data[0][0][i]=data
			self.data.y_scale[i]=y

			#y_all.append(y)
			#data_all.append(data)

		self.data.y_scale, self.data.data[0][0] = zip(*sorted(zip(self.data.y_scale, self.data.data[0][0])))

		self.gen_output()

	def callback_plot(self):
		file_name=os.path.join(get_sim_path(),"temp.dat")
		a = open(file_name, "w")
		a.write(self.out_data.toPlainText())
		a.close()
		plot_gen([file_name],[],"auto")
		
	def callback_import(self):
		a = open(self.out_file, "w")
		a.write(self.out_data.toPlainText())
		a.close()
		self.accept()

	def open_file(self):
		self.file_name=open_as_filter(self,"dat (*.dat);;csv (*.csv);;txt (*.txt);;tdf (*.tdf)",path=self.path)

		if self.file_name!=None:
			self.load_file()
			
	def load_file(self):
		if self.file_name!=None:
			if os.path.isfile(self.file_name)==True:
				f = open(self.file_name, "r")
				lines = f.readlines()
				f.close()
				text=""
				for l in range(0, len(lines)):
					text=text+lines[l].rstrip()+"\n"
				self.raw_data_path.setText(self.file_name)
				self.raw_data.setText(text)

				#got_info=plot_load_info(self.info_token,self.file_name)
				self.ribbon.import_data.setEnabled(True)
				self.ribbon.plot.setEnabled(True)



	def callback_open(self):
		self.open_file()

	def run(self):
		self.exec_()
