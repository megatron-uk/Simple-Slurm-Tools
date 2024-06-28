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

#############################################################
#
# A class for generating statistics from Slurm job data.
#
#############################################################
		
from lib.slurmcache import slurmCache
import lib.settings as settings
		
class SlurmStats():
	
	def __init__(self):
		""" Initialise the SlurmStats class """
		self.slurmcache = slurmCache()
		
	def generate_stats():
		""" Generate slurm stats for a given day. """
		
class SlurmStatsOLD():
	
	def __init__(self):
		# Initialise the class, if needed
		print("Initialising slurmDB Integration class")
		self.debug = settings.DEBUG
		self.slurmcache = slurmCache()

	def generate_stats(self, year = 2023, month = 1, day = 1, hours = [], minutes = []):
		""" Generate stats for a given day - using the hour/minutes granularity given. """
		""" See slurmsettings for use of the hours and minutes options """
		
		stats = []
		
		current_year = str(year)
		if month < 10:
			current_month = "0" + str(month)
		else:
			current_month = str(month)
		if day < 10:
			current_day = "0" + str(day)
		else:
			current_day = str(day)
		
		if self.debug:
			print("Generating stats for %s/%s/%s" % (current_year, current_month, current_day))
			print("- %d stats per day" % (len(hours)))
			print("- %d stats per hour" % (len(minutes)))
			
		for hour in hours:

			for minute in minutes:
				
				###########################################################
				#
				# Get the snapshot data for this sample period
				#
				# Snapshot data is a point-in-time, 1 second look at
				# the current number of cpu cores in use.
				# We use this to derive a '% utilisation' figure based
				# on how many cores are available, as derived from sinfo
				# calls at the current time.
				# Yes, it could be wildly innaccurate if your cluster spec
				# has changed over time. But without a regular running process
				# to log cluster capabilities, we can't do anything else
				# for historical 'percent in use / percent idle'.
				#
				###########################################################
				
				# Split off the seconds column
				minute_ = minute[0].split(':')[0]
				minute_ += ":01"
		
				start_snapshot_time = current_year + "-" + current_month + "-" + current_day + hour[0] + ":" + minute[0]
				end_snapshot_time = current_year + "-" + current_month + "-" + current_day + hour[0] + ":" + minute_
				
				if self.debug:
					print("- %s to %s [snapshot]" % (start_snapshot_time, end_snapshot_time))
				
				stat_data_snapshot = self.slurmcache.load(current_year, current_month, current_day, hour, minute, "generate_stats_snapshot")
				
				if stat_data_snapshot:
					if self.debug:
						print("- Persistent report cache hit! Returning on-disk snapshot data...")
				else:
					stat_data_snapshot = {
						'jobs_running' : [],
						'total_cores' : 0,
						'nodes' : {},
					}
					for q in settings.PARTITIONS:
						stat_data_snapshot[q] = { 'cores' : 0 }
						
					stat_data_snapshot['jobs_running'] = self.slurmjob.getByState(state = 'R', start = start_snapshot_time, end = end_snapshot_time, expand_nodes = True)
					
					# Count total number of cpu cores in use at this moment
					for j in stat_data_snapshot['jobs_running']:
						
						# Add to the total for the partition this job is running in
						stat_data_snapshot[j['Partition']]['cores'] += j['AllocCPUS']
						
						# Add to the overall total
						stat_data_snapshot['total_cores'] += j['AllocCPUS']
						
						########################################
						# Add up the number of cores this job 
						# is using on each of the nodes it is on.
						# THis will allow us to see the relative
						# utilisation of each node later on.
						for n in j['NodeList']:
							cores_per_node = int(j['AllocCPUS'] / j['AllocNodes'])
							if n not in stat_data_snapshot['nodes']:
								stat_data_snapshot['nodes'][n] = {'cores' : 0 }
							stat_data_snapshot['nodes'][n]['cores'] += cores_per_node
						
					#if self.debug:
					#	print("- Creating persistent on-disk snapshot cache")
					self.slurmcache.store(current_year, current_month, current_day, hour, minute, "generate_stats_snapshot", stat_data_snapshot)
				
				###########################################################
				#
				# Get the main slurm data for this sample period
				#
				###########################################################
				
				start_time = current_year + "-" + current_month + "-" + current_day + hour[0] + ":" + minute[0]
				end_time = current_year + "-" + current_month + "-" + current_day + hour[1] + ":" + minute[1]
				
				if self.debug:
					print("- %s to %s" % (start_time, end_time))
	
				stat_data = self.slurmcache.load(current_year, current_month, current_day, hour, minute, "generate_stats")
								
				if stat_data:
					if self.debug:
						print("- Persistent report cache hit! Returning on-disk data...")
				else:
					
	
					stat_data = {
						'start_time' : start_time,
						'end_time' : end_time,
						'total_cores' : 0,
						'total_memory' : 0,
						'idle_cores' : 0,
						'cpu_time_min' : 9999999,
						'cpu_time_max' : 0,
						'cpu_time_median' : 0,
						'cpu_time_75' : 0,
						'cpu_time_list' : [],
						'cpu_time_total' : 0,
						'nodes_min' : 999999,
						'nodes_max' : 0,
						'nodes_median' : 0,
						'nodes_75' : 0,
						'nodes_list' : [],
						'nodes_total' : 0,
						'cores_min' : 999999,
						'cores_max' : 0,
						'cores_median' : 0,
						'cores_75' : 0,
						'cores_list' : [],
						'mem_core_min' : 999999,
						'mem_core_max' : 0,
						'mem_core_median' : 0,
						'mem_core_75' : 0,
						'mem_core_list' : [],
						'mem_core_total' : 0,
						'mem_job_min' : 999999,
						'mem_job_max' : 0,
						'mem_job_median' : 0,
						'mem_job_75' : 0,
						'mem_job_list' : [],
						'mem_job_total' : 0,
						'jobs_running' : [],
						'jobs_running_total' : 0,
						'jobs_pending' : [],
						'jobs_pending_total' : 0,
						'jobs_completed' : [],
						'jobs_completed_total' : 0,
						'jobs_failed' : [],
						'jobs_failed_total' : 0,
					}
					
					for q in settings.PARTITIONS:
						stat_data[q] = { 'jobs' : 0, 'pending' : 0, 'failed' : 0}
		
					# Node status
		
					# Total jobs that were running
					stat_data['jobs_running'] = self.slurmjob.getByState(state = 'R', start = start_time, end = end_time, expand_nodes = False)
					stat_data['jobs_running_total'] = len(stat_data['jobs_running'])
					
					# Total jobs that were pending
					#stat_data['jobs_pending'] = sj.getByState(state = 'PD', start = start_time, end = end_time, expand_nodes = False)
					#stat_data['jobs_pending_total'] = len(stat_data['jobs_pending'])
					
					# Total jobs that finished in this period
					stat_data['jobs_completed'] = self.slurmjob.getByState(state = 'CD', start = start_time, end = end_time, expand_nodes = False)
					stat_data['jobs_completed_total'] = len(stat_data['jobs_completed'])
					
					# Total jobs that failed in this period
					stat_data['jobs_failed'] = self.slurmjob.getByState(state = 'F', start = start_time, end = end_time, expand_nodes = False)
					stat_data['jobs_failed_total'] = len(stat_data['jobs_failed'])
	
					# Update partition totals				
					for job in stat_data['jobs_pending']:
						if job['Partition'] not in stat_data:
							print("WARNING!!! This pending job has a partition listed which we do not recognise!")
							print("Job: %s" % job['JobID'])
							print("Partition: [%s]" % job['Partition'])
							print("... IGNORING this job.....")
						else:
							stat_data[job['Partition']]['pending'] += 1
						
					for job in stat_data['jobs_failed']:
						if job['Partition'] not in stat_data:
							print("WARNING!!! This failed job has a partition listed which we do not recognise!")
							print("Job: %s" % job['JobID'])
							print("Partition: [%s]" % job['Partition'])
							print("... IGNORING this job.....")
						else:
							stat_data[job['Partition']]['failed'] += 1
					
					for job in stat_data['jobs_running']:
						#########################################
						
						if job['Partition'] not in stat_data:
							print("WARNING!!! This running job has a partition listed which we do not recognise!")
							print("Job: %s" % job['JobID'])
							print("Partition: [%s]" % job['Partition'])
							print("... IGNORING this job.....")
						else:
							stat_data[job['Partition']]['jobs'] += 1
						
						########################################
						# Calculate total allocated cores for this time period
						stat_data['total_cores'] += job['AllocCPUS']
						# THIS DOES NOT WORK - since there are jobs that
						# overlap in the granularity of the time period, we
						# are effectively double/triple counting processor
						# utilisation. 
					
						# Update min cores value
						if job['AllocCPUS'] < stat_data['cores_min']:
							stat_data['cores_min'] = job['AllocCPUS']
						if job['AllocCPUS'] > stat_data['cores_max']:
							stat_data['cores_max'] = job['AllocCPUS']
						stat_data['cores_list'].append(job['AllocCPUS'])
					
						#########################################
						# CPU times
						if job['CPUTimeRaw'] < stat_data['cpu_time_min']:
							stat_data['cpu_time_min'] = job['CPUTimeRaw']
						if job['CPUTimeRaw'] > stat_data['cpu_time_max']:
							stat_data['cpu_time_max'] = job['CPUTimeRaw']
						stat_data['cpu_time_total'] += job['CPUTimeRaw']	
						stat_data['cpu_time_list'].append(job['CPUTimeRaw'])
					
						#########################################
						# nodes
						if job['AllocNodes'] < stat_data['nodes_min']:
							stat_data['nodes_min'] = job['AllocNodes']
						if job['AllocNodes'] > stat_data['nodes_max']:
							stat_data['nodes_max'] = job['AllocNodes']
						stat_data['nodes_total'] += job['AllocNodes']	
						stat_data['nodes_list'].append(job['AllocNodes'])
					
						#########################################
						# Allocated memory per job
						job_memory = job['MemoryPerCore'] * job['AllocCPUS']
						stat_data['total_memory'] += job_memory
					
						if job['MemoryPerCore'] < stat_data['mem_core_min']:
							stat_data['mem_core_min'] = job['MemoryPerCore']
						if job['MemoryPerCore'] > stat_data['mem_core_max']:
							stat_data['mem_core_max'] = job['MemoryPerCore']
						stat_data['mem_core_total'] += job['MemoryPerCore']
						stat_data['mem_core_list'].append(job['MemoryPerCore'])
							
						########################################
						# Allocated memory per core
						if job_memory < stat_data['mem_job_min']:
							stat_data['mem_job_min'] = job_memory
						if job_memory > stat_data['mem_job_max']:
							stat_data['mem_job_max'] = job_memory
						stat_data['mem_job_total'] += job_memory
						stat_data['mem_job_list'].append(job_memory)
						
					##########################################################
					#
					# Generate median values
					#
					##########################################################
						
					
					if len(stat_data['jobs_running']) > 0:
						
						# Update median memory per core value
						stat_data['mem_core_median'] = stat_data['mem_core_total'] / len(stat_data['jobs_running'])
					
						# Update median memory per job value
						stat_data['mem_job_median'] = stat_data['mem_job_total'] / len(stat_data['jobs_running'])
					
						# Update median cores per job value
						stat_data['cores_median'] = stat_data['total_cores'] / len(stat_data['jobs_running'])
					
						# Update median nodes per job value
						stat_data['nodes_median'] = stat_data['nodes_total'] / len(stat_data['jobs_running'])
					
						# Update median cpu time per job value
						stat_data['cpu_time_median'] = stat_data['cpu_time_total'] / len(stat_data['jobs_running'])
					
					
					##########################################################
					#
					# Generate 75% waterline values
					#
					##########################################################
					
					# Update 75% percentile waterline for memory per core
					stat_data['mem_core_list'].sort()
					if len(stat_data['mem_core_list']) > 0:
						idx = int(len(stat_data['mem_core_list']) * 0.75)
						stat_data['mem_core_75'] = stat_data['mem_core_list'][idx]
					
					# Update 75% percentile waterline for memory per job
					stat_data['mem_job_list'].sort()
					if len(stat_data['mem_job_list']) > 0:
						idx = int(len(stat_data['mem_job_list']) * 0.75)
						stat_data['mem_job_75'] = stat_data['mem_job_list'][idx]
					
					# Update 75% percentile waterline for cores
					stat_data['cores_list'].sort()
					if len(stat_data['cores_list']) > 0:
						idx = int(len(stat_data['cores_list']) * 0.75)
						stat_data['cores_75'] = stat_data['cores_list'][idx]
			
					# Update 75% percentile waterline for cpu time
					stat_data['cpu_time_list'].sort()
					if len(stat_data['cpu_time_list']) > 0:
						idx = int(len(stat_data['cpu_time_list']) * 0.75)
						stat_data['cpu_time_75'] = stat_data['cpu_time_list'][idx]
			
					# Update 75% percentile waterline for nodes
					stat_data['nodes_list'].sort()
					if len(stat_data['nodes_list']) > 0:
						idx = int(len(stat_data['nodes_list']) * 0.75)
						stat_data['nodes_75'] = stat_data['nodes_list'][idx]
		
					#if self.debug:
					#	print("- Creating persistent on-disk cache")
					self.slurmcache.store(current_year, current_month, current_day, hour, minute, "generate_stats", stat_data)
		
				stat_data['snapshot'] = stat_data_snapshot
				stats.append(stat_data)
		
		if self.debug:
			print("- All Done")
		return stats

	def generate_summary(self, stats = []):
		""" Generate a summary dict using a stats list """

		summary = {}
		
		# Get current node details from sinfo
		if self.debug:
			print("Getting detailed node data...")
		all_nodes = self.slurmnode.getNodes()
		all_node_data = {}
		total_cores_available = 0
		for n in all_nodes:
			node_data = self.slurmnode.getNode(hostname = n)

			# Add empty lists to record used/free cores at each sample point
			node_data['cores_used'] = []
			node_data['cores_free'] = []
			all_node_data[n] = node_data
			
			# Add this nodes total cores to the total available for the cluster			
			total_cores_available += node_data['CPUs']
			
		if self.debug:
			print("- Done")
			
		# In this list we will keep a copy of node_data for each reporting period
		node_details = []
		
		if self.debug:
			print("Generating a summary...")
		
		# Update for todays figures
		today = {
			'total_memory' : 0,
			'total_cores' : 0,
			'idle_cores' : 0,
			'cores_min' : 999999,
			'cores_max' : 0,
			'cores_median' : 0,
			'cores_75' : 0,
			'cores_list' : [],
			'mem_job_min' : 999999,
			'mem_job_max' : 0,
			'mem_job_median' : 0,
			'mem_job_75' : 0,
			'mem_job_list' : [],
			'mem_core_min' : 999999,
			'mem_core_max' : 0,
			'mem_core_median' : 0,
			'mem_core_75' : 0,
			'mem_core_list' : [],
			'cpu_time_total' : 0,
			'cpu_time_min' : 999999,
			'cpu_time_max' : 0,
			'cpu_time_median' : 0,
			'cpu_time_75' : 0,
			'cpu_time_list' : [],
			'jobs_running_max' : 0,
			'jobs_running_min' : 999999,
			'jobs_pending_max' : 0,
			'jobs_pending_min' : 999999,
			'jobs_completed_total' : 0,
			'jobs_failed_total' : 0,
			'nodes_min' : 0,
			'nodes_max' : 0,
			'nodes_median' : 0,
			'nodes_75' : 0,
			'nodes_list' : [],
			'use_min' : 99999,
			'use_min_pc' : 0,
			'use_max' : 0,
			'use_max_pc' : 0,
			'use_median' : 0,
			'use_median_pc' : 0,
			'use_list' : [],
		}
		for s in stats:
						
			period_cores_use = 0
			s['use_list'] = []
			for n in all_nodes:
				
				# Was this node in use at this sample period
				if n in s['snapshot']['nodes']:
					# Yes, add the number of cores in use
					cores_used = s['snapshot']['nodes'][n]['cores'] 
				else:
					# No, so set cores in use as 0
					cores_used = 0
					
				all_node_data[n]['cores_used'].append(cores_used)
				
				cores_free = all_node_data[n]['CPUs'] - cores_used
				if cores_free < 0:
					all_node_data[n]['cores_free'].append(0)
				else:
					all_node_data[n]['cores_free'].append(cores_free)
					
				# Record cores used
				s['use_list'].append(cores_used)
				period_cores_use += cores_used
				
			# update max/min total core use for this sample period
			if period_cores_use > today['use_max']:
				today['use_max'] = period_cores_use
				
			if period_cores_use < today['use_min']:
				today['use_min'] = period_cores_use
			
			# Update highest concurrent use of cores
			if s['total_cores'] > today['total_cores']:
				today['total_cores'] = s['total_cores']
			if s['idle_cores'] > today['idle_cores']:
				today['idle_cores'] = s['idle_cores']
			if s['total_memory'] > today['total_memory']:
				today['total_memory'] = s['total_memory']
			# Jobs
			if len(s['jobs_running']) < today['jobs_running_min']:
				today['jobs_running_min'] = len(s['jobs_running'])
				
			if len(s['jobs_running']) > today['jobs_running_max']:
				today['jobs_running_max'] = len(s['jobs_running'])
				
			if len(s['jobs_pending']) < today['jobs_pending_min']:
				today['jobs_pending_min'] = len(s['jobs_pending'])
				
			if len(s['jobs_pending']) > today['jobs_pending_max']:
				today['jobs_pending_max'] = len(s['jobs_pending'])
			
			today['jobs_completed_total'] += s['jobs_completed_total']
			today['jobs_failed_total'] += s['jobs_failed_total']
			
			# Absolute lowest cores for today
			if s['cores_min'] < today['cores_min']:
				today['cores_min'] = s['cores_min']
			
			# Absolute highest cores for today
			if s['cores_max'] > today['cores_max']:
				today['cores_max'] = s['cores_max']
			
			# Lowest mem per job for today
			if s['mem_job_min'] < today['mem_job_min']:
				today['mem_job_min'] = s['mem_job_min']
			
			# Highest mem per job for today
			if s['mem_job_max'] > today['mem_job_max']:
				today['mem_job_max'] = s['mem_job_max']
			
			# Lowest mem per core for today
			if s['mem_core_min'] < today['mem_core_min']:
				today['mem_core_min'] = s['mem_core_min']
			
			# Highest mem per core for today
			if s['mem_core_max'] > today['mem_core_max']:
				today['mem_core_max'] = s['mem_core_max']
				
			# Lowest cpu time for today
			if s['mem_core_min'] < today['mem_core_min']:
				today['mem_core_min'] = s['mem_core_min']
			
			# Highest nodes for today
			if s['nodes_max'] > today['nodes_max']:
				today['nodes_max'] = s['nodes_max']
				
			# Lowest nodes for today
			if s['nodes_min'] < today['nodes_min']:
				today['nodes_min'] = s['nodes_min']
			
			# highest cpu time for today
			if s['cpu_time_max'] > today['cpu_time_max']:
				today['cpu_time_max'] = s['cpu_time_max']
			
			# Lowest cpu time for today
			if s['cpu_time_min'] < today['cpu_time_min']:
				today['cpu_time_min'] = s['cpu_time_min']
			
			# Update all lists of cores, mem-per-job and mem-per-core for all of todays data
			today['cores_list'] += s['cores_list']
			today['mem_job_list'] += s['mem_job_list']
			today['mem_core_list'] += s['mem_core_list']
			today['cpu_time_list'] += s['cpu_time_list']
			today['nodes_list'] += s['nodes_list']
			today['use_list'] += s['use_list']
		
		# Median value for todays core counts
		for v in today['cores_list']:
			today['cores_median'] += v
		if len(today['cores_list']) > 0:
			today['cores_median'] = today['cores_median'] / len(today['cores_list'])
		print("- Median Cores per job in this period: %d" % (today['cores_median']))
		
		# Median value for todays mem-per-core counts
		for v in today['mem_core_list']:
			today['mem_core_median'] += v
		if len(today['mem_core_list']) > 0:
			today['mem_core_median'] = today['mem_core_median'] / len(today['mem_core_list'])
		print("- Median Mem per core in this period: %d" % (today['mem_core_median']))
		
		# Median value for todays mem-per-job counts
		for v in today['mem_job_list']:
			today['mem_job_median'] += v
		if len(today['mem_job_list']) > 0:
			today['mem_job_median'] = today['mem_job_median'] / len(today['mem_job_list'])
		print("- Median Mem per job in this period: %d" % (today['mem_job_median']))
		
		# Median value for todays cputime counts
		for v in today['cpu_time_list']:
			today['cpu_time_total'] += v
			today['cpu_time_median'] += v
		if len(today['cpu_time_list']) > 0:
			today['cpu_time_median'] = today['cpu_time_median'] / len(today['cpu_time_list'])
		print("- Median CPU time per job in this period: %d" % (today['cpu_time_median']))
		
		# Median value for todays node counts
		for v in today['nodes_list']:
			today['nodes_median'] += v
		if len(today['nodes_list']) > 0:
			today['nodes_median'] = today['nodes_median'] / len(today['nodes_list'])
		print("- Median Nodes per job in this period: %d" % (today['nodes_median']))
		
		# Median value for todays utilisation
		for v in today['use_list']:
			today['use_median'] += v
		if len(today['use_list']) > 0:
			today['use_median'] = (today['use_median'] / (total_cores_available * len(stats))) * total_cores_available
		print("- Median CPU cores in use across in this period: %d" % (today['use_median']))
		
		if total_cores_available > 0:
			today['use_median_pc'] = (today['use_median'] / total_cores_available) * 100
			today['use_max_pc'] = (today['use_max'] / total_cores_available) * 100
			today['use_min_pc'] = (today['use_min'] / total_cores_available) * 100
		
		# 75% waterline for cores for today
		today['cores_list'].sort()
		if len(today['cores_list']) > 0:
			idx = int(len(today['cores_list']) * 0.75)
			today['cores_75'] = today['cores_list'][idx]
		
		# 75% waterline for mem-per-core for today
		today['mem_core_list'].sort()
		if len(today['mem_core_list']) > 0:
			idx = int(len(today['mem_core_list']) * 0.75)
			today['mem_core_75'] = today['mem_core_list'][idx]
		
		# 75% waterline for mem-per-job for today
		today['mem_job_list'].sort()
		if len(today['mem_job_list']) > 0:
			idx = int(len(today['mem_job_list']) * 0.75)
			today['mem_job_75'] = today['mem_job_list'][idx]
		
		# 75% waterline for nodes for today
		today['nodes_list'].sort()
		if len(today['nodes_list']) > 0:
			idx = int(len(today['nodes_list']) * 0.75)
			today['nodes_75'] = today['nodes_list'][idx]
			
		# 75% waterline for cpu time for today
		today['cpu_time_list'].sort()
		if len(today['cpu_time_list']) > 0:
			idx = int(len(today['cpu_time_list']) * 0.75)
			today['cpu_time_75'] = today['cpu_time_list'][idx]
		
		if self.debug:
			print("- Done")
		
		# Generate unique list of jobs
		job_ids = {}
		job_list = []
		if self.debug:
			print("Generating job list for this period...")
		for s in stats:
			for j in s['jobs_running']:
				if j['JobID'] not in job_ids:
					job_ids[j['JobID']] = j['JobID'] 
					job_list.append(j)
		if self.debug:
			print("- Total jobs for this period: %d" % len(job_ids.keys()))
			print("- Done")
			
		# Generate list of users
		user_ids = []
		user_jobs = {}
		if self.debug:
			print("Generating user list for this period...")
		for j in job_list:
			if j['User'] not in user_ids:
				user_jobs[j['User']] = {
					'jobs' 				: [],
					'total_jobs' 		: 0,
					'total_cpu_time' 	: 0,
					'total_cores' 		: 0,
					'total_memory' 		: 0,
					'total_memory_core' : 0,
					'total_nodes' 		: 0,
					'avg_cpu_time_job' 	: 0,
					'avg_nodes_job' 	: 0,
					'avg_cores_job' 	: 0,
					'avg_memory_job' 	: 0,
					'avg_memory_core' 	: 0,
				}
				user_ids.append(j['User'])
			user_jobs[j['User']]['jobs'].append(j)
		if self.debug:
			print("- Total users for this period: %d" % len(user_ids))
		
		user_job_details = []
		for uid in user_jobs.keys():
			user_jobs[uid]['total_jobs'] = len(user_jobs[uid]['jobs'])
			user_jobs[uid]['user'] = uid

			for j in user_jobs[uid]['jobs']:
				user_jobs[uid]['total_cpu_time'] += j['CPUTimeRaw']
				user_jobs[uid]['total_cores'] += j['AllocCPUS']
				user_jobs[uid]['total_memory'] += j['TotalMemory']
				user_jobs[uid]['total_memory_core'] += j['MemoryPerCore']
				user_jobs[uid]['total_nodes'] += j['AllocNodes']
			
			if user_jobs[uid]['total_jobs'] > 0:
				user_jobs[uid]['avg_cpu_time_job'] = user_jobs[uid]['total_cpu_time'] / user_jobs[uid]['total_jobs']
				user_jobs[uid]['avg_nodes_job'] = user_jobs[uid]['total_nodes'] / user_jobs[uid]['total_jobs']
				user_jobs[uid]['avg_cores_job'] = user_jobs[uid]['total_cores'] / user_jobs[uid]['total_jobs']
				user_jobs[uid]['avg_memory_job'] = user_jobs[uid]['total_memory'] / user_jobs[uid]['total_jobs']
				user_jobs[uid]['avg_memory_core'] = user_jobs[uid]['total_memory_core'] / user_jobs[uid]['total_jobs']
		
			user_job_details.append(user_jobs[uid])
		
			#if self.debug:
			#	print("-- %16s Totals: Jobs [%5d] Cores [%5d] Memory/Job [%8d] Memory/Core [%8d] Nodes [%5d] CPU [%16d]" % (uid, user_jobs[uid]['total_jobs'], user_jobs[uid]['total_cores'], user_jobs[uid]['total_memory'], user_jobs[uid]['total_memory_core'], user_jobs[uid]['total_nodes'], user_jobs[uid]['total_cpu_time']))
			#	print("-- %16s Median: ---- [-----] Cores [%5d] Memory/Job [%8d] Memory/Core [%8d] Nodes [%5d] CPU [%16d]" % (uid, user_jobs[uid]['avg_cores_job'], user_jobs[uid]['avg_memory_job'], user_jobs[uid]['avg_memory_core'], user_jobs[uid]['avg_nodes_job'], user_jobs[uid]['avg_cpu_time_job']))
		if self.debug:
			print("- Done")
		
		# League tables
		if self.debug:
			print("Generating top %d league tables..." % settings.LEAGUE_TABLE_SIZE)
		top_jobs = sorted(user_job_details, key=lambda x: x['total_jobs'], reverse=True)[0:settings.LEAGUE_TABLE_SIZE]		
		top_cpu_time = sorted(user_job_details, key=lambda x: x['total_cpu_time'], reverse=True)[0:settings.LEAGUE_TABLE_SIZE]
		top_cores = sorted(user_job_details, key=lambda x: x['total_cores'], reverse=True)[0:settings.LEAGUE_TABLE_SIZE]
		top_memory = sorted(user_job_details, key=lambda x: x['total_memory'], reverse=True)[0:settings.LEAGUE_TABLE_SIZE]
		top_memory_cores = sorted(user_job_details, key=lambda x: x['total_memory_core'], reverse=True)[0:settings.LEAGUE_TABLE_SIZE]
		top_nodes = sorted(user_job_details, key=lambda x: x['total_nodes'], reverse=True)[0:settings.LEAGUE_TABLE_SIZE]
		
		top_median_cpu_time = sorted(user_job_details, key=lambda x: x['avg_cpu_time_job'], reverse=True)[0:settings.LEAGUE_TABLE_SIZE]
		top_median_cores = sorted(user_job_details, key=lambda x: x['avg_cores_job'], reverse=True)[0:settings.LEAGUE_TABLE_SIZE]
		top_median_memory = sorted(user_job_details, key=lambda x: x['avg_memory_job'], reverse=True)[0:settings.LEAGUE_TABLE_SIZE]
		top_median_memory_cores = sorted(user_job_details, key=lambda x: x['avg_memory_core'], reverse=True)[0:settings.LEAGUE_TABLE_SIZE]
		top_median_nodes = sorted(user_job_details, key=lambda x: x['avg_nodes_job'], reverse=True)[0:settings.LEAGUE_TABLE_SIZE]
		if self.debug:
			print("- Done")
			
		summary['node_details'] = all_node_data
		summary['today'] = today
		summary['user_job_details'] = user_job_details
		summary['job_list'] = job_list
		summary['top_jobs'] = top_jobs
		summary['top_cpu_time'] = top_cpu_time
		summary['top_cores'] = top_cores
		summary['top_memory'] = top_memory
		summary['top_memory_cores'] = top_memory_cores
		summary['top_nodes'] = top_nodes
		summary['top_median_cpu_time'] = top_median_cpu_time
		summary['top_median_cores'] = top_median_cores
		summary['top_median_memory'] = top_median_memory
		summary['top_median_memory_cores'] = top_median_memory_cores
		summary['top_median_nodes'] = top_median_nodes

		if self.debug:
			print("- All Done")

		return summary