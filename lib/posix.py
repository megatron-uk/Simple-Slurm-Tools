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
	
	if find_type == "lfs":
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
		process = subprocess.Popen(job_cmd, shell=True,
						stdin=subprocess.PIPE, stdout=subprocess.PIPE,
						stderr=subprocess.STDOUT)
		if process:
			output = process.stdout.read()
			if len(output) > 1:
				fields = output.decode().split()
				if len(fields) > 5:
					if find_type == "lfs":
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
		print("ERROR (get_user_quota): %s" % err)
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
					if find_type == "lfs":
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
		print("ERROR (get_group_quota): %s" % err)
		return False

def decode_ls_orphaned_files(ls_output = "", username_list = []):
	""" Decode a block of -aslLR output, recording files which *do not* belong to a list of usernames """

	ls_data = []
	
	# Field position in an ls -lR output
	file_size_pos = 0
	unix_perms_pos = 1
	files_total_pos = 2
	unix_owner_pos = 3
	unix_group_pos = 4
	file_bytesize_pos = 5
	file_month_pos = 6
	file_da_posy = 7
	file_year_pos = 8
	file_name_pos = 9
	
	line_no = 0
	dirname = ""
	dirsize = 0
	ls_output_split = ls_output.split(b"\n")
	for line in ls_output_split:
		try:
			line = line.decode()
			if line_no == 0:
				dirname = line
			if line_no == 1:
				line_split = line.split()
				if len(line_split) == 2:
					dirsize = int(line_split[1])					
			else:
				if line_no > 1:
					line_split = line.split()
					if len(line_split) > 9:
						filename = line_split[file_name_pos]
						
						# Don't process "." and ".." entries
						if filename not in [".", ".."]:
							full_file_path = dirname + "/" + filename
							unix_group = line_split[unix_group_pos]
							unix_owner = line_split[unix_owner_pos]
							file_size = line_split[file_size_pos]
							file_size = int(file_size)
							
				
							if unix_owner not in username_list:
								f = {
									'file' : full_file_path,
									'username' : unix_owner,
									'groupname' : unix_group,
									'kbytes' : file_size,
								}
								ls_data.append(f)
								
		except Exception as err:
			print("ERROR (decode_ls_orphaned_files): %s" % err)					
						
		line_no += 1
	return ls_data

def decode_ls_output_byuser(ls_output = "", user_name = "myname", invert = False):
	""" Decode a block of ls -aslLR output, each block is split by a carriage return """
	
	# Example output
	#
	#./datafolder:
	#total 10561076
	#drwxr-s---  6 username groupname        4096 Jun 20  2023 .
	#drwxrws--- 10 root     groupname        4096 Jun 21  2023 ..
	#-rw-rw----  1 username anothergroup 10814461821 Jun 19  2023 file1.zip
	#-rw-r-----  1 username groupname        4957 Jun 20  2023 file2.zip
	#drwxr-s---  2 username groupname        4096 Jun 20  2023 file3.txt
	#drwxrws---  3 username groupname        4096 Jun 19  2023 file4.txt
	#drwxrws---  3 username groupname        4096 Jun 19  2023 file5.txt
	#drwxrws---  3 username groupname        4096 Jun 19  2023 file6.csv
	#
	# In the case above, 'file1.zip' has a different group assigned to the directory itself.
	
	# Returns the following structure
	#ls_data = {
	#	'files' : ['/a/list/of/filenames'],
	#	'bytes' : 12345,
	#}
	ls_data = {
		'files' : [],
		'bytes' : 0,
		'kbytes' : 0,
	}
	
	# Field position in an ls -lR output
	file_size_pos = 0
	unix_perms_pos = 1
	files_total_pos = 2
	unix_owner_pos = 3
	unix_group_pos = 4
	file_bytesize_pos = 5
	file_month_pos = 6
	file_da_posy = 7
	file_year_pos = 8
	file_name_pos = 9
	
	line_no = 0
	dirname = ""
	dirsize = 0
	ls_output_split = ls_output.split(b"\n")
	for line in ls_output_split:
		try:
			line = line.decode()
			if line_no == 0:
				dirname = line
			if line_no == 1:
				line_split = line.split()
				if len(line_split) == 2:
					dirsize = int(line_split[1])					
			else:
				if line_no > 1:
					line_split = line.split()
					if len(line_split) > 9:
						filename = line_split[file_name_pos]
						
						# Don't process "." and ".." entries
						if filename not in [".", ".."]:
							full_file_path = dirname + "/" + filename
							unix_group = line_split[unix_group_pos]
							unix_owner = line_split[unix_owner_pos]
							file_size = line_split[file_size_pos]
							file_size = int(file_size)
							
							# Are we looking for non-matching owners?
							if invert:
								if unix_owner != user_name:
									ls_data['files'].append(full_file_path)
									ls_data['bytes'] = ls_data['bytes'] + file_size
									
							# ... or matching owners?
							else:
								if unix_owner == user_name:
									ls_data['files'].append(full_file_path)
									ls_data['bytes'] = ls_data['bytes'] + file_size
		except Exception as err:
			print("ERROR (decode_ls_output_byuser): %s" % err)					
						
		
		line_no += 1
	
	ls_data['kbytes'] = ls_data['bytes']		
	return ls_data

