#!/usr/bin/env python

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

#############################################################
#
# Encapsulation of a Slurm job.
#
#############################################################

AUTHOR = "John Snowdon"
URL= "https://github.com/megatron-uk/Simple-Slurm-Tools"

import traceback
import subprocess
import datetime
import time

# Fields retrieved when getting lists of jobs
FIELDS_SUMMARY = 'User,Account,AllocCPUS,AllocNodes,CPUTimeRaw,Elapsed,JobID,Reserved,NodeList,Partition,Reason,ReqCPUS,ReqMem,ReqNodes,Submit'

# Fields which should be cast to an integer type
FIELDS_INTEGER = ['AllocCPUS', 'AllocNodes', 'ReqCPUS', 'CPUTimeRaw', 'ReqNodes']

# Fields to convert into an array
FIELDS_LIST = []

# Fields retrieved when getting details on a single job
FIELDS = 'User,Account,AllocCPUS,AllocNodes,AllocTRES,AssocID,AveCPU,AveCPUFreq,AveDiskRead,AveDiskWrite,AvePages,AveRSS,AveVMSize,BlockID,Cluster,Comment,Constraints,ConsumedEnergy,ConsumedEnergyRaw,CPUTime,CPUTimeRAW,DBIndex,DerivedExitCode,Elapsed,ElapsedRaw,Eligible,End,ExitCode,Flags,GID,Group,JobID,JobIDRaw,JobName,Layout,MaxDiskRead,MaxDiskReadNode,MaxDiskReadTask,MaxDiskWrite,MaxDiskWriteNode,MaxDiskWriteTask,MaxPages,MaxPagesNode,MaxPagesTask,MaxRSS,MaxRSSNode,MaxRSSTask,MaxVMSize,MaxVMSizeNode,MaxVMSizeTask,McsLabel,MinCPU,MinCPUNode,MinCPUTask,NCPUS,NNodes,NodeList,NTasks,Priority,Partition,QOS,QOSRAW,Reason,ReqCPUFreq,ReqCPUFreqMin,ReqCPUFreqMax,ReqCPUFreqGov,ReqCPUS,ReqMem,ReqNodes,ReqTRES,Reservation,ReservationId,Reserved,ResvCPU,ResvCPURAW,Start,State,Submit,Suspended,SystemCPU,SystemComment,Timelimit,TimelimitRaw,TotalCPU,TRESUsageInAve,TRESUsageInMax,TRESUsageInMaxNode,TRESUsageInMaxTask,TRESUsageInMin,TRESUsageInMinNode,TRESUsageInMinTask,TRESUsageInTot,TRESUsageOutAve,TRESUsageOutMax,TRESUsageOutMaxNode,TRESUsageOutMaxTask,TRESUsageOutMin,TRESUsageOutMinNode,TRESUsageOutMinTask,TRESUsageOutTot,UID,User,UserCPU,WCKey,WCKeyID,WorkDir'

FAIL_STATES = 'CA,DL,F,NF,PR,RS,RV,TO,OOM'

