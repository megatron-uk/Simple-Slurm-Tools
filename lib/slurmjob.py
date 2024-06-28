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
# Encapsulation of a Slurm job.
#
#############################################################

AUTHOR = "John Snowdon"
URL= "https://github.com/megatron-uk/Simple-Slurm-Tools"

# Fields retrieved when getting lists of jobs
FIELDS_SUMMARY 	= 'User,Account,AllocCPUS,AllocNodes,CPUTimeRaw,Elapsed,JobID,Reserved,\
NodeList,Partition,Reason,ReqCPUS,ReqMem,ReqNodes,Submit'
FIELDS_INTEGER 	= ['AllocCPUS', 'AllocNodes', 'ReqCPUS', 'CPUTimeRaw', 'ReqNodes']
FIELDS_LIST 		= []
FIELDS 			= 'User,Account,AllocCPUS,AllocNodes,AllocTRES,AssocID,AveCPU,\
AveCPUFreq,AveDiskRead,AveDiskWrite,AvePages,AveRSS,AveVMSize,BlockID,Cluster,\
Comment,Constraints,ConsumedEnergy,ConsumedEnergyRaw,CPUTime,CPUTimeRAW,DBIndex,\
DerivedExitCode,Elapsed,ElapsedRaw,Eligible,End,ExitCode,Flags,GID,Group,JobID,\
JobIDRaw,JobName,Layout,MaxDiskRead,MaxDiskReadNode,MaxDiskReadTask,MaxDiskWrite,\
MaxDiskWriteNode,MaxDiskWriteTask,MaxPages,MaxPagesNode,MaxPagesTask,MaxRSS,MaxRSSNode,\
MaxRSSTask,MaxVMSize,MaxVMSizeNode,MaxVMSizeTask,McsLabel,MinCPU,MinCPUNode,MinCPUTask,\
NCPUS,NNodes,NodeList,NTasks,Priority,Partition,QOS,QOSRAW,Reason,ReqCPUFreq,\
ReqCPUFreqMin,ReqCPUFreqMax,ReqCPUFreqGov,ReqCPUS,ReqMem,ReqNodes,ReqTRES,Reservation,\
ReservationId,Reserved,ResvCPU,ResvCPURAW,Start,State,Submit,Suspended,SystemCPU,\
SystemComment,Timelimit,TimelimitRaw,TotalCPU,TRESUsageInAve,TRESUsageInMax,\
TRESUsageInMaxNode,TRESUsageInMaxTask,TRESUsageInMin,TRESUsageInMinNode,\
TRESUsageInMinTask,TRESUsageInTot,TRESUsageOutAve,TRESUsageOutMax,TRESUsageOutMaxNode,\
TRESUsageOutMaxTask,TRESUsageOutMin,TRESUsageOutMinNode,TRESUsageOutMinTask,\
TRESUsageOutTot,UID,User,UserCPU,WCKey,WCKeyID,WorkDir'
FAIL_STATES 		= 'CA,DL,F,NF,PR,RS,RV,TO,OOM'

