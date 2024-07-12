### shistory

The *shistory* command produces a report on historic use of the HPC scheduler as well as an (optional) report on the historic use by users.

The report is useful in identifying general performance and utilisation trends over a given monitoring period. 

#### Requirements

   * Python 3
   * Access to the Slurm '**sacct**' command

#### Example

The command takes several optional parameters:

        usage: sjobs [-h] [-csv] [-csv_user] [-keyfield KEYFIELD] [-keytype KEYTYPE] [-day] [-week] [-month] [-year]
             [-periods PERIODS] [-pc PC]

        options:
          -h, --help          show this help message and exit
          -csv                Enable CSV summary output only [default disabled].
          -csv_user           Enable CSV user stats output only [default disabled].
          -keyfield KEYFIELD  One of [runtime, waittime, cores, nodes, ramcore, cpuhours], [default is runtime].
          -keytype KEYTYPE    Data type to use for the keyfield, one of [min, max, mean, total], [default is total].
          -day                Reports are in periods of one day.
          -week               Reports are in periods of one week [default].
          -month              Reports are in periods of one month.
          -year               Reports are in periods of one year.
          -periods PERIODS    Total number of reporting periods to produce history for [default is 1].
          -pc PC              Percentile figure for reports [defaults is 75].

The defaults are clearly identified and are:

   * Do not produce CSV output
   * Do not include user summaries
   * Report on the HPC system over a period of one week
   * Use a custom percentile of 75% for benchmarking

With the default values a report similar to below will be produced:

        $ ./shistory 
        Slurm Job Histories
        ==================================

        Report period	: week
        Report count	: 1
        Percentile	: 75%

        Please wait, starting retrieval of job data...
        - Retrieving week data for 2024-07-05T00:00:00 - 2024-07-12T00:00:00

        Please wait, analysing job data...
        - Analysing 22619 jobs

        Period (type)     Jobs -   CPUHours -  RunTime -                WaitTime -               Cores -              Nodes -           RAM/Core -
                          Total    Total       Min/Max/Mean/75%         Min/Max/Mean/75%         Min/Max/Mean/75%     Min/Max/Mean/75%  Min/Max/Mean/75%
        =============     =======  ==========  =======================  =======================  ===================  ================  ===============================
        2024-07-05 week   22619    324141.0        0/ 3430/   84/   76      2/ 1440/ 1102/ 1256     1/ 264/   9/  12        1/ 6/ 1/ 1      256/ 409600/   5369/   2500
        $

A description of the fields is given below:

   * **Period (type)** - The start date of the sampling period and the length of the sample window.

   * **Jobs (Total)** - The total number of jobs in the *completed* (state == CD) in the given period, and the number of jobs used in the calculation of the following data fields.


   * **CPU Hours (Total)** - The sum of all CPU time of all jobs completed in the given period; where the CPU time for a job is calculated as *Allocated CPU's * Job Runtime*.


   * **Runtime (min/max/mean/75%)** - The *shortest*, *longest* and *average* time, *in minutes*, that all jobs which completed in the given period ran for. In addition the 75% column gives a figure which indicates how long was necessary for 75% of all jobs to run to completion. This latter column can be adjusted via the **-pc** parameter.

   * **Waittime (min/max/mean/75%)** - The *shortest*, *longest* and *average* time, *in minutes*, that a job spent in the pending state in the given period. In addition the 75% column gives a figure which indicates how long was necessary for 75% of all jobs to wait in the pending state until they began to run. This latter column can be adjusted via the **-pc** parameter.

   * **Cores (min/max/mean/75%)** - The *smallest*, *largest* and *average* number of CPU cores that a job was allocated in the given period. In addition the 75% column gives a figure which indicates how many cores were necessary to satisfy 75% of all jobs to run to completion. This latter column can be adjusted via the **-pc** parameter.

   * **Nodes (min/max/mean/75%)** - The *smallest*, *largest* and *average* number of compute nodes that a job was allocated in the given period. In addition the 75% column gives a figure which indicates how many compute nodes were necessary to satisfy 75% of all jobs to run to completion. This latter column can be adjusted via the **-pc** parameter.

   * **RAM/Core (min/max/mean/75%)** - The *smallest*, *largest* and *average* number of RAM, *in megabytes*, per CPU core that a job was allocated in the given period. In addition the 75% column gives a figure which indicates the smallest amount of RAM to CPU core which was necessary to satisfy 75% of all jobs to run to completion. This latter column can be adjusted via the **-pc** parameter.

