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

import traceback
import subprocess
import datetime

#############################################################
#
# Retrieve limit data for a user or account.
#
#############################################################

class SlurmLimits():

	def __init__(self, account_code):
		self.account_code = account_code
		self.parts = []
		self.limits = {}
		self.free_parts = []
		self.paid_parts = []

	def getAccountLimitsCores(self):
		if "cores" in self.limits.keys():
			return self.limits['cores']

		if "GrpTRES" in self.limits.keys():
			fields = self.limits['GrpTRES'].split('=')
			if len(fields) > 1:
				try:
					self.limits['cores'] = int(fields[1].split(',')[0])
				except:
					self.limits['cores'] = 0

	def getAccountLimitsGPU(self):
		if "gpu" in self.limits.keys():
			return self.limits['gpu']

		if "GrpTRES" in self.limits.keys():
			fields = self.limits['GrpTRES'].split('=')
			if len(fields) > 1:
				try:
					self.limits['gpu'] = int(fields[2])
				except:
					self.limits['gpu'] = 0

	def getAccountPartitions(self):
		if len(self.parts) > 0:
			return self.parts

		if self.account_code:

			job_cmd = f"sacctmgr list associations where account={self.account_code} -p"

			try:
				process = subprocess.Popen(job_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				if process:
					output = process.stdout.read().decode("utf-8")
					output = output.split('\n')
					if len(output) > 2:
						for line in output:
							if self.account_code in str(line):
								fields = str(line).split('|')
								part_name = fields[3]
								if part_name and (part_name != "") and (part_name not in self.parts):
									self.parts.append(part_name)
			except Exception as error:
                                print(f"Exception making sacctmgr partition call for account code {self.account_code}")
                                print(f"Exception was {error}")
                                print(traceback.format_exc())
                                return False
		return self.parts

	def getAccountFreePartitions(self):
		if len(self.free_parts) > 0:
			return self.free_parts

		self.getAccountPartitions()
		for part_name in self.parts:
			if "_free" in part_name:
				self.free_parts.append(part_name)

		return self.free_parts

	def getAccountPaidPartitions(self):
		if len(self.paid_parts) > 0:
			return self.paid_parts

		self.getAccountPartitions()
		for part_name in self.parts:
			if "_paid" in part_name:
				self.paid_parts.append(part_name)

		return self.paid_parts

	def getAccountLimits(self):
		if len(self.limits.keys()) > 0:
			return self.limits
		if self.account_code:

			job_cmd = f"sacctmgr list associations where account={self.account_code} user='' -p"

			try:
				process = subprocess.Popen(job_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				if process:
					output = process.stdout.read().decode("utf-8")
					output = output.split('\n')
					if len(output) == 3:
						line = output[1]
						if self.account_code in line:
							fields = line.split('|')
							self.limits = {
								'facility' : fields[0],
								'account_code' : fields[1],
								'user' : fields[2],
								'partition' : fields[3],
								'share' : fields[4],
								'priority' : fields[5],
								'GrpJobs' : fields[6],
								'GrpTRES' : fields[7],
								'GrpSubmit' : fields[8],
								'GrpWall' : fields[9],
								'GrpTRESMins' : fields[10],
								'MaxJobs' : fields[11],
								'MaxTRES' : fields[12],
								'MaxTRESPerNode' : fields[13],
								'MaxSubmit' : fields[14],
								'MaxWall' : fields[15],
								'MaxTRESMins' : fields[16],
								'QOS' : fields[17],
								'Def QOS' : fields[18],
								'ram' : None
							}
							for k in self.limits.keys():
								if self.limits[k] == '':
									self.limits[k] = None
							for k in ["share", "priority", "GrpTRESMins", "MaxJobs", "MaxSubmit", "MaxWall", "MaxTRESMins"]:
								try:
									self.limits[k] = int(self.limits[k])
								except:
									pass
							self.getAccountLimitsCores()
							self.getAccountLimitsGPU()
			except Exception as error:
				print(f"Exception making sacctmgr limits call for account code {self.account_code}")
				print(f"Exception was {error}")
				print(traceback.format_exc())

		return self.limits
