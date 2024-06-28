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

import grp
import pwd
import os
import subprocess

####################################################################
#
# Simple routines to work with Posix users and groups
#
####################################################################

AUTHOR		= "John Snowdon"
URL			= "https://github.com/megatron-uk/Simple-Slurm-Tools"

def get_groups(groups = None):
	""" Turn a comma seperated string of group names into a list of real unix group names. """
	groupnames = []
	for group in groups.split(","):
		if len(group) > 1:
			try:
				# Is this a valid posix group?
				grpstruct = grp.getgrnam(group.lstrip().rstrip())
				groupnames.append(grpstruct.gr_name)	
			except Exception as err:
				pass
	return groupnames

def get_users(users = None):
	""" Turn a comma seperated string of usernames into a list of usernames. """
	usernames = []
	for user in users.split(","):
		if len(user) > 1:
			try:
				# Is this a valid posix username?
				usrstruct = pwd.getpwnam(user.lstrip().rstrip())
				usernames.append(usrstruct.pw_name)
			except Exception as err:
				pass
	return usernames

def get_users_from_groups(groups = []):
	""" Get a list of usernames from a group list """
	usernames = []
	for group in groups:
		if group:
			job_cmd = "getent group %s | awk -F: \'{print $4}\'" % group
			try:
				process = subprocess.Popen(job_cmd, shell=True,
						stdin=subprocess.PIPE, stdout=subprocess.PIPE,
						stderr=subprocess.STDOUT)
				if process:
					output = process.stdout.read().rstrip().split(b'\n')
					if len(output) > 0:
						for line in output:
							line = line.decode()
							line = line.replace(';', ',')
							users = get_users(line)
							for user in users:
								if user not in usernames:
									usernames.append(user)
			except Exception as err:
				pass
	return usernames
	
def get_user_quota(find_type = "normal", user_name = "myname", quota_directory = "/mydir"):
	""" Get quota details for a given username and mount point """
	
	if FIND_TYPE == "lfs":
		job_cmd = f"lfs quota -u {user_name} 2>/dev/null {quota_directory} | grep {quota_directory}"
	else:
		job_cmd = f"quota -u {user_name} --show-mntpoint -w 2>/dev/null | grep {quota_directory}"
	
	data = {
		'username'	: user_name,
		'dirname'	: quota_directory,
		'quota'		: 0,
		'limit'		: 0,
		'overquota'	: False,
	}
	
	try:
		if process:
			output = process.stdout.read()
			if len(output) > 1:
				fields = output.decode().split()
				if len(fields) > 5:
					if FIND_TYPE == "lfs":
						# Lustre based filesystem quotas
						QUOTA_FIELD = 1
						LIMIT_FIELD = 2
					else:
						# Normal Linux quota subsystem
						QUOTA_FIELD = 2
						LIMIT_FIELD = 3

					# Handle quota useage fields which show over-quota status
					if '*' in fields[QUOTA_FIELD]:
						data['quota'] = int(fields[QUOTA_FIELD].split('*')[0])
						data['overquota'] = True						
					else:
						data['quota'] = int(fields[QUOTA_FIELD])
						
					# Handle limit fields which show over-quota status
					if '*' in fields[LIMIT_FIELD]:
						data['limit'] = int(fields[LIMIT_FIELD].split('*')[0])
						data['overquota'] = True
					else:
						data['limit'] = int(fields[LIMIT_FIELD])

		return(data)

	except Exception as err:
		pass
		return False
	
def get_group_quota(find_type = "normal", group_name = "mygroup", quota_directory = "/mydir"):
	""" Get quota details for a given group and mount point """
	
	if find_type == "lfs":
		job_cmd = f"lfs quota -g {group_name} 2>/dev/null {quota_directory} | grep {quota_directory}"
	else:
		job_cmd = f"quota -g {group_name} --show-mntpoint -w 2>/dev/null | grep {quota_directory}"
	
	data = {
		'group'		: group_name,
		'dirname'	: quota_directory,
		'quota'		: 0,
		'limit'		: 0,
		'overquota'	: False
	}
	
	try:
		process = subprocess.Popen(job_cmd, shell=True,
			stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT)
		if process:
			output = process.stdout.read()
			if len(output) > 1:
				fields = output.decode().split()
				if len(fields) > 5:
					if FIND_TYPE == "lfs":
						# Lustre based filesystem quotas
						QUOTA_FIELD = 1
						LIMIT_FIELD = 2
					else:
						# Normal Linux quota subsystem
						QUOTA_FIELD = 2
						LIMIT_FIELD = 3
	
					# Handle quota useage fields which show over-quota status
					if '*' in fields[QUOTA_FIELD]:
						data['quota'] = int(fields[QUOTA_FIELD].split('*')[0])
						data['overquota'] = True
					else:
						data['quota'] = int(fields[QUOTA_FIELD])
						
					# Handle limit fields which show over-quota status
					if '*' in fields[LIMIT_FIELD]:
						data['limit'] = int(fields[LIMIT_FIELD].split('*')[0])
						data['overquota'] = True
					else:
						data['limit'] = int(fields[LIMIT_FIELD])
					
		return(data)

	except Exception as err:
		return False

