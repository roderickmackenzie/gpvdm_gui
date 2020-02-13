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

## @package ref
#  Reference manager window.
#


from icon_lib import icon_get
import os

#qt
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QTableWidget,QAbstractItemView,QPushButton
from PyQt5.QtGui import QPainter,QIcon

from window_list import resize_window_to_be_sane

#windows
from cal_path import get_ui_path

from gpvdm_select import gpvdm_select

from inp import inp
from inp import inp_get_token_array
from inp_util import inp_check_ver
from inp import inp_new_file
from inp import inp_add_token
from inp import inp_load_file
from inp import inp_save_lines_to_file
from inp import inp_get_token_value_from_list
from tab import tab_class

import webbrowser

from ref_io import ref
from ref_io import load_ref
from QWidgetSavePos import QWidgetSavePos

def get_ref_text(file_name,html=True):
	r=load_ref(file_name)
	text=""
	if r!=None:
		if html==True:
			if r.group!="":
				text="<b>"+_("Data provided by")+":</b>"+r.group+"<br>"
			text=text+"<b>"+_("Associated paper")+":</b>"+r.author+", "+r.journal+", "+r.volume+", "+r.pages+", "+r.year+"<br>"
			text=text+"<b>doi link:</b> <a href=\"http://doi.org/"+r.doi+"\"> http://doi.org/"+r.doi+"</a>"
		else:
			if r.group!="":
				text=_("Data provided by")+": "+r.group+" "
			#text=text+"Associated paper:"+author+", "+journal+", "+volume+", "+pages+", "+year

		return text
	return None

class ref_window(QWidgetSavePos):
	def __init__(self,file_name):
		"""Pass this the file name of the file you want referenced."""
		QWidgetSavePos.__init__(self,"ref_window")
		resize_window_to_be_sane(self,0.5,0.5)
		self.file_name=os.path.splitext(file_name)[0]+".ref"
		self.gen_file()
		self.setWindowIcon(icon_get("ref"))
		self.setWindowTitle(_("Reference manager")+" (https://www.gpvdm.com)")

		self.vbox=QVBoxLayout()


		self.toolbar=QToolBar()
		self.toolbar.setIconSize(QSize(48, 48))

		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.toolbar.addWidget(spacer)

		self.tb_help = QAction(icon_get("help"), _("Help"), self)
		self.tb_help.setStatusTip(_("Help"))
		self.tb_help.triggered.connect(self.callback_help)
		self.toolbar.addAction(self.tb_help)

		self.vbox.addWidget(self.toolbar)
		tab=tab_class(self.file_name)
		tab.icon_file="ref.png"
		self.vbox.addWidget(tab)

		self.button_widget=QWidget()
		self.button_hbox=QHBoxLayout()
		self.button_widget.setLayout(self.button_hbox)

		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.button_hbox.addWidget(spacer)


		self.button_close=QPushButton(_("Close"))
		self.button_close.clicked.connect(self.callback_close)
		self.button_hbox.addWidget(self.button_close)
		self.vbox.addWidget(self.button_widget)
		self.setLayout(self.vbox)

	def callback_close(self):
		self.close()

	def gen_file(self):
		make_new=True
		lines=inp_load_file(self.file_name)
		if lines!=False:
			if inp_check_ver(self.file_name, "1.0")==True:
				make_new=False

		if make_new==True:
			lines=[]
			lines.append("#ref_website")
			lines.append("")
			lines.append("#ref_research_group")
			lines.append("")
			lines.append("#ref_authors")
			lines.append("")
			lines.append("#ref_jounral")
			lines.append("")
			lines.append("#ref_title")
			lines.append("")
			lines.append("#ref_volume")
			lines.append("")
			lines.append("#ref_pages")
			lines.append("")
			lines.append("#ref_year")
			lines.append("")
			lines.append("#ref_md5")
			lines.append("")
			lines.append("#ref_doi")
			lines.append("")
			lines.append("#ref_unformatted")
			lines.append("")
			lines.append("#ver")
			lines.append("1.0")
			lines.append("#end")

			inp_save_lines_to_file(self.file_name,lines)

	def load(self):
		ret=inp_get_token_array(self.file_name, self.token)
		if ret!=False:									#We have found the file and got the token
			self.ui.text.setText("\n".join(ret))
		else:
			self.ui.text.setText(_("New file"))

			if inp_check_ver(self.file_name, "1.0")==True:	#The file exists but there is no token.
				lines=[]
				lines=inp_load_file(self.file_name)
				lines=inp_add_token(lines,self.token,self.ui.text.toPlainText())
				print("written to 1",self.file_name)
				inp_save_lines_to_file(self.file_name,lines)
			else:											#The file does not exist or there is an error
				lines=inp_new_file()
				lines=inp_add_token(lines,self.token,self.ui.text.toPlainText())
				print("written to 2",self.file_name,lines)
				inp_save_lines_to_file(self.file_name,lines)

	def callback_help(self):
		webbrowser.open('http://www.gpvdm.com/man/index.html')

