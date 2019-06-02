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


## @package command_args
#  Handle command line arguments.
#

import sys
import os

from clone import gpvdm_clone
from export_as import export_as
from import_archive import import_archive
from util import gpvdm_copy_src

from import_archive import clean_scan_dirs
from ver import ver
from ver import version
from import_archive import import_scan_dirs
from make_man import make_man
from scan_tree import tree_load_program
from scan_tree import tree_gen

from server import base_server
from cal_path import get_exe_command
from dat_file_class import dat_file
from plot_io import plot_load_info
from scan_plot import scan_gen_plot_data
from server_io import server_find_simulations_to_run
from clean_sim import clean_sim_dir
from ver import ver_sync_ver
from code_ctrl import enable_cluster
from win_lin import running_on_linux
from inp import inp_update_token_value
from device_lib_io import device_lib_replace
from device_lib_io import device_lib_delete
from cal_path import test_arg_for_sim_file
from cal_path import set_sim_path
from import_archive import patch_file
from inp import inp_encrypt
from inp import inp_dir_listing
from util_zip import archive_decompress
from util_zip import archive_compress
from scan_io import build_scan
from scan_io import scan_build_nested_simulation
from scan_tree import tree_load_flat_list

from scan_item import scan_items_clear
from scan_item import scan_items_populate_from_known_tokens
from scan_item import scan_items_populate_from_files
from device_lib_io import device_lib_token_change
from device_lib_io import device_lib_token_delete
from device_lib_io import device_lib_token_insert
from device_lib_io import device_lib_token_duplicate
from device_lib_io import device_lib_fix_ver

from scan_ml import scan_ml_build_vector

from scan_io import scan_archive

from gui_enable import set_gui
from gui_enable import gui_get

from device_lib_io import device_lib_token_repair

from materials_io import archive_materials

import i18n
_ = i18n.language.gettext

import argparse
parser = argparse.ArgumentParser(epilog=_("gpvdm command line tool")+" https://www.gpvdm.com"+"\n"+_("Report bugs to:")+" roderick.mackenzie@nottingham.ac.uk")
parser.add_argument("--version", help=_("displays the current version"), action='store_true')
parser.add_argument("--ver", help=_("displays the current version"), action='store_true')
parser.add_argument("--replace", help=_("replaces file in device lib --replace file.inp path_to_device_lib"), nargs=2)
parser.add_argument("--token_append", help=_("Appends a token to files in the device lib after a given token --token_append file.inp #token #token_befor #value path_to_device_lib"), nargs=5)
parser.add_argument("--token_change", help=_("Changes the value of a token device lib --token_change file.inp \\#token value"), nargs=3)
parser.add_argument("--token_delete", help=_("Delete a token from the device lib --token_delete file.inp \\#token"), nargs=2)
parser.add_argument("--token_insert", help=_("Insert a token into the device lib files --token_insert file.inp \\where \\#token \\value"), nargs=4)
parser.add_argument("--token_duplicate", help=_("Copy the value of a token the device lib files --token_insert dest_file.inp \\token \\#src_file.inp \\token"), nargs=4)
parser.add_argument("--token_repair", help=_("Repair --token_repair dest_file.inp \\#token \\#src_file.inp \\token"), nargs=4)
parser.add_argument("--token_fix_ver", help=_("Fix ver --token_fix_ver file.inp version"), nargs=2)

parser.add_argument("--delete", help=_("deletes file in device lib --delete file.inp path_to_device_lib"), nargs=2)


if test_arg_for_sim_file()==False:
	args = parser.parse_args()

def command_args_tool(argc,argv):
	if test_arg_for_sim_file()!=False:
		return

	if argc>=2:
		if args.version:
			print(version())
			sys.exit(0)
		elif args.ver:
			print(ver())
			sys.exit(0)
		elif args.replace:
			device_lib_replace(args.replace[0],dir_name=args.replace[1])
			exit(0)
		elif args.token_append:
			device_lib_token_append_after(args.token_append[0],dir_name=args.token_append[1])
			exit(0)
		elif args.token_change:
			print(args.token_change)
			device_lib_token_change(args.token_change[0],args.token_change[1],args.token_change[2])
			exit(0)
		elif args.token_delete:
			print(args.token_delete)
			device_lib_token_delete(args.token_delete[0],args.token_delete[1])
			exit(0)
		elif args.token_insert:
			print(args.token_insert)
			device_lib_token_insert(args.token_insert[0],args.token_insert[1],args.token_insert[2],args.token_insert[3])
			exit(0)
		elif args.token_duplicate:
			device_lib_token_duplicate(args.token_duplicate[0], args.token_duplicate[1], args.token_duplicate[2], args.token_duplicate[3])
			exit(0)
		elif args.token_repair:
			device_lib_token_repair(args.token_repair[0], args.token_repair[1], args.token_repair[2], args.token_repair[3])
			exit(0)
		elif args.token_fix_ver:
			device_lib_fix_ver(args.token_fix_ver[0], args.token_fix_ver[1])
			exit(0)
		elif args.delete:
			device_lib_delete(args.delete[0],dir_name=args.delete[1])
			exit(0)

