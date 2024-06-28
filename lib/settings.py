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

######################################################
#
# Config variables for the Slurm status application.
#
######################################################

DEBUG = True

# Where templates live, relative to this file
TEMPLATE_PATH = "./templates/"

# Where HTML output is written to, relative to this file
HTML_PATH  = "./html/"

# Where persistent cache resides
CACHE_PATH = "./report_cache/"

# Partition names
PARTITIONS = ['defq', 'short', 'long', 'interactive', 'bigmem', 'dell-gpu', 'power']

######################################################
#
# DAILY settings
#

# Control the granularity of daily/weekly reports
# We ALWAYS want to report on an hourly basis
TODAY_DAYS = 1
TODAY_HOURS = [
	('00', '00'), ('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'), ('06', '06'), 
	('07', '07'), ('08', '08'), ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'),
	('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), 
	('21', '21'), ('22', '22'), ('23', '23')]

# Lets split each hour into 9m 59s chunks so that a day report is quite detailed
TODAY_MINUTES = [('00:00', '09:59'), ('10:00', '19:59'), ('20:00', '29:59'), ('30:00', '39:59'), ('40:00', '49:59'), ('50:00', '59:59')]


######################################################
#
# WEEKLY settings
#

# How many days do we include in a week report
WEEK_DAYS = 7
# For weekly reports lets keep reports on every hour
WEEK_HOURS = [
	('00', '00'), ('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'), ('06', '06'), 
	('07', '07'), ('08', '08'), ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'),
	('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), 
	('21', '21'), ('22', '22'), ('23', '23')]
# Lets split each hour into 20m chunks so that a day report is quite detailed
WEEK_MINUTES = [('00:00', '19:59'), ('20:00', '39:59'), ('40:00', '59:59')]

######################################################
#
# MONTHLY settings
#

MONTH_DAYS = 30
# For month reports lets keep reports on every hour
MONTH_HOURS = [
	('00', '00'), ('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'), ('06', '06'), 
	('07', '07'), ('08', '08'), ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'),
	('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), 
	('21', '21'), ('22', '22'), ('23', '23')]
# Decrease the granularity to one reporting period every hour
MONTH_MINUTES = [('00:00', '59:59')]

######################################################
#
# YEARLY settings
#
YEAR_DAYS = 365
# For year reports lets keep reports to a 24h window
YEAR_HOURS = [
	('00', '23')]
# Decrease the granularity to one reporting period per 24h
YEAR_MINUTES = [('00:00', '59:59')]

# How many entries in a league table result
LEAGUE_TABLE_SIZE = 25