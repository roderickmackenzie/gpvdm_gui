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

## @package solar_solargeometry
#  Solar module.
#

import math
from solar_model import *

#Equations to calculate zenith angle can be seen in .../Papers and Sources/zenithcalc.pdf
def get_zenith(Latitude, Longitude, d, hour, minute, timezone):
    gamma_val = ((2 * math.pi) / 365) * ((d - 1) + (hour - 12) / 24)
    decl_angle = 0.006918 - (0.399912 * math.cos(gamma_val)) + 0.070257 * math.sin(gamma_val) - 0.006758 * math.cos(
        2 * gamma_val) \
                 + 0.000907 * math.sin(2 * gamma_val) - 0.002697 * math.cos(3 * gamma_val) + 0.00148 * math.sin(
        3 * gamma_val)
    eq_time = 229.18 * (
        0.000075 + 0.001868 * math.cos(gamma_val) - 0.032077 * math.sin(gamma_val) - 0.014615 * math.cos(2 * gamma_val)
        - 0.040849 * math.sin(2 * gamma_val))
    time_offset = eq_time - 4 * Longitude + 60*timezone
    true_solar_time = hour * 60 + minute + time_offset
    solar_hour_angle = true_solar_time / 4 - 180

    Z_deg = (180/math.pi)*math.acos((math.sin(Latitude * (math.pi / 180)) * math.sin(decl_angle)) + (
        math.cos(Latitude * (math.pi / 180)) * math.cos(decl_angle) * math.cos(solar_hour_angle * (math.pi / 180))))
    return Z_deg
