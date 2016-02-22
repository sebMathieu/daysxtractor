# @package minpopbins
# @author Sebastien MATHIEU

import time

from .bins import Bins


## Create bins for time series with a minimum population.
class MinPopBins(Bins):
    ## Create bins from data.
    # @param data Data with the time series.
    # @param binsPerTimeSeries Default number of bins per time series.
    # @param minPop Minimum relative population of a bin in [0,1]. A value of 0 will still merge the 0 population bins.
    def __init__(self, data=None, binsPerTimeSeries=10, minPop=0):
        self.minPop = minPop
        Bins.__init__(self, data, binsPerTimeSeries)

    def _createBins(self, data, binsPerTimeSeries):
        self.labels = data.labels

        # Bins number
        self.binsNumber = [binsPerTimeSeries] * len(self.labelRanges())
        self.binStart = []
        for p in self.labelRanges():
            label = data.labels[p]
            self.binStart.append(
                [(label.max - label.min) * b / binsPerTimeSeries + label.min for b in range(binsPerTimeSeries)])
            self.binStart[p].append(label.max)

        # Populate the bins
        Bins._createBinsFromStartValues(self, data)

        # Merge consecutive bins with low population
        for p in self.labelRanges():
            # Merge unpopulated
            B = self.binsNumber[p]
            inititialB = B
            minOccurences = self.minPop * self.labels[p].datapoints
            b = 0
            while b < B:
                if self.binSize[p][b] == 0 or (self.binSize[p][b] < minOccurences
                                               and self.binSize[p][b + 1] < minOccurences):
                    # Merge with the previous
                    self.binSize[p][b + 1] += self.binSize[p][b]
                    self.binStart[p][b + 1] = self.binStart[p][b]

                    del self.binStart[p][b]
                    del self.binSize[p][b]
                    B -= 1
                else:
                    b += 1

            # Split the most populated
            while B < inititialB:
                b = self.binSize[p].index(max(self.binSize[p]))

                self.binStart[p].insert(b + 1, (self.binStart[p][b + 1] + self.binStart[p][b]) / 2.0)

                # Estimates impact on bin size
                self.binSize[p].insert(b + 1, self.binSize[p][b] / 2.0)
                self.binSize[p][b] /= 2.0

                B += 1

        Bins._createBinsFromStartValues(self, data)

        # Compute cumulated sizes
        self._computeCumulatedBinSize()

    ## @var minPop
    # Minimum relative population of a bin in [0,1].
