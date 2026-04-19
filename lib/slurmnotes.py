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

notes = {
	'a' : "The amount of CPU cores in use has reached the limit for the account_code. No further jobs will be started until this figure reduces.",
	'b' : "The amount of CPU cores requested by pending jobs is greater than the limit for the account code. Only a subset will start at any time until the figure reduces.",
	'c' : "The amount of GPU cards in use has reached the limit for the account_code. No further jobs requiring GPU cards will be started until this figure reduces.",
	'd' : "The amount of GPU cards requested by pending jobs is greater than the limit for the account_code. Only a subset will start at any time until the figure reduces.",
	'e' : "The number of jobs running has reached the limit for the account_code (see GrpJobs). Individual users may not have reached their own limits (MaxJobs), no further jobs will be started until the aggregate figure reduces.",
	'f' : "The number of pending jobs has reached the limit for the account_code (see GrpSubmit). Individual users may not have reached their own limits (MaxSubmit), no further jobs will be queued until the aggregate figure reduces.",
	'g' : "The combined total of running and pending jobs has reached the limit for the account_code (see GrpSubmit). No new jobs will be accepted until the aggregate figure reduces.",
	'z' : "Where a value is set to Undefined, this means either no limit is set, or it inherits the maximum value set at the time Slurm was compiled.",
}
