gopy
=====

gopy is a python wrapper around the [Globus online](http://www.globusonline.org) ssh commandline interface.

Only a subset of the available commands is wrapped yet.

Main purpose of writing the wrapper was to be able to run parameter sweep type benchmarks between sites to figure out the impact of changing the various perf-* options of the [transfer](http://www.globusonline.org/docs_man.php?cmd=transfer).

This benchmark script is included in this repository as well...

Prerequisites
-------------------

- Python (>= 2.5)
- git

Checking out the sourcecode
-------------------------------------------

    git clone git://github.com/makkus/gopy.git
 
Running the benchmark script
---------------------------------------------

In order to run benchmarks you need to manually activate the two endpoints you are going to use. Also, you need to copy appropriate source files in place. Also, you need to have a working (ssh-key based) login to globusonline.org.

This script is not finished yet, so there are a few things missing like file-cleanup afterwards (although I'm not sure whether that is possible with globusonline anyway), endpoint activation and such...

### Usage ###

Here's how you run the script:
 
    python go-benchmarks/benchmark.py --help
 
 Which should give you something like:
 
    Usage: benchmark.py (-l|-u <globus_online_username> -n <benchmark_name>) [OPTION...]
    
    Benchmarks have names, when creating a new benchmark you need to specify the perf-p, perf-cc and perf-pp options you want the benchmark to cycle through. Once benchmark is created those options can't be changed anymore.

    -h	--help					this help
    -d	--debug					turns debug on (not implemented yet)
    -u	--username=GLOBUS_ONLINE_USERNAME	the globus online username
    -l	--list					lists all available benchmark names
    -n	--name=BENCHMARK_NAME			the name of the benchmark
    -i	--info					displaying information about a benchmark
    -s	--source-endpoint=SOURCE_ENDPOINT	the name of the source endpoint to be used in this series (also requires -p and -t)
    -p	--source-path				the path to the input file/folder to be used in this series (also requires -s and -t)
    -t	--target-endpoint=SOURCE_ENDPOINT	the name of the target endpoint (also requires -p and -s)
    	--perf-p				perf-p options (comma-seperated) to use in this benchmark (can only be specified if benchmark with the specified name does not exist yet)
    	--perf-cc				perf-cc options (comma-seperated) to use in this benchmark (can only be specified if benchmark with the specified name does not exist yet)
    	--perf-pp				perf-pp options (comma-seperated) to use in this benchmark (can only be specified if benchmark with the specified name does not exist yet)
    -c	--csv-file				exports the specified benchmark into a csv file
    -v	--visualize				prints a url to a google charts image for all the transfer series in this benchmark


### Creating a new benchmark ###
 
First you need to create a new benchmark, initializing with 3 (comma-seperated) lists of the perf-* options you want to iterate through (be aware that that can result in a lot of runs):

    benchmark.py -n test  -u markus  --perf-p=1,8,16 --perf-cc=1 --perf-pp=1,16,32
   
 Will result in: 
   
    Name:  test
	perf-p:		1
	perf-cc:	1
	perf-pp:	1 16 32
	Series:
		No transfer series for this benchmark yet. Add one using something like: --source-endpoint=ci#pads --source-path=/~/testfile_1GB --target-endpoint=markus#ng5

### Running a new transfer series ###

Then run your first transfer series:

    benchmark.py -n new_test4 -u markus  --source-endpoint=ci#pads --source-path=/~/testfile_1GB --target-endpoint=markus#ng5
    
### Creating a benchmark and running a transfer series straight away ###

Alternatively you could also run the first series of transfers straight away:

    benchmark.py -n test2  -u markus --perf-p=1,8,16 --perf-cc=1 --perf-pp=1,16,3 --source-endpoint=ci#pads --source-path=/~/testfile_100mb --target-endpoint=ng5

### Listing all benchmarks ###

You can get a list of all your current benchmarks via:

    benchmark.py --list
    
### Displaying information about a benchmark ###
    
And to get information about a particular benchmark, you use:

    benchmark.py -u markus -n medium --info
 
You get information about the transfer series that are attached to this benchmark:

    Name: medium
	perf-p:		1 4 8 12 16
	perf-cc:	1
	perf-pp:	1 8 16 24 32
	Series:
		Started: 2011-03-15 11:44:51.309713
		Source endpoint: ci#pads
		Source path: /~/testfile_100mb
		Target endpoint: ng5
			Options: (globus default)			(Speed: 17.12 mbps)
			Options: --perf-p=1 --perf-cc=1 --perf-pp=1	(Speed: 6.991 mbps)
			Options: --perf-p=1 --perf-cc=1 --perf-pp=8	(Speed: 9.869 mbps)
			Options: --perf-p=1 --perf-cc=1 --perf-pp=16	(Speed: 10.107 mbps)
			Options: --perf-p=1 --perf-cc=1 --perf-pp=24	(Speed: 8.066 mbps)
			Options: --perf-p=1 --perf-cc=1 --perf-pp=32	(Speed: 7.626 mbps)
			Options: --perf-p=4 --perf-cc=1 --perf-pp=1	(Speed: 19.508 mbps)
			Options: --perf-p=4 --perf-cc=1 --perf-pp=8	(Speed: 21.509 mbps)
			Options: --perf-p=4 --perf-cc=1 --perf-pp=16	(Speed: 16.777 mbps)
			Options: --perf-p=4 --perf-cc=1 --perf-pp=24	(Speed: 20.972 mbps)
			Options: --perf-p=4 --perf-cc=1 --perf-pp=32	(Speed: 23.967 mbps)
			Options: --perf-p=8 --perf-cc=1 --perf-pp=1	(Speed: 28.926 mbps)
			Options: --perf-p=8 --perf-cc=1 --perf-pp=8	(Speed: 27.962 mbps)
			Options: --perf-p=8 --perf-cc=1 --perf-pp=16	(Speed: 31.069 mbps)
			Options: --perf-p=8 --perf-cc=1 --perf-pp=24	(Speed: 18.236 mbps)
			Options: --perf-p=8 --perf-cc=1 --perf-pp=32	(Speed: 25.42 mbps)
			Options: --perf-p=12 --perf-cc=1 --perf-pp=1	(Speed: 23.967 mbps)
			Options: --perf-p=12 --perf-cc=1 --perf-pp=8	(Speed: 25.42 mbps)
			Options: --perf-p=12 --perf-cc=1 --perf-pp=16	(Speed: 24.672 mbps)
			Options: --perf-p=12 --perf-cc=1 --perf-pp=24	(Speed: 32.264 mbps)
			Options: --perf-p=12 --perf-cc=1 --perf-pp=32	(Speed: 26.214 mbps)
			Options: --perf-p=16 --perf-cc=1 --perf-pp=1	(Speed: 19.973 mbps)
			Options: --perf-p=16 --perf-cc=1 --perf-pp=8	(Speed: 28.926 mbps)
			Options: --perf-p=16 --perf-cc=1 --perf-pp=16	(Speed: 27.962 mbps)
			Options: --perf-p=16 --perf-cc=1 --perf-pp=24	(Speed: 28.926 mbps)
			Options: --perf-p=16 --perf-cc=1 --perf-pp=32	(Speed: 34.953 mbps)


### Getting a graph of a benchmark (not fully implemented yet) ###

    benchmark.py -n medium  -u markus  --visualize
    
Which will result in something like:

    Chart URL for series 2011-03-15 11:44:51.309713: 
    http://chart.apis.google.com/chart?chxr=0,0,32|1,0,16&chxs=1,676767,10.5,0,l,676767&chxt=x,y,x,y&chs=600x300&cht=s&chds=0,32,0,16,0,34.953&chd=t:0,1,8,16,24,32,1,8,16,24,32,1,8,16,24,32,1,8,16,24,32,1,8,16,24,32|0,1,1,1,1,1,4,4,4,4,4,8,8,8,8,8,12,12,12,12,12,16,16,16,16,16|17.12,6.991,9.869,10.107,8.066,7.626,19.508,21.509,16.777,20.972,23.967,28.926,27.962,31.069,18.236,25.42,23.967,25.42,24.672,32.264,26.214,19.973,28.926,27.962,28.926,34.953&chdl=Speed+in+mbps&chma=|5&chtt=Transfer+speed&chxl=0:|4|8|12|16|20|24|28|32|1:|4|8|12|16|20|24|28|32|2:|perf-pp|3:|perf-p&chxp=0,4,8,12,16,20,24,28,32|1,4,8,12,16,20,24,28,32|2,100|3,100
    
    Chart URL for series 2011-03-15 12:55:45.620249: 
    http://chart.apis.google.com/chart?chxr=0,0,32|1,0,16&chxs=1,676767,10.5,0,l,676767&chxt=x,y,x,y&chs=600x300&cht=s&chds=0,32,0,16,0,34.953&chd=t:0,1,8,16,24,32,1,8,16,24,32,1,8,16,24,32,1,8,16,24,32,1,8,16,24,32,0,1,8,16|0,1,1,1,1,1,4,4,4,4,4,8,8,8,8,8,12,12,12,12,12,16,16,16,16,16,0,1,1,1|17.12,6.991,9.869,10.107,8.066,7.626,19.508,21.509,16.777,20.972,23.967,28.926,27.962,31.069,18.236,25.42,23.967,25.42,24.672,32.264,26.214,19.973,28.926,27.962,28.926,34.953,17.12,6.991,9.869,10.107&chdl=Speed+in+mbps&chma=|5&chtt=Transfer+speed&chxl=0:|4|8|12|16|20|24|28|32|1:|4|8|12|16|20|24|28|32|2:|perf-pp|3:|perf-p&chxp=0,4,8,12,16,20,24,28,32|1,4,8,12,16,20,24,28,32|2,100|3,100
    
    Chart URL for series 2011-03-15 15:22:44.410233: 
    http://chart.apis.google.com/chart?chxr=0,0,32|1,0,16&chxs=1,676767,10.5,0,l,676767&chxt=x,y,x,y&chs=600x300&cht=s&chds=0,32,0,16,0,34.953&chd=t:0,1,8,16,24,32,1,8,16,24,32,1,8,16,24,32,1,8,16,24,32,1,8,16,24,32,0,1,8,16,0,1,8,16,24,32,1,8,16,24,32,1,8,16,24|0,1,1,1,1,1,4,4,4,4,4,8,8,8,8,8,12,12,12,12,12,16,16,16,16,16,0,1,1,1,0,1,1,1,1,1,4,4,4,4,4,8,8,8,8|17.12,6.991,9.869,10.107,8.066,7.626,19.508,21.509,16.777,20.972,23.967,28.926,27.962,31.069,18.236,25.42,23.967,25.42,24.672,32.264,26.214,19.973,28.926,27.962,28.926,34.953,17.12,6.991,9.869,10.107,17.12,6.991,9.869,10.107,8.066,7.626,19.508,21.509,16.777,20.972,23.967,28.926,27.962,31.069,18.236&chdl=Speed+in+mbps&chma=|5&chtt=Transfer+speed&chxl=0:|4|8|12|16|20|24|28|32|1:|4|8|12|16|20|24|28|32|2:|perf-pp|3:|perf-p&chxp=0,4,8,12,16,20,24,28,32|1,4,8,12,16,20,24,28,32|2,100|3,100

### Exporting a benchmark to a csv file ###

    benchmark.py -n medium  -u markus --csv-file=/home/markus/benchmark.csv
    
   
