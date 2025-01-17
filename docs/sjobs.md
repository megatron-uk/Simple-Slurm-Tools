### sjobs

The *sjobs* command produces a text-based utilisation summary report for the current state of a given Slurm job queue.

It provides an at-a-glance indication of how heavily used a given queue is, as well as showing the maxium and average job sizes (cores, nodes, memory use, wallclock time). 

#### Requirements

   * Python 3
   * Access to the Slurm '**sacct**' command

#### Example

The command takes **one mandatory parameter**; the name of the queue to report on:

        $ sjobs default_queue
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