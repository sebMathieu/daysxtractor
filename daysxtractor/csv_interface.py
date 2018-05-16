##@package csv_interface
#@author Sebastien MATHIEU

import time, datetime
from .data import *
import csv
import dateutil


## Parse a CSV file with time series.
# The first column of the file is the date, the second corresponds to the quarter (which may be empty).
# Following columns are the different parameters characterizing the parameters.
# The first two lines compose the header with the title of each column on the first and the units in the second.
# @param filePath Path to the excel file.
# @param with_units Boolean, true if the second row contains the units.
# @return Data with the time series.
def parseFile(filePath, with_units=False):
    # Open excel
    tic = time.clock()

    with open(filePath, newline='') as file:
        data = parseData(file, with_units)

    # Print what has been read
    toc = time.clock()
    print("Data for %s days read in %.2f seconds.\nLabels:" % (len(data.days()), toc-tic))
    for l in data.labels:
        print("\t%s: min=%.2f, average=%.2f, max=%.2f" % (l.name, l.min, l.average, l.max))
    print("")

    return data


## Parse a CSV file with time series.
# The first column of the file is the date, the second corresponds to the quarter (which may be empty).
# Following columns are the different parameters characterizing the parameters.
# The first two lines compose the header with the title of each column on the first and the units in the second.
# @param file File pointer
# @param with_units Boolean, true if the second row contains the units.
# @return Data with the time series.
def parseData(file, with_units=False):
    data = Data()
    reader = csv.reader(file)

    # Header
    header = next(reader)
    if with_units:
        units_header = next(reader)

    for j in range(1, len(header)):
        label = TimeSeriesLabel(header[j])
        if with_units:
            label.units = units_header[j]
        data.labels.append(label)

    # Content
    day = None
    dayTimeSeries = {}
    rows = 0
    for row in reader:
        t = dateutil.parser.parse(row[0])
        d = t.date()

        if d != day:
            day = d

            # Initialize the time series
            dayTimeSeries = {}
            for p in range(len(data.labels)):
                dayTimeSeries[p] = []
            data.timeSeries[day] = dayTimeSeries

        # Add the data
        for p in data.labelRanges():
            v = float(row[p+1])
            dayTimeSeries[p].append(v)

            # Update min-max
            data.labels[p].min = min(data.labels[p].min, v) if data.labels[p].min is not None else v
            data.labels[p].max = max(data.labels[p].max, v) if data.labels[p].max is not None else v
            if data.labels[p].average is None:
                data.labels[p].average = v
            else:
                data.labels[p].average += v

        rows += 1

    # Finish the average computation
    for p in data.labelRanges():
        data.labels[p].datapoints = rows
        data.labels[p].average /= rows

    return data

## Parse an excel file with representative days.
# The first row of the file is a header.
# The next lines contains the days in the first column and their weights in the second.
# @param filePath Path to the excel file.
# @return Dictionary with the select days and their weights.
def parseRepresentativeDays(filePath):
    days = {}

    with open(filePath, newline='') as file:
        reader = csv.reader(file)

        next(reader)  # Skip header
        for row in reader:
            # Parse
            t = dateutil.parser.parse(row[0])
            d = t.date()
            w = float(row[1])

            # Assign to dictionary
            days[d] = w

    return days


## Write representative days into an excel file.
# @param days Dictionary with the days as keys and their weight as values.
# @param path Output file path.
def writeDays(days, path):

    with open(path, "w", newline='') as file:
        writer = csv.writer(file)

        writer.writerow(["Day", "Weight"])
        for d in sorted(days.keys()):
            writer.writerow([d, days[d]])