class slurmJob():
	
	def __init__(self, debug = False):
		self.job = {}
		self.subjobs = []
		self.debug = debug
	
		self.hostname_cache = {}
	
	def expandnodelist(self, nodelist = None):
		""" Expand a slurm nodelist into discrete hostnames """
		
		expanded_list = []
		
		job_cmd = "scontrol show hostname %s" % nodelist
		
		try:
			
			if nodelist in self.hostname_cache:
				return self.hostname_cache[nodelist]
			
			p = subprocess.Popen(job_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			if p:
				output = p.stdout.read().rstrip().split(b'\n')
				if len(output) > 0:
					for hostname in output:
						expanded_list.append(hostname.decode())
					self.hostname_cache[nodelist] = expanded_list
			else:
				return False
		except Exception as e:
			print("Exception making subprocess call for job state %s" % state)
			print("Exception was %s" % e)
			return False
		
		return expanded_list
	
	def fieldToDatetime(self, field = ""):
		""" Turn a string field from slurm into a python datetime object """
		
		days = 0
		hours = 0
		minutes = 0
		seconds = 0
		if len(field) > 0:
			if '-' in field:
				days = int(field.split('-')[0])
				hours = int((field.split('-')[1]).split(':')[0])
				minutes = int((field.split('-')[1]).split(':')[1])
				seconds = int((field.split('-')[1]).split(':')[2])
			else:
				hours = int(field.split(':')[0])
				minutes = int(field.split(':')[1])
				seconds = int(field.split(':')[2])
				
		d = datetime.timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds)
		return d
	
	def getMemoryPerCore(self, reqmem = 0, cpus = 0, reqnodes = 0, allocnodes = 0):
		""" Generate the memory-per-core metric """
		
		d = 0
		
		if 'c' in reqmem:			
			if 'M' in reqmem:
				d = int(float(reqmem.split('M')[0])) 
				
			if 'G' in reqmem:
				d = int(float(reqmem.split('G')[0])) * 1024
			
			if 'T' in reqmem:
				d = int(float(reqmem.split('T')[0])) * 1024 * 1024			
			return d
			
		if 'n' in reqmem:
				
			if allocnodes != 0:
				Nodes = allocnodes
			else:
				Nodes = reqnodes
				
			if 'M' in reqmem:
				d = int(float(reqmem.split('M')[0])) / (cpus / Nodes) 
				
			if 'G' in reqmem:
				d = (int(float(reqmem.split('G')[0])) * 1024) / (cpus / Nodes)
			
			if 'T' in reqmem:
				d = (int(float(reqmem.split('T')[0])) * 1024 * 1024) / (cpus / Nodes)			
			
		return d
	
	def setrowSummary(self, stdout = None, expand_nodes = False):
		""" Takes one row of job summary text from an sacct call
		and maps the columns to dictionary keys.
		Returns the dictionary containing the job fields """
		
		try:
			
			d = {}
			d['MemoryPerCore'] = 0
			idx = 0
			stdout_decoded = stdout.decode().split('|')
			for fieldname in FIELDS_SUMMARY.split(','):
				d[fieldname] = stdout_decoded[idx]
				if fieldname in FIELDS_INTEGER:
					d[fieldname] = int(d[fieldname])
				if fieldname in FIELDS_LIST:
					d[fieldname] = d[fieldname].split(',')
				idx += 1
			
			# Memory is a special case, as it is not reported in a standard way
			# We could have a memory per core figure '2500Mc', '4Gc', etc.
			# OR
			# We could have a memory per node figure '4000Mn', '32Gn', etc.
			# We need to normalise both cases so that all jobs can be reported
			# in the same way.
			CPUS = 0
			if d['AllocCPUS'] != 0:
				CPUS = d['AllocCPUS']
			else:
				CPUS = d['ReqCPUS']
				
			d['MemoryPerCore'] = self.getMemoryPerCore(d['ReqMem'], CPUS, d['ReqNodes'], d['AllocNodes'])			
			d['TotalMemory'] = CPUS * d['MemoryPerCore']
	
			if expand_nodes:
				d['NodeList'] = self.expandnodelist(nodelist = d['NodeList'])

			d['ReservedTime'] = self.fieldToDatetime(field = d['Reserved']).total_seconds() / 60
			d['ElapsedTime'] = self.fieldToDatetime(field = d['Elapsed']).total_seconds() / 60
						
			# Also generate a 'minutes prior to now' field based on the submission date/time field
			submitdatetime = datetime.datetime.strptime(d['Submit'], '%Y-%m-%dT%H:%M:%S')
			d['SubmitMinutes'] = (datetime.datetime.now() - submitdatetime).seconds / 60
			
		except Exception as e:
			print("Exception while mapping job data!")
			print("Exception was: %s" % e)
			print(traceback.format_exc())
			print("")
			if 'JobID' in d:
				print("The above entry for job [%s] will be IGNORED..." % d['JobID'])
			else:
				print("The above entry will be IGNORED...")
			
			return False

		return d

	
	def setrow(self, row = 0, stdout = None):
		""" Takes one row of text output from an sacct call and maps
		the columns to dictionary keys
		If the 'row' value is set to other than 0, then the dictionary 
		is added as a job sub-component entry. """
	
		d = {}
		d['MemoryPerCore'] = 0
		idx = 0

		# Split the string into fields based on the list of entries
		# we requested in the FIELDS variable
		for fieldname in FIELDS.split(','):
			d[fieldname] = stdout.decode().split('|')[idx]
			if fieldname in FIELDS_INTEGER:
				d[fieldname] = int(d[fieldname])	
			if fieldname in FIELDS_LIST:
				d[fieldname] = d[fieldname].split(',')
			idx += 1	
			
		# Memory is a special case, as it is not reported in a standard way
		# We could have a memory per core figure '2500Mc', '4Gc', etc.
		# OR
		# We could have a memory per node figure '4000Mn', '32Gn', etc.
		# We need to normalise both cases so that all jobs can be reported
		# in the same way.
		if row == 0:
			
			CPUS = 0
			if d['AllocCPUS'] != 0:
				CPUS = d['AllocCPUS']
			else:
				CPUS = d['ReqCPUS']
				
			d['NodeList'] = self.expandnodelist(nodelist = d['NodeList'])
			d['MemoryPerCore'] = self.getMemoryPerCore(d['ReqMem'], CPUS, d['ReqNodes'], d['AllocNodes'])	
			d['TotalMemory'] = CPUS * d['MemoryPerCore']

		# Reserved and Elapsed time are also in a non-standard field type of
		# D-HH:MM:SS
		# This needs to be transformed into an object we can tally with others
		if row == 0:
			d['ReservedTime'] = self.fieldToDatetime(field = d['Reserved']).total_seconds() / 60
			d['ElapsedTime'] = self.fieldToDatetime(field = d['Elapsed']).total_seconds() / 60

		if row == 0:
			# If this is the first row of an sacct output, set it as
			# the 'leader' job entry
			self.job = d
			
		else:
			# Otherwise record this as a component of the the job
			self.subjobs.append(d)
	
	def getByState(self, state = None, start = None, end = None, expand_nodes = False):
		""" Return all of the jobs in a given state across all partitions """
		
		# If looking for failed jobs, expand the criteria to all 'abnormal' codes
		if state == 'F':
			state = FAIL_STATES
			
		if start and end:
			job_cmd = "sacct -X -p -a -S %s -E %s --state=%s --format=%s" % (start, end, state, FIELDS_SUMMARY)
		else:
			job_cmd = "sacct -X -p -a --state=%s --format=%s" % (state, FIELDS_SUMMARY)
		jobs = []
		try:
			p = subprocess.Popen(job_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			if p:
				output = p.stdout.read().split(b'\n')
				if len(output) > 3:
					for line in output[1:-1]:
						o = self.setrowSummary(stdout = line, expand_nodes = expand_nodes)
						if o:
							jobs.append(o)
			else:
				return False
		except Exception as e:
			print("Exception making subprocess call for job state %s" % state)
			print("Exception was %s" % e)
			print(traceback.format_exc())
			return False
			
		return jobs

	def getByNode(self, hostname = None, expand_nodes = False):
		""" Return all of the jobs currently on a given node """
		
		job_cmd = "sacct -X -p -a --nodelist=%s --state=R --format=%s" % (hostname, FIELDS_SUMMARY)	
		jobs = []
		try:
			p = subprocess.Popen(job_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			if p:
				output = p.stdout.read().split(b'\n')
				if len(output) > 3:
					for line in output[1:-1]:
						o = self.setrowSummary(stdout = line, expand_nodes = expand_nodes)
						if o:
							jobs.append(o)
			else:
				return False
		except Exception as e:
			print("Exception making subprocess call for jobs on node %s" % hostname)
			print("Exception was %s" % e)
			print(traceback.format_exc())
			return False

		return jobs

	def getByPartition(self, partition = None, state = "R", expand_nodes = False):
		""" Return all of the jobs on a given partition with a given slurm state code """
		
		job_cmd = "sacct -X -p -a --partition=%s --state=%s --format=%s" % (partition, state, FIELDS_SUMMARY)	
		jobs = []
		try:
			p = subprocess.Popen(job_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			if p:
				output = p.stdout.read().split(b'\n')
				if len(output) > 3:
					for line in output[1:-1]:
						o = self.setrowSummary(stdout = line, expand_nodes = expand_nodes)
						if o:
							jobs.append(o)
			else:
				return False
		except Exception as e:
			print("Exception making subprocess call for jobs on partition %s" % partition)
			print("Exception was %s" % e)
			print(traceback.format_exc())
			return False

		return jobs
	
	def get(self, jobid = None):
		""" Return the top-level information for a specific job - this only
		returns a single entry, use 'getAll()' to return sub-components """
		
		self.JobID = jobid
		
		job_cmd = "sacct -p -a -j %d --format=%s" % (jobid, FIELDS)
	
		try:
			p = subprocess.Popen(job_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			if p:
				# Parse stdout
				# First line are the field headers
				# Second line are the underline of the column names
				# Fields are delimited by '|'
				output = p.stdout.read().split(b'\n')

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
		except Exception as e:
			print("Exception making subprocess call for jobid %d" % jobid)
			print("Exception was %s" % e)
			print(traceback.format_exc())
			return False
