##@package data
#@author Sebastien MATHIEU

import math
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as pyplot


## Class containing the time series data.
class Data:
    def __init__(self):
        self.labels=[]
        self.timeSeries={}

    ## Get the list of days.
    # @return List of days.
    def days(self):
        return self.timeSeries.keys()

    ## Get the range of index of the labels.
    # @return Range of labels.
    def labelRanges(self):
        return range(len(self.labels))

    ## Plot a timeseries.
    # @param label Label of the timeseries.
    # @param resolution of the chart in ]0,1[, the smaller the better.
    # @param pathPrefix Prefix of the output file.
    def plotTimeseries(self, label, resolution=0.01, pathPrefix=""):
        labelIndex = self.labels.index(label)

        # Define the bins
        if resolution <= 0 or resolution >= 1:
            raise Exception("Invalid resolution %s which is outside of the range ]0,1[." % resolution)
        ticks = []
        v = 0
        while v < 1.0:
            ticks.append(v)
            v += resolution
        ticks.append(1.0)
        B = len(ticks)

        # Compute the bin sizes
        binSize = [0]*B
        observations = 0
        for dayData in self.timeSeries.values():
            dayTimeseries = dayData[labelIndex]
            observations += len(dayTimeseries)
            for v in dayTimeseries:
                bucket = B-1-math.floor((v-label.min)/(label.max-label.min)*B)
                binSize[bucket] += 1

        # Compute cumulated sums
        cumulated = [0]*B
        binSize[0] /= observations
        cumulated[0] = binSize[0]
        for b in range(1, B):
            binSize[b] /= observations
            cumulated[b] = cumulated[b-1]+binSize[b]

        # Plot
        x = [v*100 if v < 100 else 100.0 for v in cumulated]
        y = [label.max-v*(label.max-label.min) for v in ticks]

        pyplot.plot(x, y, 'k')
        pyplot.xticks(range(0, 101, 10))
        pyplot.axis([0, 100.0, label.min, label.max])

        pyplot.xlabel('Duration [%]')
        pyplot.ylabel('Duration curve values')
        if label.units is not None and label.units != "":
            pyplot.title('%s [%s]' % (label.name, label.units))
        else:
            pyplot.title('%s' % label.name)
        pyplot.savefig(pathPrefix + label.name + ".pdf")

        pyplot.close()

    ## Plot the original timeseries and the one obtained with the representative days.
    # @param label Label of the timeseries.
    # @param representativeDays List of representative days
    # @param resolution Resolution of the chart in ]0,1[, the smaller the better.
    # @param pathPrefix Prefix of the output file.
    def plotRepresentativeTimeseries(self, label, representativeDays, resolution=0.01, pathPrefix=""):
        labelIndex = self.labels.index(label)

        # Define the bins
        if resolution <= 0 or resolution >= 1:
            raise Exception("Invalid resolution %s which is outside of the range ]0,1[." % resolution)
        ticks = []
        v = 0
        while v < 1.0:
            ticks.append(v)
            v += resolution
        ticks.append(1.0)
        B = len(ticks)

        # Compute the original bin sizes
        binSize = [0]*B
        observations = 0
        for dayData in self.timeSeries.values():
            dayTimeseries = dayData[labelIndex]
            observations += len(dayTimeseries)
            for v in dayTimeseries:
                bucket = B-1-math.floor((v-label.min)/(label.max-label.min)*B)
                binSize[bucket] += 1

        # Compute cumulated sums
        cumulated = [0]*B
        binSize[0] /= observations
        cumulated[0] = binSize[0]
        for b in range(1, B):
            binSize[b] /= observations
            cumulated[b] = cumulated[b-1]+binSize[b]

        # Compute the representative bin sizes
        reprBinSize = [0]*B
        # Find the original indexes of each days
        for day, w in representativeDays.items():
            dayTimeseries = self.timeSeries[day][labelIndex]
            for v in dayTimeseries:
                bucket = B-1-math.floor((v-label.min)/(label.max-label.min)*B)
                reprBinSize[bucket] += w

        # Compute representative cumulated sums
        reprCumulated = [0]*B
        reprBinSize[0] /= observations
        reprCumulated[0] = reprBinSize[0]
        for b in range(1, B):
            reprBinSize[b] /= observations
            reprCumulated[b] = reprCumulated[b-1]+reprBinSize[b]

        # Plot
        x = [v*100 if v < 100 else 100.0 for v in cumulated]
        reprX = [v*100 if v < 100 else 100.0 for v in reprCumulated]
        y = [label.max-v*(label.max-label.min) for v in ticks]

        pyplot.plot(x, y, 'k', reprX, y, 'k--')
        pyplot.xticks(range(0, 101, 10))
        pyplot.axis([0, 100.0, label.min, label.max])

        pyplot.xlabel('Duration [%]')
        pyplot.ylabel('Duration curve values')
        if label.units is not None and label.units != "":
            pyplot.title('%s [%s]' % (label.name, label.units))
        else:
            pyplot.title(label.name)
        pyplot.legend(['Original', 'Representative days'])
        pyplot.savefig(pathPrefix + label.name + ".pdf")

        pyplot.close()

    ## @var labels
    # List of TimeSeriesLabels.
    ## @var timeSeries
    # Dictionary with the time series taking as key the day and as value a dictionary label index/array of values.


## Time series labels and information.
class TimeSeriesLabel:
    def __init__(self, name=None):
        self.name = name
        self.min = None
        self.max = None
        self.average = None
        self.datapoints = 0
        self.units = ""

    def __repr__(self):
        return "%s with %s data points: min=%.2f, average=%.2f, max=%.2f" % (self.datapoints, self.name, self.min, self.average, self.max)

    ## @var name
    # Name of the time series.
    ## @var min
    # Minimum over the time series.
    ## @var max
    # Maximum over the time series.
    ## @var average
    # Average over the time series.
    ## @var datapoints
    # Number of data points in the time series.
    ## @var units
    # Units.