class SlurmJob():
	""" Class with methods for working with slurm job details from sacct and scontrol """

	def __init__(self, debug = False):
		self.job = {}
		self.job_id = None
		self.subjobs = []
		self.debug = debug

		self.hostname_cache = {}

	def expand_nodelist(self, nodelist = None):
		""" Expand a slurm nodelist into discrete hostnames """

		expanded_list = []

		job_cmd = f"scontrol show hostname {nodelist}"

		try:

			if nodelist in self.hostname_cache:
				return self.hostname_cache[nodelist]

			process = subprocess.Popen(job_cmd, shell=True,
				stdin=subprocess.PIPE, stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
			if process:
				output = process.stdout.read().rstrip().split(b'\n')
				if len(output) > 0:
					for hostname in output:
						expanded_list.append(hostname.decode())
					self.hostname_cache[nodelist] = expanded_list
			else:
				return False
		except Exception as error:
			print(f"Exception making subprocess call to expand node list [{job_cmd}]")
			print(f"Exception was {error}")
			return False

		return expanded_list

	def field_to_datetime(self, field = ""):
		""" Turn a string field from slurm into a python datetime object """

		days = 0
		hours = 0
		minutes = 0
		seconds = 0
		if len(field) > 0:
			if '-' in field:
				# DD-HH:MM:SS
				days = int(field.split('-')[0])
				hours = int((field.split('-')[1]).split(':')[0])
				minutes = int((field.split('-')[1]).split(':')[1])
				seconds = int((field.split('-')[1]).split(':')[2])
			else:
				# HH:MM:SS
				hours = int(field.split(':')[0])
				minutes = int(field.split(':')[1])
				seconds = int(field.split(':')[2])

		data = datetime.timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds)
		return data

	def get_memorypercore(self, reqmem = 0, cpus = 0, reqnodes = 0, allocnodes = 0):
		""" Generate the memory-per-core metric """

		data = 0

		if 'c' in reqmem:
			if 'M' in reqmem:
				data = int(float(reqmem.split('M')[0]))

			if 'G' in reqmem:
				data = int(float(reqmem.split('G')[0])) * 1024

			if 'T' in reqmem:
				data = int(float(reqmem.split('T')[0])) * 1024 * 1024
			return data

		if 'n' in reqmem:
			if allocnodes != 0:
				nodes = allocnodes
			else:
				nodes = reqnodes

			if 'M' in reqmem:
				data = int(float(reqmem.split('M')[0])) / (cpus / nodes)

			if 'G' in reqmem:
				data = (int(float(reqmem.split('G')[0])) * 1024) / (cpus / nodes)

			if 'T' in reqmem:
				data = (int(float(reqmem.split('T')[0])) * 1024 * 1024) / (cpus / nodes)

		return data

	def set_rowsummary(self, stdout = None, expand_nodes = False):
		""" Takes one row of job summary text from an sacct call
		and maps the columns to dictionary keys.
		Returns the dictionary containing the job fields """

		try:

			data = {}
			data['MemoryPerCore'] = 0
			idx = 0
			stdout_decoded = stdout.decode().split('|')
			for fieldname in FIELDS_SUMMARY.split(','):
				data[fieldname] = stdout_decoded[idx]
				if fieldname in FIELDS_INTEGER:
					data[fieldname] = int(data[fieldname])
				if fieldname in FIELDS_LIST:
					data[fieldname] = data[fieldname].split(',')
				idx += 1

			# Memory is a special case, as it is not reported in a standard way
			# We could have a memory per core figure '2500Mc', '4Gc', etc.
			# OR
			# We could have a memory per node figure '4000Mn', '32Gn', etc.
			# We need to normalise both cases so that all jobs can be reported
			# in the same way.
			cpus = 0
			if data['AllocCPUS'] != 0:
				cpus = data['AllocCPUS']
			else:
				cpus = data['ReqCPUS']

			data['MemoryPerCore'] = self.get_memorypercore(data['ReqMem'],
				cpus,
				data['ReqNodes'],
				data['AllocNodes'])
			data['TotalMemory'] = cpus * data['MemoryPerCore']

			if expand_nodes:
				data['NodeList'] = self.expand_nodelist(nodelist = data['NodeList'])

			data['ReservedTime'] = self.field_to_datetime(field = data['Reserved']).total_seconds() / 60
			data['ElapsedTime'] = self.field_to_datetime(field = data['Elapsed']).total_seconds() / 60

			# Also generate a 'minutes prior to now' field based on the submission date/time field
			submitdatetime = datetime.datetime.strptime(data['Submit'], '%Y-%m-%dT%H:%M:%S')
			data['SubmitMinutes'] = (datetime.datetime.now() - submitdatetime).seconds / 60

		except Exception as error:
			print("Exception while mapping job data!")
			print(f"Exception was {error}")
			print(traceback.format_exc())
			print("")
			if 'JobID' in data:
				print(f"The above entry for job [{data['JobID']}] will be IGNORED...")
			else:
				print("The above entry will be IGNORED...")

			return False

		return data

	def setrow(self, row = 0, stdout = None):
		""" Takes one row of text output from an sacct call and maps
		the columns to dictionary keys.
		If the 'row' value is set to other than 0, then the dictionary
		is added as a job sub-component entry. """

		data = {}
		data['MemoryPerCore'] = 0
		idx = 0

		# Split the string into fields based on the list of entries
		# we requested in the FIELDS variable
		for fieldname in FIELDS.split(','):
			data[fieldname] = stdout.decode().split('|')[idx]
			if fieldname in FIELDS_INTEGER:
				data[fieldname] = int(data[fieldname])
			if fieldname in FIELDS_LIST:
				data[fieldname] = data[fieldname].split(',')
			idx += 1

		# Memory is a special case, as it is not reported in a standard way
		# We could have a memory per core figure '2500Mc', '4Gc', etc.
		# OR
		# We could have a memory per node figure '4000Mn', '32Gn', etc.
		# We need to normalise both cases so that all jobs can be reported
		# in the same way.
		if row == 0:

			cpus = 0
			if data['AllocCPUS'] != 0:
				cpus = data['AllocCPUS']
			else:
				cpus = data['ReqCPUS']

			data['NodeList'] = self.expand_nodelist(nodelist = data['NodeList'])
			data['MemoryPerCore'] = self.get_memorypercore(data['ReqMem'],
				cpus, data['ReqNodes'],
				data['AllocNodes'])
			data['TotalMemory'] = cpus * data['MemoryPerCore']

		# Reserved and Elapsed time are also in a non-standard field type of
		# D-HH:MM:SS
		# This needs to be transformed into an object we can tally with others
		if row == 0:
			data['ReservedTime'] = self.field_to_datetime(field = data['Reserved']).total_seconds() / 60
			data['ElapsedTime'] = self.field_to_datetime(field = data['Elapsed']).total_seconds() / 60

		if row == 0:
			# If this is the first row of an sacct output, set it as
			# the 'leader' job entry
			self.job = data

		else:
			# Otherwise record this as a component of the the job
			self.subjobs.append(data)

	def get_by(self, job_cmd = "", expand_nodes = False):
		""" Get job data """

		try:
			jobs = []
			process = subprocess.Popen(job_cmd, shell=True,
				stdin=subprocess.PIPE, stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
			if process:
				output = process.stdout.read().split(b'\n')
				if len(output) > 3:
					for line in output[1:-1]:
						outdata = self.set_rowsummary(stdout = line, expand_nodes = expand_nodes)
						if outdata:
							jobs.append(outdata)
			else:
				return False
		except Exception as error:
			print(f"Exception making subprocess call for job cmd [{job_cmd}]")
			print(f"Exception was {error}")
			print(traceback.format_exc())
			return False

		return jobs

	def get_bystate(self, state = None, start = None, end = None, expand_nodes = False):
		""" Return all of the jobs in a given state across all partitions """

		# If looking for failed jobs, expand the criteria to all 'abnormal' codes
		if state == 'F':
			state = FAIL_STATES
		if start and end:
			job_cmd = f"sacct -X -p -a -S {start} -E {end} --state={state} --format={FIELDS_SUMMARY}"
		else:
			job_cmd = f"sacct -X -p -a --state={state} --format={FIELDS_SUMMARY}"
		jobs = self.get_by(job_cmd, expand_nodes)
		return jobs

	def get_bynode(self, hostname = None, expand_nodes = False):
		""" Return all of the jobs currently on a given node """

		job_cmd = f"sacct -X -p -a --nodelist={hostname} --state=R --format={FIELDS_SUMMARY}"
		jobs = self.get_by(job_cmd, expand_nodes)
		return jobs

	def get_bypartition(self, partition = None, state = "R", expand_nodes = False):
		""" Return all of the jobs on a given partition with a given slurm state code """

		job_cmd = f"sacct -X -p -a --partition={partition} --state={state} --format={FIELDS_SUMMARY}"
		jobs = self.get_by(job_cmd, expand_nodes)
		return jobs

	def get_details(self, jobid = None):
		""" Return the top-level information for a specific job - this only
		returns a single entry, use 'getAll()' to return sub-components """

		self.job_id = jobid

		job_cmd = f"sacct -p -a -j {self.job_id} --format={FIELDS}"

		try:
			process = subprocess.Popen(job_cmd, shell=True,
				stdin=subprocess.PIPE, stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
			if process:
				# Parse stdout
				# First line are the field headers
				# Second line are the underline of the column names
				# Fields are delimited by '|'
				output = process.stdout.read().split(b'\n')

				# One job entry
				if len(output) == 3:
					self.setrow(0, output[1])

				# More than one job entry
				if len(output) > 3:
					line_number = 1
					for line in output[1:-1]:
						if line_number == 1:
							self.setrow(0, line)
						else:
							self.setrow(line_number, line)
						line_number += 1

			else:
				return False
		except Exception as error:
			print(f"Exception making subprocess call for jobid {self.job_id}")
			print(f"Exception was {error}")
			print(traceback.format_exc())
			return False

		return True
