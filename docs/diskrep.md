### diskrep

The *diskrep* command is used to generate filesystem utilisation reports.

The tool can use either the Linux **quota** command to retrieve filesystem utilisation and limit levels for users and groups, or, in the event of a filesystem without quotas enabled, can use **GNU find** to manually calculate utilisation for found files. 

Both methods require the script to be ran from an administrative account which can access other users directory trees, or be run on a directory tree which you already have access to.

#### Requirements

   * Python 3
   * Linux quota utilities
   * GNU find
   * Must be run via **sudo** in order to run quota on other users and groups
   * Must be run via **sudo** in order to use find and stat on other users directory contents
   * The system must be configured to enumerate members of a group by a standard *getent group groupname* call

Optionally, in the case of a Lustre filesystem, the Lustre variant of the find utility can be used instead.

#### Options & Arguments

   * **-nq** No Quota; disables quota-based utilisation calculations and switches on *find* and manual file-size metrics. Slower, but will work for any directory or filesystem tree, including those without quotas enabled
   * **-csv** Data will be output in comma seperated value format
   * **-bygroup** Utilisation will be aggregated by group, rather than user; i.e. you will see totals for a group, the default is to report by individual user
   * **-users** A comma seperated list of which users to generate a report for
   * **-users_exclude** A comma seperated list of users to exclude from the report
   * **-groups** A comma seperated list of groups to generate the report for
   * **-groups_exclude** A comma seperated list of groups to exclude from the report
   * **-lfs** Use native Lustre *find* command instead of GNU findutils.
   * **dirname** The name of the directory or filesystem mount point to report on

#### Example

An example showing a report against **/home** for the **users** group using the **non-quota** space calculation method, aggregated by user, is shown below:

        $ diskrep -nq -groups users /home/
        diskrep - A disk utilisation report tool
        ========================================

        Analysing	: /home/
        Method		: find
        Find type	: generic
        Group mode	: False
        Users		: 4 users / 0 excluded
        Groups		: 1 groups / 0 excluded

        User with highest disk space use	: jen, 654451 KBytes
        User with highest quota use		: jen, 64 %

        Username            KBytes used        KBytes limit       Quota Utilisation
        ========            ===========        ============       =================
        jen                      654451             1024000        64%
        bob                       45678              256000        17%
        jack                      32342               65355        49%
        sam                        9927               65355        15%
        
        OK
        $