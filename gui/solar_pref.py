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

## @package solar_pref
#  Solar model.
#

import sys
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QCheckBox,QDesktopWidget,QPushButton


class checkBoxInput(QWidget):
    def __init__(self, parentObject, parent=None):
        super(checkBoxInput, self).__init__(parent)
        self.resize(100,200)
        self.parentObject = parentObject

        layout = QVBoxLayout()
        self.b1 = QCheckBox("Title")
        self.b1.setChecked(self.parentObject.states[0])
        layout.addWidget(self.b1)

        self.b2 = QCheckBox("BlackBody")
        self.b2.setChecked(self.parentObject.states[1])
        layout.addWidget(self.b2)

        self.b3 = QCheckBox("Extraterrestrial")
        self.b3.setChecked(self.parentObject.states[2])
        layout.addWidget(self.b3)

        self.b4 = QCheckBox("Direct")
        self.b4.setChecked(self.parentObject.states[3])
        if parentObject.enable_earthattr:
            layout.addWidget(self.b4)

        self.b5 = QCheckBox("Diffuse")
        self.b5.setChecked(self.parentObject.states[4])
        self.b5.stateChanged.connect(lambda: self.b5)
        if parentObject.enable_earthattr:
            layout.addWidget(self.b5)

        self.b6 = QCheckBox("Total")
        self.b6.setChecked(self.parentObject.states[5])
        if parentObject.enable_earthattr:
            layout.addWidget(self.b6)
        if parentObject.enable_marsattr:
            layout.addWidget(self.b6)
        if parentObject.enable_venusattr:
            layout.addWidget(self.b6)

        self.b7 = QCheckBox("Legend")
        self.b7.setChecked(self.parentObject.states[6])
        layout.addWidget(self.b7)

        self.okButton = QPushButton('Apply')
        layout.addWidget(self.okButton)
        self.okButton.clicked.connect(self.getPreferences)


        self.setLayout(layout)
        self.center()

    def getPreferences(self):
        TitleState = self.b1.isChecked()
        BlackBodyState = self.b2.isChecked()
        ETState = self.b3.isChecked()
        DirectState = self.b4.isChecked()
        DiffuseState = self.b5.isChecked()
        TotalState = self.b6.isChecked()
        LegendState = self.b7.isChecked()
        self.parentObject.states = [TitleState, BlackBodyState, ETState, DirectState, DiffuseState, TotalState, LegendState]
        self.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

