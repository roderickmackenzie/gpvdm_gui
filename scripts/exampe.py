#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

class gpvdm_plugin:

	def __init__(self,api):
		api.mkdir("scan")					#make a new scandir
		for i in range(1,20):				#count from 1 to 20
			sim_path="scan/"+str(i)			#define a sub simulation dir
			api.mkdir(sim_path)				#make the dir
			api.clone(sim_path)				#copy the simulation files to the dir
			print(str(1e-7*float(i)))			#Print some text
			api.edit(sim_path+"/dos0.inp","#mueffe",str(1e-7*float(i)))	#Edit the values in a simulation file
			api.edit(sim_path+"/dos0.inp","#mueffh",str(1e-7*float(i)*2.0))	#Edit the values in a simulation file
			api.add_job(path=sim_path)			#Add the job to the job list
		api.run()						#Run the jobs on as many CPUs as you have