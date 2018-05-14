##@package excel_interface
#@author Sebastien MATHIEU

import time, datetime
import xlrd
import xlwt
from .data import *


## Parse an excel file with time series.
# The first column of the file is the date.
# Following columns are the different parameters characterizing the parameters.
# @param filePath Path to the excel file.
# @param with_units Boolean, true if the second row contains the units.
# @return Data with the time series.
def parseFile(filePath, with_units=False):
    # Open excel
    tic = time.clock()
    data = Data()
    workbook = xlrd.open_workbook(filePath, on_demand=True)
    sheet = workbook.sheet_by_index(0)

    # Parse header
    for c in range(1, sheet.ncols):
        label = TimeSeriesLabel(sheet.cell_value(0, c))
        if with_units:
            label.units = sheet.cell_value(1, c)
        data.labels.append(label)

    # Parse content
    dayRaw = None
    dayTimeSeries = {}
    takeDayRaw=False
    for r in range(2, sheet.nrows):
        row = sheet.row_values(r, 0, sheet.ncols)

        # New day?
        if row[0] != dayRaw:
            # New day
            dayRaw = row[0]
            day = row[0]

            # Cast it as a day
            try:
                if takeDayRaw or int(dayRaw) < 2000:  # The number is probably not a date
                    day = dayRaw
                    takeDayRaw = True
                else:
                    dayTuple = xlrd.xldate_as_tuple(dayRaw, workbook.datemode)  # Gregorian (year, month, day, hour, minute, nearest_second)
                    day = datetime.datetime(dayTuple[0], dayTuple[1], dayTuple[2], dayTuple[3], dayTuple[4], dayTuple[5])
            except Exception:
                day = dayRaw
                takeDayRaw = True

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

    # Finish the average computation
    for p in data.labelRanges():
        data.labels[p].datapoints = sheet.nrows-2
        data.labels[p].average /= sheet.nrows-2

    # Print what has been read
    toc = time.clock()
    print("Data for %s days read in %.2f seconds.\nLabels:" % (len(data.days()), toc-tic))
    for l in data.labels:
        print("\t%s: min=%.2f, average=%.2f, max=%.2f" % (l.name, l.min, l.average, l.max))
    print("")

    return data


## Parse an excel file with representative days.
# The first row of the file is a header.
# The next lines contains the days in the first column and their weights in the second.
# @param filePath Path to the excel file.
# @return Dictionary with the select days and their weights.
def parseRepresentativeDays(filePath):
    days = {}

    # Open the file
    workbook = xlrd.open_workbook(filePath, on_demand=True)
    sheet = workbook.sheet_by_index(0)

    # For each row
    takeDayRaw=False
    for r in range(1, sheet.nrows):
        # Get row
        row = sheet.row_values(r, 0, sheet.ncols)

        # Parse date
        day = row[0]

        # Cast it as a day
        try:
            if takeDayRaw or int(day) < 2000:  # The number is probably not a date
                takeDayRaw = True
            else:
                dayTuple = xlrd.xldate_as_tuple(day, workbook.datemode)  # Gregorian (year, month, day, hour, minute, nearest_second)
                day = datetime.datetime(dayTuple[0], dayTuple[1], dayTuple[2], dayTuple[3], dayTuple[4], dayTuple[5])
        except Exception:
            takeDayRaw = True

        # Get the weight
        weight = float(row[1])

        # Assign to dictionary
        days[day] = weight

    return days


## Write representative days into an excel file.
# @param days Dictionary with the days as keys and their weight as values.
# @param path Output file path.
def writeDays(days, path):
    wb = xlwt.Workbook()
    ws = wb.add_sheet('days')
    ws.write(0, 0, "Day")
    ws.write(0, 1, "Weight")
    date_style = xlwt.easyxf(num_format_str="dd/mm/yyyy")

    i = 1
    for d in sorted(days.keys()):
        ws.write(i, 0, d, date_style)
        ws.write(i, 1, days[d])
        i += 1
    wb.save(path)
