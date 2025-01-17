### lib/posix.py

#### Purpose

This file contains functions which work with unix/linux users, groups, processes and disk quotas.

#### Classes

None

---

#### Functions

##### get_groups()

Params: 

   * *groups*; comma seperated list of group names. e.g. "users,sudo,team1,web$dev"

Returns:

   * Python list of *valid* unix group names. e.g. ['users', 'sudo', 'team1']
   * Empty list on error

Description:

   * Processes a string of (possible) unix group names and attempts to map them to real groups. If the group can be enumerated correctly, the group is added to the output list. Group names which do not map to real groups are discarded.

---

##### get_users()

Params:

   * *users*; comma seperated list of user names. e.g. "root,user1,apache,bob,fred"

Returns:

   * Python list of *valid* unix user names. e.g. ['root', 'apache', 'bob', 'fred']
   * Empty list on error

Description:

   * Processes a string of (possible) unix usernames and attempts to map them to real users. If the user can be enumerated correctly, the username is added to the output list. Names which do not map to real users are discarded.

---

##### get_users_from_groups()

Params:
 
   * *groups*; a Python list of group names. e.g. ['users', 'sudo', 'team1', 'webdev']

Returns:

  * Python list of unique unix user names. e.g. ['root', 'bob', 'fred', 'apache', 'webuser', 'user1']

Description:

   * Returns the unique set of all unix user names who are members of the given Python list of group names. Duplicate users across multiple groups are included only once.

---

##### get_user_quota()

Params:

   * find_type, *string*; defaults to "normal". Other possible values include "lfs". Indicates which backend quota tool to use.
   * user_name, *string*; a valid unix user name. e.g. "bob"
   * quota_directory, *string*; a valid mount point or directory name. e.g. "/mnt/data"

Returns:

   * Python dict with the following structure:
      * username, *string*; e.g. "bob"
      * dirname, *string*; e.g. "/mnt/data"
      * quota, *int*; actual quota use, in kilobytes. e.g. 12345678
      * limit, *int*; quota upper limit, in kilobytes. e.g. 23456789
      * overquota, *boolean*; True if over quota, otherwise False
   * False on error

Description:

   * Queries an individual user quota using the prescribed back-end quota tool, mapping the quota fields to a Python dictionary.

NOTE: This will return False if called for a user or filesystem which does not have quotas enabled.

---

##### get_group_quota()

Params:

   * find_type, *string*; defaults to "normal". Other possible values include "lfs". Indicates which backend quota tool to use.
   * group_name, *string*; a valid unix group name. e.g. "users"
   * quota_directory, *string*; a valid mount point or directory name. e.g. "/mnt/data"

Returns:

   * Python dict with the following structure:
      * group, *string*; e.g. "users"
      * dirname, *string*; e.g. "/mnt/data"
      * quota, *int*; actual quota use of the group, in kilobytes. e.g. 12345678
      * limit, *int*; upper quota limit of the group, in kilobytes. e.g. 23456789
      * overquota, *boolean*; True if the group is over quota, otherwise False
   * False on error

Description:

   * Queries a group quota using the prescribed back-end quota tool, mapping the quota fields to a Python dictionary.

NOTE: This will return False if called for a group or filesystem which does not have quotas enabled.

---

##### get_group_utilisation()

---

##### get_user_utilisation()

---

##### get_user_orphaned_files()