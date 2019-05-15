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

## @package solar_main
#  Part of solar module - delete?
#
import sys
from PyQt5.QtWidgets import QMenuBar, QWidget, QApplication, QAction,QDesktopWidget,QTabWidget,QVBoxLayout
from PyQt5.QtGui import QIcon

import os

from solar_planet import planet
from ribbon_solar import ribbon_solar

from icon_lib import icon_get
from PyQt5.QtCore import pyqtSignal

class solar_main(QWidget):

	update = pyqtSignal()

	def __init__(self,path):
		self.path=path
		self.export_file_name=os.path.join(self.path,"spectra.inp")
		super().__init__()
		self.resize(1200,600)
		self.setWindowIcon(icon_get("weather-few-clouds"))

		self.vbox=QVBoxLayout()

		self.ribbon = ribbon_solar()
		self.vbox.addWidget(self.ribbon)
		
		self.ribbon.run.triggered.connect(self.callback_run)

		self.ribbon.export.triggered.connect(self.callback_export)
		
		self.setWindowTitle(_("Solar Spectrum Generator")+" (https://www.gpvdm.com)")
		self.center()

		self.notebook = QTabWidget()

		self.vbox.addWidget(self.notebook)

		earth = planet(self.export_file_name)
		earth.set_earth(True)
		earth.init()
		self.notebook.addTab(earth,"Earth")

		#mercury = planet(self.export_file_name)
		#mercury.set_mercury(True)
		#mercury.set_orbitalpoint(True)
		#mercury.init()
		#self.notebook.addTab(mercury,"Mercury")

		#venus = planet(self.export_file_name)
		#venus.set_venus(True)
		#venus.set_orbitalpoint(True)
		#venus.init()
		#self.notebook.addTab(venus,"Venus")

		#mars = planet(self.export_file_name)
		#mars.set_mars(True)
		#mars.set_orbitalpoint(True)
		#mars.init()
		#self.notebook.addTab(mars,"Mars")

		#ceres = planet(self.export_file_name)
		#ceres.set_ceres(True)
		#ceres.set_orbitalpoint(True)
		#ceres.init()
		#self.notebook.addTab(ceres, "Ceres (Dwarf Planet)")

		#europa = planet(self.export_file_name)
		#europa.set_europa(True)
		#europa.set_orbitalpoint(True)
		#europa.init()
		#self.notebook.addTab(europa, "Europa (moon of Jupiter)")

		#halley = planet(self.export_file_name)
		#halley.set_halley(True)
		#halley.set_orbitalpoint(True)
		#halley.init()
		#self.notebook.addTab(halley, "Halley's Comet")

		#pluto = planet(self.export_file_name)
		#pluto.set_pluto(True)
		#pluto.set_orbitalpoint(True)
		#pluto.init()
		#self.notebook.addTab(pluto, "Pluto")
		
		self.setLayout(self.vbox)


	def callback_run(self):
		tab = self.notebook.currentWidget()
		tab.update()

	def callback_export(self):
		tab = self.notebook.currentWidget()
		tab.export()
		self.update.emit()


	def save(self):
		self.notebook.currentWidget().save()

	def copy(self):
		self.notebook.currentWidget().copy2clip()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())


if __name__ == '__main__':
	app = QApplication(sys.argv)
	win = spectrum_main()
	sys.exit(app.exec_())
