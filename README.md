# Simple Slurm Tools

This project contains a set of simple tools for administrators working with High Performance Computer facilities largely based on [Slurm](https://slurm.schedmd.com/documentation.html) and the common supporting tools which are often used alongside Slurm.

The tools are fairly simple, usually performing a single function, and are modelled around tasks that I tend to do on a regular basis.

   * [diskrep](docs/diskrep.md) - A disk/filesystem utilisation report tool
   * [grouprep](docs/grouprep) - A group audit tool
   * [modulespy](docs/modulespy) - A Linux *module* dependency finder
   * [shistory](docs/shistory) - Historic data of the overall HPC system, or HPC users
   * [sjobs](docs/sjobs) - A simple Slurm queue & job report tool

Required packages for most of the tools are usually limited to basic system tools (e.g. slurm itself, quota tools) and Python (3.x). The only external packages are required are those used by the HTML report generators.

## Supporting Tools

Most of the Python functionality is implemented in a collection of functions in the [lib](lib/) subfolder. 

Whilst these are not written to be directly called, they may be useful for other purposes. These files include:

   * [lib/settings.py](docs/settings.md) - Global settings common across all tools
   * [lib/slurmcache.py](docs/slurmcache.md) - Simple methods to cache the results of expensive calculations to disk
   * [lib/slurmjob.py](docs/slurmjob.md) - Interface to the slurm sacct command to return queue and job information
   * [lib/posix.py](docs/posix.md) - Methods to query unix users and groups, disk quotas etc

---