def decode_ls_output_bygroup(ls_output = "", group_name = "mygroup", invert = False):
	""" Decode a block of ls -lR output, each block is split by a carriage return """
	
	# Example output
	#
	#./datafolder:
	#total 10561076
	#drwxr-s---  6 username groupname        4096 Jun 20  2023 .
	#drwxrws--- 10 root     groupname        4096 Jun 21  2023 ..
	#-rw-rw----  1 username anothergroup 10814461821 Jun 19  2023 file1.zip
	#-rw-r-----  1 username groupname        4957 Jun 20  2023 file2.zip
	#drwxr-s---  2 username groupname        4096 Jun 20  2023 file3.txt
	#drwxrws---  3 username groupname        4096 Jun 19  2023 file4.txt
	#drwxrws---  3 username groupname        4096 Jun 19  2023 file5.txt
	#drwxrws---  3 username groupname        4096 Jun 19  2023 file6.csv
	#
	# In the case above, 'file1.zip' has a different group assigned to the directory itself.
	
	# Returns the following structure
	#ls_data = {
	#	'files' : ['/a/list/of/filenames'],
	#	'bytes' : 12345,
	#}
	ls_data = {
		'files' : [],
		'bytes' : 0,
		'kbytes' : 0,
	}
	
	# Field position in an ls -lR output
	file_size_pos = 0
	unix_perms_pos = 1
	files_total_pos = 2
	unix_owner_pos = 3
	unix_group_pos = 4
	file_bytesize_pos = 5
	file_month_pos = 6
	file_da_posy = 7
	file_year_pos = 8
	file_name_pos = 9
	
	line_no = 0
	dirname = ""
	dirsize = 0
	
	ls_output_split = ls_output.split(b"\n")
	for line in ls_output_split:
		try:
			line = line.decode()
			if line_no == 0:
				dirname = line
			if line_no == 1:
				line_split = line.split()
				if len(line_split) == 2:
					dirsize = int(line_split[1])
					ls_data['kbytes'] = dirsize
			else:
				if line_no > 1:
					line_split = line.split()
					if len(line_split) > 9:
						filename = line_split[file_name_pos]
						
						# Don't process "." and ".." entries
						if filename not in [".", ".."]:
							full_file_path = dirname + "/" + filename
							unix_group = line_split[unix_group_pos]
							unix_owner = line_split[unix_owner_pos]
							file_size = line_split[file_size_pos]
							file_size = int(file_size)
							
							# Are we looking for non-matching groups?
							if invert:
								if unix_group != group_name:
									ls_data['files'].append(full_file_path)
									ls_data['bytes'] = ls_data['bytes'] + file_size
									
							# ... or matching groups?
							else:
								if unix_group == group_name:
									ls_data['files'].append(full_file_path)
									ls_data['bytes'] = ls_data['bytes'] + file_size
		except Exception as err:
			print("ERROR (decode_ls_output_bygroup): %s" % err)
		
		line_no += 1
		
	ls_data['kbytes'] = ls_data['bytes']		
	return ls_data
		
			

