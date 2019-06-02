#!/usr/bin/env python3
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

## @package gpvdm
#  The main gpvdm gui code
#

import os
import sys

#paths
sys.path.append('./gui/')
sys.path.append('/usr/lib/gpvdm/')
sys.path.append('/usr/lib64/gpvdm/')
sys.path.append('/usr/share/gpvdm/gui/')	#debian
sys.path.append('/usr/share/sip/PyQt5/')

from notice import notice
print(notice())
print("loading.... please wait...")

from gui_enable import gui_test
gui_test()

from win_lin import running_on_linux
from cal_path import get_image_file_path
from cal_path import calculate_paths
from cal_path import calculate_paths_init
from cal_path import get_share_path
from cal_path import set_sim_path

calculate_paths_init()
calculate_paths()
from cal_path import get_lang_path

import i18n
_ = i18n.language.gettext

from cal_path import get_inp_file_path
from token_lib import build_token_lib
build_token_lib()

from code_ctrl import enable_betafeatures
from code_ctrl import code_ctrl_load
from code_ctrl import enable_webupdates

#undo
from undo import undo_list_class

#ver
from ver import ver_load_info
from ver import ver_error

ver_load_info()

code_ctrl_load()

from command_args_tool import command_args_tool

command_args_tool(len(sys.argv),sys.argv)

