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

## @package optics_ribbon
#  The ribbon for the optics window
#


import os

from dump_io import dump_io

from code_ctrl import enable_betafeatures
from cal_path import get_css_path

#qt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon, QTextFormat,QTextOption
from PyQt5.QtCore import QSize, Qt,QFile,QIODevice,QRect
from PyQt5.QtWidgets import QWidget,QSizePolicy, QPlainTextEdit,QVBoxLayout,QHBoxLayout, QPushButton,QDialog,QFileDialog,QToolBar, QMessageBox, QLineEdit, QToolButton
from PyQt5.QtWidgets import QTabWidget

from PyQt5.QtGui import QPainter,QColor
from icon_lib import icon_get

from about import about_dlg

from mode_selector import mode_selector
from tb_optical_model import tb_optical_model
from tb_spectrum import tb_spectrum

from util import wrap_text
from ribbon_base import ribbon_base
from play import play
from QAction_lock import QAction_lock
from inp import inp_get_token_value
from inp import inp_update_token_value
from cal_path import get_sim_path

from PyQt5.QtCore import QFile, QRegExp, Qt
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat
from code_editor import code_editor

from inp import inp_load_file
from inp import inp_save

class Highlighter(QSyntaxHighlighter):
	def __init__(self, parent=None):
		super(Highlighter, self).__init__(parent)

		self.highlightingRules = []

		keyword = QTextCharFormat()
		keyword.setForeground( Qt.darkRed )
		keyword.setFontWeight( QFont.Bold )
		keywords = [ "break", "else", "for", "if", "in"
					 "next", "repeat", "return", "switch",
					 "try", "while" ] 
		for word in keywords:
			pattern = QRegExp("\\b" + word + "\\b")
			self.highlightingRules.append( (pattern, keyword) )


		keywords = [ "class","def"]

		for word in keywords:
			pattern = QRegExp(word + "\\b")
			self.highlightingRules.append( (pattern, keyword) )

		classFormat = QTextCharFormat()
		classFormat.setFontWeight(QFont.Bold)
		classFormat.setForeground(Qt.darkMagenta)
		self.highlightingRules.append((QRegExp("\\bQ[A-Za-z]+\\b"),classFormat))

		singleLineCommentFormat = QTextCharFormat()
		singleLineCommentFormat.setForeground(Qt.red)
		self.highlightingRules.append((QRegExp("//[^\n]*"),singleLineCommentFormat))

		self.multiLineCommentFormat = QTextCharFormat()
		self.multiLineCommentFormat.setForeground(Qt.red)

		quotationFormat = QTextCharFormat()
		quotationFormat.setForeground(Qt.darkGreen)
		self.highlightingRules.append((QRegExp("\".*\""), quotationFormat))

		functionFormat = QTextCharFormat()
		functionFormat.setFontItalic(True)
		functionFormat.setForeground(Qt.blue)
		self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\()"),functionFormat))

		self.commentStartExpression = QRegExp("/\\*")
		self.commentEndExpression = QRegExp("\\*/")

	def highlightBlock(self, text):
		for pattern, format in self.highlightingRules:
		    expression = QRegExp(pattern)
		    index = expression.indexIn(text)
		    while index >= 0:
		        length = expression.matchedLength()
		        self.setFormat(index, length, format)
		        index = expression.indexIn(text, index + length)

		self.setCurrentBlockState(0)

		startIndex = 0
		if self.previousBlockState() != 1:
		    startIndex = self.commentStartExpression.indexIn(text)

		while startIndex >= 0:
		    endIndex = self.commentEndExpression.indexIn(text, startIndex)

		    if endIndex == -1:
		        self.setCurrentBlockState(1)
		        commentLength = len(text) - startIndex
		    else:
		        commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

		    self.setFormat(startIndex, commentLength,
		            self.multiLineCommentFormat)
		    startIndex = self.commentStartExpression.indexIn(text,
		            startIndex + commentLength);

class script_editor(code_editor):
	def __init__(self):
		code_editor.__init__(self)
		font = QFont()
		font.setFamily('Monospace')
		font.setFixedPitch(True)
		font.setPointSize(17)

		self.setFont(font)

		self.highlighter = Highlighter(self.document())

	def load(self,file_name):
		self.file_name=file_name
		lines=inp_load_file(file_name)
		self.setPlainText("\n".join(lines))

	def save(self):
		text=self.toPlainText().split("\n")
		inp_save(self.file_name,text)

	def run(self):
		os.system("python3 "+self.file_name)