def get_group_utilisation_ls(find_type = "ls", group_name = "mygroup", quota_directory = "/mydir", invert = False, cmd_only = False):
	""" Parse a block of output from an ls -lR command and return a python dict of the data """
	
	# Returns
	data = {
		'group'		: group_name,
		'dirname'	: quota_directory,
		'quota'		: 0,
		'limit'		: 0,
		'files'		: []
	}
	
	job_cmd = f"ls -alskLR {quota_directory} 2>/dev/null"
	
	if cmd_only:
		return job_cmd
		
	try:
		process = subprocess.Popen(job_cmd, shell=True,
					stdin=subprocess.PIPE, stdout=subprocess.PIPE,
					stderr=subprocess.STDOUT)
		if process:
			output = process.stdout.read().rstrip().split(b'\n\n')
			for ls_output in output:
				ls_data = decode_ls_output_bygroup(ls_output, group_name, invert)
				data['quota'] = data['quota'] + ls_data['kbytes']
				data['files'] = data['files'] + ls_data['files']
				
		return data

	except Exception as err:
		print("ERROR (get_group_utilisation_ls): %s" % err)
		return False

def get_group_utilisation(find_type = "normal", group_name = "mygroup", quota_directory = "/mydir", invert = False, cmd_only = False):
	""" Uses 'find' to calculate the space utilisation of an entire directory tree by a given unix group """

	if find_type == "lfs":
		if invert:
			# Find everything NOT owned by the group
			job_cmd = f"lfs find {quota_directory} -not -group {group_name} 2>/dev/null"
		else:
			job_cmd = f"lfs find {quota_directory} -group {group_name} 2>/dev/null"
	else:
		if invert:
			# Find everything NOT owned by the group
			job_cmd = f"find {quota_directory} -not -group {group_name} 2>/dev/null"
		else:
			job_cmd = f"find {quota_directory} -group {group_name} 2>/dev/null"
	
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
		print("ERROR (get_group_utilisation): %s" % err)
		return False
		
def get_user_utilisation_ls(find_type = "normal", user_name = "myuser", quota_directory = "/mydir", cmd_only = False):
	""" Report user utilisation of a given directory tree, using ls -lR """
	
	job_cmd = f"ls -alskLR {quota_directory} 2>/dev/null"
	
	if cmd_only:
		return job_cmd
		
	data = {
		'username'	: user_name,
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
			output = process.stdout.read().rstrip().split(b'\n\n')
			for ls_output in output:
				ls_data = decode_ls_output_byuser(ls_output, user_name)
				if ls_data:
					data['quota'] = data['quota'] + ls_data['kbytes']
					data['files'] = data['files'] + ls_data['files']
				
		return data

	except Exception as err:
		print("ERROR (get_user_utilisation_ls): %s" % err)
		return False
		
def get_user_utilisation(find_type = "normal", user_name = "myuser", quota_directory = "/mydir", cmd_only = False):
	""" Report user utilisation of a given directory tree using find """
		
	if find_type == "lfs":
		job_cmd = f"lfs find {quota_directory} -user {user_name} 2>/dev/null"
	else:
		job_cmd = f"find {quota_directory} -user {user_name} 2>/dev/null"
	
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
		print("ERROR (get_user_utilisation): %s" % err)
		return False
		
def get_user_orphaned_files_ls(find_type = "normal", username_list = None, quota_directory = "/mydir", cmd_only = False):
	""" Get a list of files which are owned by users other than those in the provided username_list. """
	
	job_cmd = f"ls -alskLR {quota_directory} 2>/dev/null"
	
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
			output = process.stdout.read().rstrip().split(b'\n\n')
			for ls_output in output:
				found_files = decode_ls_orphaned_files(ls_output, username_list)
				for f in found_files:
						data['files'].append(f)
						
						uid = f['username']
						gid = f['groupname']
						if uid not in data['users']:
							data['users'][uid] = {
								'files' : [],
								'username' : "",
								'uid' : uid,
								'quota' : 0
							}
							
						data['users'][uid]['files'].append(f)
						data['users'][uid]['quota'] = data['users'][uid]['quota'] + f['kbytes']
						
						# INcrease the count of space used
						data['quota'] = data['quota'] + f['kbytes']
			return data

	except Exception as err:
		print("ERROR (get_user_orphaned_files_ls): %s" % err)
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
	
	