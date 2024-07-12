#!/usr/bin/env python3

"""
Simple Slurm Tools
Copyright (C) 2024 John Snowdon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

#####################################################################
#
# Tools to cache slurm statistic data as persistent files to disk
#
#####################################################################

import datetime
import json
import hashlib
import os
import lib.settings as settings

CODE_FILES = ["lib/slurmjob.py"]

class slurmCache():

	def __init__(self):
		self.master_key = None
		self.debug = settings.DEBUG

	def hashcode(self):
		""" Hash all of the source files which will be used to
		generate a report. If they change, then we know that the 
		persistent cache files may be invalid as it is likely that
		the data generation algorithm is different, the data structures
		which are returned are different, or similar. """
		
		fingerprint = ""
		data = ""
		for f in CODE_FILES:
			with open(f, 'r') as code_file:
				# read contents of the file
				data += code_file.read()   
				
		# pipe contents of the source files through md5 to get a fingerprint
		data = data.encode('utf-8')
		fingerprint = hashlib.md5(data).hexdigest()
				
		self.master_key = fingerprint
		return fingerprint
		
	def hashkey(self, year = 0, month = 0, day = 0, hours = 0, minutes = 0, key = ""):
		
		if self.master_key is None:
			self.hashcode()
		sub_key = str(year) + "-" + str(month) + "-" + str(day) + "-" + str(hours) + "-" + str(minutes) + str(key)
		sub_key = sub_key.encode('utf-8')
		k = self.master_key + "-" + hashlib.md5(sub_key).hexdigest()
		
		return k
		
		
	def store(self, year = 0, month = 0, day = 0, hours = 0, minutes = 0, key = "", data = None):
		""" Store a persistent data object on disk """
		
		if data:
				
			k = self.hashkey(year, month, day, hours, minutes, key)
			
			cache_filename = settings.CACHE_PATH + "/" + k + ".json"
			
			if os.path.exists(cache_filename):
				os.remove(cache_filename)
				
			json_data = json.dumps(data)
			
			cache_file = open(cache_filename, "w")
			cache_file.write(json_data)
			cache_file.close()
			return True
		else:
			return False
			
	def load(self, year = 0, month = 0, day = 0, hours = 0, minutes = 0, key = ""):
		""" Load a persistent cache object from disk """

		k = self.hashkey(year, month, day, hours, minutes, key)
			
		cache_filename = settings.CACHE_PATH + "/" + k + ".json"
		
		if os.path.exists(cache_filename):
			if self.debug:
				print("-- Cache loading %s" % cache_filename)
			cache_file = open(cache_filename, "r")
			cache_data = cache_file.read()
			data = json.loads(cache_data)
			cache_file.close()
			return data
		else:
			return False
		
	def storecmd(self, key = "", data = None):
		""" Store a persistent data object on disk """
		
		if data:
				
			k = self.hashkey(key)
			
			cache_filename = settings.CACHE_PATH + "/" + k + ".json"
			
			if os.path.exists(cache_filename):
				os.remove(cache_filename)
				
			json_data = json.dumps(data)
			
			cache_file = open(cache_filename, "w")
			cache_file.write(json_data)
			cache_file.close()
			return True
		else:
			return False
		
	def loadcmd(self, key = ""):
		""" Load a persistent cache object from disk """

		k = self.hashkey(key)
			
		cache_filename = settings.CACHE_PATH + "/" + k + ".json"
		
		if os.path.exists(cache_filename):
			if self.debug:
				print("-- Cache loading %s" % cache_filename)
			cache_file = open(cache_filename, "r")
			cache_data = cache_file.read()
			data = json.loads(cache_data)
			cache_file.close()
			return data
		else:
			return False