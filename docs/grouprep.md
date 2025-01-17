### grouprep

The *grouprep* command audits and reports on a given unix group and associated directory tree (i.e. possibly their allocated project working space) to determine filesystem use and identify files owned by users or groups *alien* to the named group.

Its main use is to report when one or more users has left a group and directory tree still contains contents linked to their (now alien) uid. Its secondary use is to identify situations where a member of a group has changed the group of one or more files so it is no longer set to the correct gid.

This tool is useful in the following scenario:

   * All members of a group work under a shared filesystem tree
   * All files created under that tree should be owned by a single group/gid
   * Orphaned files created by previous group members need to be identified and re-assigned to a current group member

#### Requirements

   * Python 3
   * Must be run via **sudo** to audit groups to which you are not a member
   * Must be run via **sudo** to audit directory trees to which you do not have access permissions
   * The system must be configured to enumerate members of a group by a standard *getent group groupname* call

Optionally, in the case of a Lustre filesystem, the Lustre variant of the find utility can be used instead.

#### Example

   * **-nq** No Quota; disables quota-based utilisation calculations and switches on *find* and manual file-size metrics. Slower, but will work for any directory or filesystem tree, including those without quotas enabled
   * **-ls** No Quota, and use a recursive *ls* command instead of *find*. This is generally fast, but due to the way ls, find, quota, du differ, may not be as accurate as other methods. However, it is usually 'good enough'.
   * **-csv** Data will be output in comma seperated value format
   * **-lfs** Use native Lustre *find* command instead of GNU findutils.
   * **groupname** The name of the unix group to report on
   * **dirname** The name of the directory or filesystem mount point to report on

An example showing a report against **/export/Project1** for the **team1** group using the **non-quota** space calculation method is shown below.

This particular example highlights that at least part of the directory tree was created by users (uid **501** & **502**) that are no longer part of the **team1** group. In addition, some files (4599 of them!) are set to the wrong group:

        $ grouprep -nq team1 /export/Project1
        grouprep - A group audit & report tool
        ========================================

        Analysing	: /export/Project1
        Method		: find
        FS type		: generic
        Group mode	: False
        Users		: 2 users
        Groups		: 1 group (team1)

        Please wait, retrieving group space utilisation: 
        Please wait, retrieving individual user space utilisation: ..
        Please wait, retrieving alien group space utilisation: 
        Please wait, retrieving alien user space utilisation: 

        Group Report		Value
        ============		=====
        Group name		    team1
        Group exists		Yes
        Group has members	Yes
        Group folder		Yes: /export/Project1
        Total utilisation	346949421 kbytes
        - user bob		    334528184 kbytes
        - user fred		    28137842 kbytes

        Files that are owned by another group
        ==================
        Total space		17607284 kbytes
        Total files		4599 files
        * These files may need a 'chgrp'
        * Hint: find /export/Project1 -not -group team1 2>/dev/null

        Files with owners no longer in this group
        ==================
        Total space		1890680 kbytes
        Total files		1688 files
        Total users		2 users
        - uid 501  		1818326 kbytes, in 1574 files
        - uid 502  		71508 kbytes, in 114 files
        * These files may need a 'chown'
        * Hint: find /export/Project1 -not -user bob -a -not -user fred  2>/dev/null

        OK
        $