def get_group_utilisation(find_type = "normal", group_name = "mygroup", quota_directory = "/mydir", invert = False, cmd_only = False):
	""" Uses 'find' to calculate the space utilisation of an entire directory tree by a given unix group """
	
	if find_type == "generic":
		if invert:
			# Find everything NOT owned by the group
			job_cmd = f"find {quota_directory} -not -group {group_name} 2>/dev/null"
		else:
			job_cmd = f"find {quota_directory} -group {group_name} 2>/dev/null"
		
	if find_type == "lfs":
		if invert:
			# Find everything NOT owned by the group
			job_cmd = f"lfs find {quota_directory} -not -group {group_name} 2>/dev/null"
		else:
			job_cmd = f"lfs find {quota_directory} -group {group_name} 2>/dev/null"
	
	if cmd_only:
		return job_cmd
	
	data = {
		'group'		: group_name,
		'dirname'	: quota_directory,
		'quota'		: 0,
		'limit'		: 0,
		'files'		: []
	}
	
	try:
		process = subprocess.Popen(job_cmd, shell=True,
					stdin=subprocess.PIPE, stdout=subprocess.PIPE,
					stderr=subprocess.STDOUT)
		if process:
			output = process.stdout.read().rstrip().split(b'\n')
			if len(output) > 1:
				found_files_b = output
				found_files = []
				for f in found_files_b:
					try:
						found_files.append(f.decode())
					except Exception as err:
						# In case any files have names that we cannot decode
						#print(f"Error, {err}")
						pass
				# Sum the total capacity used by each file
				for f in found_files:
					try:
						file_data = os.stat(f)
						data['files'].append(f)
						data['quota'] = data['quota'] + file_data.st_size
					except:
						pass
					
				# st_size is in bytes, so store as kbytes
				if data['quota'] > 1024:
					data['quota'] = int(data['quota'] / 1024)
				else:
					data['quota'] = 0
				
		return data

	except Exception as err:
		return False
		
def get_user_utilisation(find_type = "normal", user_name = "myuser", quota_directory = "/mydir", cmd_only = False):
	""" Report user utilisation of a given directory tree """
	
	
	if find_type == "generic":
		job_cmd = f"find {quota_directory} -user {user_name} 2>/dev/null"
	if find_type == "lfs":
		job_cmd = f"lfs find {quota_directory} -user {user_name} 2>/dev/null"
	
	if cmd_only:
		return job_cmd
	
	data = {
		'username'	: user_name,
		'dirname'	: quota_directory,
		'quota'		: 0,
		'limit'		: 0
	}
	
	try:
		process = subprocess.Popen(job_cmd, shell=True,
					stdin=subprocess.PIPE, stdout=subprocess.PIPE,
					stderr=subprocess.STDOUT)
		if process:
			output = process.stdout.read().rstrip().split(b'\n')
			if len(output) > 1:
				found_files_b = output
				found_files = []
				for f in found_files_b:
					try:
						found_files.append(f.decode())
					except Exception as e:
						# In case any files have names that we cannot decode
						#print(f"Error, {e}")
						pass
				# Sum the total capacity used by each file
				for f in found_files:
					try:
						file_data = os.stat(f)
						data['quota'] = data['quota'] + file_data.st_size
					except Exception as err:
						pass
					
				# st_size is in bytes, so store as kbytes
				if data['quota'] > 1024:
					data['quota'] = int(data['quota'] / 1024)
				else:
					data['quota'] = 0
							
		return(data)

	except Exception as err:
		return False
		
def get_user_orphaned_files(find_type = "normal", username_list = None, quota_directory = "/mydir", cmd_only = False):
	""" Get a list of files which are owned by users other than those in the provided username_list. """
	
	if find_type == "generic":
		if len(username_list) == 1:
			# group with more than one name
			job_cmd = f"find {quota_directory} -not -user {username_list[0]} 2>/dev/null"
		else:
			# group with one name
			job_cmd = f"find {quota_directory} "
			for u in username_list:
				job_cmd = job_cmd + "-not -user " + u + " -a "
				
			# trim trailing "-a "
			job_cmd = job_cmd[:-3] + " 2>/dev/null"
			
	if find_type == "lfs":
		if len(username_list) == 1:
			# group with more than one name
			job_cmd = f"lfs find {quota_directory} -not -user {username_list[0]} 2>/dev/null"
		else:
			# group with one name
			job_cmd = f"find {quota_directory} "
			for u in username_list:
				job_cmd = job_cmd + "-not -user " + u + " -a "
				
			# trim trailing "-a "
			job_cmd = job_cmd[:-3] + " 2>/dev/null"
	
	if cmd_only:
		return job_cmd
	
	data = {
		'files' : [],	# A list of files that are found
		'users' : {},	# A dictionary of users whose files are found, including space utilisation for each
		'quota' : 0		# Sum of the entire space utilisation of the found files
	}
	
	try:
		process = subprocess.Popen(job_cmd, shell=True,
					stdin=subprocess.PIPE, stdout=subprocess.PIPE,
					stderr=subprocess.STDOUT)
		if process:
			output = process.stdout.read().rstrip().split(b'\n')
			if len(output) > 1:
				found_files_b = output
				found_files = []
				for f in found_files_b:
					try:
						found_files.append(f.decode())
					except Exception as e:
						# In case any files have names that we cannot decode
						#print(f"Error, {e}")
						pass
				# Sum the total capacity used by each file
				for f in found_files:
					try:
						file_data = os.stat(f)
						# Record the filename
						data['files'].append(f)
						
						uid = file_data.st_uid
						gid = file_data.st_gid
						if uid not in data['users']:
							data['users'][uid] = {
								'files' : [],
								'username' : "",
								'uid' : uid,
								'quota' : 0
							}
							
						data['users'][uid]['files'].append(f)
						data['users'][uid]['quota'] = data['users'][uid]['quota'] + int(file_data.st_size / 1024)
						
						# INcrease the count of space used
						data['quota'] = data['quota'] + file_data.st_size
					except Exception as err:
						pass
					
				# st_size is in bytes, so store as kbytes
				if data['quota'] > 1024:
					data['quota'] = int(data['quota'] / 1024)
				else:
					data['quota'] = 0
					
				# Map uid to username for all found
				# uids
				for uid in data['users']:
					pass
							
		return(data)

	except Exception as err:
		return False
	
	