If the **-periods** parameter is set to greater than **1**, then this will produce a chronological output of performance data, e.g:

        $ ./shistory -periods 5
        Slurm Job Histories
        ==================================

        Report period	: week
        Report count	: 5
        Percentile	: 75%

        Please wait, starting retrieval of job data...
        - Retrieving week data for 2024-06-07T00:00:00 - 2024-06-14T00:00:00
        - Retrieving week data for 2024-06-14T00:00:00 - 2024-06-21T00:00:00
        - Retrieving week data for 2024-06-21T00:00:00 - 2024-06-28T00:00:00
        - Retrieving week data for 2024-06-28T00:00:00 - 2024-07-05T00:00:00
        - Retrieving week data for 2024-07-05T00:00:00 - 2024-07-12T00:00:00

        Please wait, analysing job data...
        - Analysing 46129 jobs
        - Analysing 120289 jobs
        - Analysing 9776 jobs
        - Analysing 74592 jobs
        - Analysing 22619 jobs

        Period (type)     Jobs -   CPUHours -  RunTime -                WaitTime -               Cores -              Nodes -           RAM/Core -
                          Total    Total       Min/Max/Mean/75%         Min/Max/Mean/75%         Min/Max/Mean/75%     Min/Max/Mean/75%  Min/Max/Mean/75%
        =============     =======  ==========  =======================  =======================  ===================  ================  ===============================
        2024-06-07 week   46129    296589.7        0/ 5772/   87/   76      1/ 1440/  941/ 1270     1/ 352/   4/   8        1/29/ 1/ 1      256/1024000/   3466/   3072 
        2024-06-14 week   120289   242150.7        0/ 6068/   42/    5      0/ 1440/  932/ 1037     1/ 264/   2/   1        1/ 9/ 1/ 1      256/ 819200/   2769/   2500 
        2024-06-21 week   9776     254925.8        0/ 5589/  102/   76      0/ 1440/ 1115/ 1240     1/ 264/  10/  12        1/ 9/ 1/ 1      100/ 409600/  11834/   4096 
        2024-06-28 week   74592    287455.1        0/ 6525/   25/   12      1/ 1440/  905/ 1328     1/ 176/   3/   1        1/12/ 1/ 1      256/ 409600/   3312/   2500 
        2024-07-05 week   22619    324141.0        0/ 3430/   84/   76      2/ 1440/ 1102/ 1256     1/ 264/   9/  12        1/ 6/ 1/ 1      256/ 409600/   5369/   2500

For large data sets, the above information can be output in CSV format for further analysis by supplying the **-csv** command line option.

##### Week Summary Example

Two examples of producing data for a week, where both commands will process the same number of jobs, but aggregate and present the information at a different granularity:

   * Summary of a week, with data aggregated over 7 days:
   * *shistory -week*

   * Summary of a week, with data aggregated over a 24 hour window:
   * *shistory -periods 7 -day*

#### User Summary

The normal use of the *shistory* command only summarises general HPC job/performance data, however it can also produce targetted summaries of the same data on a **per user** basis. 

This output is normally too detailed to display in text mode, so it is only activated if the **-csv_user** flag is set.

By default the user report will use the following parameters:

   * **-week** - A week is the default sampling period
   * **-period** - A single period of 1
   * **-keyfield** - Will default to displaying the job **runtime** data of each user. Other possible options are **waittime**, **cores**, **nodes**, **ramcore** or **cpuhours** [note, for cpuhours, only a *total* can be shown].
   * **-keytype** - Will default to selecting the **total** value for the given keyfield. Other possible options are **min**, **max** or **mean**

Basic example, using defaults:

        $ ./shistory -csv_user
        total runtime date,period,bob,james,sue,jenny,frank
        2024-07-05,week,752.0,8151.6,46.0,3352.3,3137.8

This prints two lines, the first the header fields, and the second being the *total* *runtime* of a users' jobs in the given sampling period. *Every* user who has had a job complete in the sampling window will be included. 

As with the interactive display, the **-periods** and **-day**, **-week**, **-month** and **-year** options can be used to alter the number and granularity of the sampling windows. e.g.

        $ ./shistory -csv_user -periods 3 -day
        total runtime date,period,bob,james,sue,jenny,frank
        2024-07-05,day,752.0,8151.6,46.0,3352.3,3137.8
        2024-07-06,day,353.8,14915.0,8076.1,0,431399.0
        2024-07-07,day,267.1,6231.4,38.2,485251.3,17424.1

If a user has not had any jobs run in one or more of the sampling periods, then the data will be presented as *0* for that record.

##### Further User Summary Examples

   * Report, by user, the total consumed CPU Hours, by month, over a 12 month period (note that the *-keytype total* option isn't needed, since it is implicit with cpuhours):
   * *shistory -csv_user -periods 12 -month -keyfield cpuhours*

   * Report, by user, the average cores needed to run their jobs, by day, over the last 30 days:
   * *shistory -csv_user -periods 30 -day -keyfield cores -keytype mean*