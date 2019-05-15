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

## @package circuit
#  Widget to draw circuit diagram
#

import os
from cal_path import get_image_file_path
from tb_pulse_load_type import tb_pulse_load_type

#qt
from PyQt5.QtCore import QSize, Qt 
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QToolBar,QSizePolicy,QAction,QTabWidget,QMenuBar,QStatusBar
from PyQt5.QtGui import QPainter,QIcon,QPixmap

class my_draw(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        self.mQImage = QPixmap("document-new.png")

    def paintEvent(self, QPaintEvent):
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(100,10, self.mQImage)
        painter.end()


class circuit(QWidget):

	def update(self,object):
		self.darea.queue_draw()

	def __init__(self,index):
		QWidget.__init__(self)

		vbox=QVBoxLayout()


		self.index=index

		toolbar=QToolBar()
		toolbar.setIconSize(QSize(48, 48))


		self.load_type=tb_pulse_load_type(self.index)
		#self.load_type.connect("changed", self.draw_callback)

		toolbar.addWidget(self.load_type)
		vbox.addWidget(toolbar)

		self.diode = QPixmap(os.path.join(get_image_file_path(),"diode.png"))
		self.ideal_diode = QPixmap(os.path.join(get_image_file_path(),"ideal_diode.png"))
		self.load = QPixmap(os.path.join(get_image_file_path(),"load.png"))
		self.ideal_load = QPixmap(os.path.join(get_image_file_path(),"ideal_load.png"))
		self.voc = QPixmap(os.path.join(get_image_file_path(),"voc.png"))

		self.darea = QWidget()

		vbox.addWidget(self.darea)

		self.setLayout(vbox)
		self.load_type.changed.connect(self.repaint)
		return

	def paintEvent(self, QPaintEvent):
		y_offset=100
		x_offset=50

		painter = QPainter()
		painter.begin(self)

		if self.load_type.sim_mode.currentText()=="load":
			painter.drawPixmap(x_offset,y_offset, self.diode)

			painter.drawPixmap(x_offset+620,y_offset+67, self.load)
		elif self.load_type.sim_mode.currentText()=="ideal_diode_ideal_load":
			painter.drawPixmap(x_offset,y_offset, self.ideal_diode)

			painter.drawPixmap(x_offset+620,y_offset+68, self.ideal_load)
		else:
			painter.drawPixmap(x_offset,y_offset, self.diode)

			painter.drawPixmap(x_offset+620,y_offset+57, self.voc)

		painter.end()


