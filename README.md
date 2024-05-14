# Simple Slurm Tools

This project contains a set of simple tools for administrators working with High Performance Computer facilities largely based on [Slurm](https://slurm.schedmd.com/documentation.html) and the common supporting tools which are often used alongside Slurm.

The tools are fairly simple, usually performing a single function, and are modelled around tasks that I tend to do on a regular basis.

   * [diskrep](#diskrep) - A disk/filesystem utilisation report tool
   * [modulespy](#modulespy) - A Linux *module* dependency finder
   * [sjobs](#sjobs) - A simple Slurm queue report tool

Required packages for most of the tools are usually limited to basic system tools (e.g. slurm itself) and Python (3.x, no external Python modules are needed).

---

### diskrep

The *diskrep* command is used to generate filesystem utilisation reports.

The tool can use either quota to retrieve filesystem utilisation and limit levels for users and groups, or, in the event of a filesystem without quotas enabled, can use find to manually calculate utilisation. Both methods require the script to be ran from an administrative account which can access other users directory trees.

#### Requirements

   * Python 3
   * Must be run via **sudo** in order to run quota on other users and groups
   * Must be run via **sudo** in order to use find and stat on other users directory contents
   * The system must be configured to enumerate members of a group by a standard *getent group groupname* call

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

        Part of Simple Slurm Tools
        Author: John Snowdon
        URL: https://github.com/megatron-uk/Simple-Slurm-Tools

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
---

### modulespy

The *modulespy* command recurses through the dependencies of a given Linux module, as would be instantiated via the normal '**module load packagename**' command.

Its purpose is to recursively find **all** child modules loaded by the named module. 

Module environments can get rather complex, and it is often difficult to understand the relationship between dependencies, this tool lets you know **exactly** which modules are loaded when you load a specific one.

#### Requirements

   * Python 3
   * Access to the '**module show**' command

#### Example

The command only takes a single option; the name of the module to query. An example showing all the dependencies of a GCC module is shown below:

        $ modulespy GCC
        modulespy - A loadable module interrogation tool
        ================================================
    
        Searching for all dependencies of: GCC
        GCC -> GCCcore/12.3.0
        GCC -> binutils/2.40-GCCcore-12.3.0
        binutils/2.40-GCCcore-12.3.0 -> GCCcore/12.3.0
        binutils/2.40-GCCcore-12.3.0 -> zlib/1.2.13-GCCcore-12.3.0
        zlib/1.2.13-GCCcore-12.3.0 -> GCCcore/12.3.0
    
        OK
        $
---

### sjobs

The *sjobs* command produces a utilisation summary report for the current state of a given Slurm job queue.

It provides an at-a-glance indication of how heavily used a given queue is, as well as showing the maxium and average job sizes (cores, nodes, memory use, wallclock time). 

#### Requirements

   * Python 3
   * Access to the Slurm '**sacct**' command

#### Example

The command takes one mandatory parameter; the name of the queue to report on:

        $ sjobs default
        sjobs - Slurm Job Summary
        =========================

        Please wait, retrieving running data for default...
        Please wait, retrieving pending data for default...

        -= Running =-                            -= Pending =-
        =============                            =============
        Total users              :       12      Total users waiting              :        8
        Total running jobs       :      762      Total waiting jobs               :       36
        Total allocated cores    :     3371      Total requested cores            :      774
        Total allocated memory   :     8327 GB   Total requested memory           :     1914 GB
        Total runtime            :    43609 min  Total waiting time               :    27339 min
        -
        Largest job (cores)      :      264      Largest waiting job (cores)      :       32
        Largest job (memory/job) :      644 GB   Largest waiting job (memory/job) :       78 GB
        Largest job (memory/core):       26 GB   Largest waiting job (memory/core):        4 GB
        Longest job runtime      :     2878 min  Longest waiting time             :     1337 min
        -
        Average job (cores)      :        4      Average waiting job (cores)      :       21
        Average job (memory/job) :       10 GB   Average waiting job (memory/job) :       53 GB
        Average job (memory/core):        2 GB   Average waiting job (memory/core):        2 GB
        Average runtime          :       57 min  Average waiting time             :      759 min

        OK
        $