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

## @package spectral2
#  After R. Bird and C. Riordan 1984
#

import os
import sys

from math import *

from dat_file import dat_file
from cal_path import get_atmosphere_path
from zenith import zenith

class spectral2():
	def __init__(self):
		self.day=80		#winter equinox
		self.lat=51		#london
		self.hour=12
		self.min=0

		self.P=1.0		#Preasure 1bar
		self.aod=0.27	#AOD
		self.W= 1.42	#precip water

		file_name = os.path.join(get_atmosphere_path(), "SPECTRAL2", "etr.inp")
		self.etr=dat_file()
		self.etr.load(file_name)

		file_name = os.path.join(get_atmosphere_path(), "SPECTRAL2", "h2o.inp")
		self.aw=dat_file()
		self.aw.load(file_name)

		file_name = os.path.join(get_atmosphere_path(), "SPECTRAL2", "o3.inp")
		self.ao=dat_file()
		self.ao.load(file_name)

		file_name = os.path.join(get_atmosphere_path(), "SPECTRAL2", "uni_abs.inp")
		self.au=dat_file()
		self.au.load(file_name)

		self.cal_earth_sun_distance()

		#zenith
		self.Z_rad=zenith(self.lat, self.day, self.hour, self.min)
		self.Z_deg=self.Z_rad*360/2/pi

		self.Tr=dat_file()
		self.Tr.copy(self.etr)
		self.cal_rayleigh()

		self.Ta=dat_file()
		self.Ta.copy(self.etr)
		self.cal_arosol()

		self.Tw=dat_file()
		self.Tw.copy(self.etr)
		self.cal_water()

		self.To=dat_file()
		self.To.copy(self.etr)
		self.cal_ozone()

		self.Tu=dat_file()
		self.Tu.copy(self.etr)
		self.cal_mixed_gas()

		self.Id=self.etr*self.D*self.Tr*self.Ta*self.Tw*self.To*self.Tu
		self.Id.save_as_txt("one.dat")

		self.I=self.Id

	def cal_earth_sun_distance(self):
		# Earth-Sun Correction factor
		psi = 2 * pi * (self.day - 1) / 365		#eq 2-3
		self.D = 1.00011 + 0.034221 * cos(psi) + 0.00128 * sin(psi) + 0.00719 * cos(2 * psi) + 0.000077 * sin(2 * psi)		#eq 2-2

	def cal_rayleigh(self):
		P0=1.013								#In bar not mb
		# relative air mass (2-5)
		self.M = pow(cos(self.Z_rad) + 0.15 * pow(93.885 - self.Z_deg, -1.253), -1.0)

		# pressure corrected air mass
		self.M_dash = self.M * self.P / P0

		for y in range(0,self.Tr.y_len):
			lam=self.Tr.y_scale[y]*1e6		#in um
			self.Tr.data[0][0][y] = exp((-self.M_dash) / ((pow(lam, 4.0)) * (115.6406 - (1.3366 / pow(lam,2.0)))))	#(2-4)

	def cal_arosol(self):
		#So this ecpression comes from the origonal source code, and by reading the test in combinaion with the wiki page on the Angstrom exponent
		alpha=1.140
		for y in range(0,self.Ta.y_len):
			lam=self.Ta.y_scale[y]*1e6		#in um
			self.Ta.data[0][0][y] = exp(-self.aod * self.M * (lam / 0.5) ** (-alpha))


	def cal_water(self):
		for y in range(0,self.Tw.y_len):
			lam=self.Tw.y_scale[y]*1e6		#in um
			aw=self.aw.data[0][0][y]
			self.Tw.data[0][0][y] = exp((-0.2385 * aw * self.W * self.M) / pow(1 + 20.07 * aw * self.W * self.M,  0.45) )

	def cal_ozone(self):
		max_ozone_height=22.0
		Mo = (1 + max_ozone_height / 6370) / pow((pow(cos(self.Z_rad), 2.0) + 2 * max_ozone_height / 6370), 0.5)  # effective ozone mass
		for y in range(0,self.To.y_len):
			lam=self.To.y_scale[y]*1e6		#in um
			ao=self.ao.data[0][0][y]
			self.To.data[0][0][y] = exp(-ao * 0.395 * Mo)
		#print(str(self.To))

	def cal_mixed_gas(self):
		for y in range(0,self.Tu.y_len):
			lam=self.Tu.y_scale[y]*1e6		#in um
			au=self.au.data[0][0][y]
			self.Tu.data[0][0][y] = exp((-1.41 * au * self.M_dash) / pow((1.0 + 118.93 * au * self.M_dash),  0.45))


def earth_calc(Latitude, Longitude, W, p, Date, Time, AOD, timezone):
	a=spectral2()
	asdas

	# Diffuse irradiance on a horizontal surface
	# Rayleigh Scattering Component
	C_s = vals[0:122, 5]
	OMEGL = 0.945 * np.exp(-0.095 * (np.log(lam / 0.4)) ** 2)
	DELA = AOD * ((lam / 0.5) ** -1.14)
	T_aalam = np.exp(-(1 - OMEGL) * DELA * M)
	I_rlam = ext_ter_spec * D * math.cos(Z_rad) * T_olam * T_ulam * T_wlam * T_aalam * (1 - T_rlam ** 0.95) * 0.5 * C_s

	# Aerosol Scattering Component
	ALG = math.log(1 - 0.65)
	BFS = ALG * (0.0783 + ALG * (-0.3824 - ALG * 0.5874))
	AFS = ALG * (1.459 + ALG * (0.1595 + ALG * 0.4129))
	F_s = 1 - 0.5 * math.exp((AFS + BFS * math.cos(Z_rad)) * math.cos(Z_rad))
	T_aslam = np.exp(-OMEGL * DELA * M)
	I_alam = ext_ter_spec * D * math.cos(Z_rad) * T_olam * T_ulam * T_wlam * T_aalam * (T_rlam ** 1.5) * (
	1 - T_aslam) * F_s * C_s



	I_diffuse = I_rlam + I_alam  # +I_glam

	I_total = I_direct + I_diffuse

	# Solar Constant Calc (using trapezium rule to integrate I_total over wavelengths)
	solar_const = 0

	for i in range(1,len(I_total)):
		solar_const = solar_const + 0.5*(lam[i]-lam[i-1])*(I_total[i]+I_total[i-1])

	#ETR
	wb = openpyxl.load_workbook(filename=file_location)
	sheet_ranges = wb['Sheet1']
	vals = sheet_ranges['A1:B122']
	vals_array = []
	for row in vals:
		vals_array.append(list(map(lambda cell: float(cell.value), row)))

	vals1 = np.array(vals_array)

	lumin = vals1[0:122,1]

	#luminosity

	luminosity = 0

	for i in range(0, len(lam)):
		luminosity = luminosity + 683*10**(-3)*lumin[i]*I_total[i]

	#print(luminosity)

	return lam, I_direct, I_diffuse, I_total, lam_bb, sol, ext_ter_spec, solar_const

