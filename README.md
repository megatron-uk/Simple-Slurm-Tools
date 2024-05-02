# Simple Slurm Tools

This project contains a set of simple tools for administrators working with High Performance Computer facilities largely based on [Slurm](https://slurm.schedmd.com/documentation.html) and the common supporting tools which are often used alongside Slurm.

The tools are fairly simple, usually performing a single function, and are modelled around tasks that I tend to do on a regular basis.

   * [modulespy](#modulespy) - A Linux *module* dependency finder
   * [sjobs](#sjobs) - A simple Slurm queue report tool

Required packages for most of the tools are usually limited to basic system tools (e.g. slurm itself) and Python (3.x, no external Python modules are needed).

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