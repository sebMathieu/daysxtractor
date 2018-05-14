DaysXtractor
=============
Extract a given number of representative days of a set of time series.

**Quick usage:**
> python3 -m daysxtrator -t 60 data/data.csv

Motivation
----------
Maybe you are confronted to a large amount of data representative of a
year, i.e. data for each quarters of the year. However, you are unwilling
to work with all of them and would like to focus only on a few days.
But if you select 10 days over the 365, which one would you select?
This program provides you these days and their weights.

Usage
--------
> python -m daysxtrator [options] data.csv

The data can be provided in a CSV or an XLS file.
The first column in the data gives the date.
Following columns are the different parameters characterizing the parameters.
The first two lines compose the header with the title of each column
on the first and the units in the second.
Examples can be found in the data folder.

**Options:**
- `-n 12`		Number of representative days to select.
- `-s name`		Use an optimization solver (cplex, gurobi, cbc, asl:scip, etc.).
- `-t 60`		Set the time limit to 60 seconds.
- `-v`			Verbose mode.
- `-p`			Plot.
- `-c days.csv` Check selected representative days. The first row of the file is a header. The next lines contains the days in the first column and their weights in the second.
- `-u`          Specifies that the second row of the excel files contains the units.
- `-o folder`   Output the plots in a specific folder.

Documentation can be built using doxygen with the following command.
> doxygen doc/doxyfile

Contributions
-------------
Feel free to contribute, sharing your own data reader or providing your personal day selector module.
