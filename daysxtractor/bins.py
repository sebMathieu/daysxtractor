# @package bins
# @author Sebastien MATHIEU

import math, copy

## Create bins for time series.
class Bins:
    ## Create bins from data.
    # @param data Data with the time series.
    # @param binsPerTimeSeries Default number of bins per time series.
    def __init__(self, data=None, binsPerTimeSeries=10):
        self.labels = None
        self.days = None
        self.binStart = None
        self.binSize = None
        self.binsNumber = None
        self.cumulatedBinSize = None
        self.A = None

        # Actually create the bins
        if data is not None:
            self._createBins(data, binsPerTimeSeries)

    ## Create bins from representative days.
    # @param bins Bins of the initial time series.
    # @param representativeDays Dictionary with the selected representative days as keys and their weights as values.
    def createFromRepresentativeDays(self, bins, representativeDays):
        self.labels = bins.labels
        self.days = {}
        self.binStart = copy.deepcopy(bins.binStart)
        self.binsNumber = copy.deepcopy(bins.binsNumber)

        # Find the original indexes of each days
        dayIndex = 0
        origIndexes = {}
        weights = {}
        for day, w in representativeDays.items():
            self.days[dayIndex] = day
            weights[dayIndex] = w
            for oIndex, d in bins.days.items():
                if d == day:
                    origIndexes[dayIndex] = oIndex
                    break
            dayIndex += 1

        # Create A and binSize
        self.A = []
        self.binSize = []
        for p in self.labelRanges():
            self.A.append([])
            self.binSize.append([0.0]*len(self.binRange(p)))
            for b in self.binRange(p):
                self.A[p].append([bins.A[p][b][origIndexes[d]] for d in self.daysRange()])
                for d in self.daysRange():
                    self.binSize[p][b] += weights[d]*self.A[p][b][d]

        # Compute cumulated bin size
        self._computeCumulatedBinSize()

    ## Get the range of index of the labels.
    # @return Range of labels.
    def labelRanges(self):
        return range(len(self.labels))

    ## Get the range of bins of a label.
    # @param p Label index.
    def binRange(self, p):
        return range(self.binsNumber[p])

    ## Get the range of index of the days.
    # @return Range of days.
    def daysRange(self):
        return range(len(self.days))

    ## Compute the normalized root-mean-square error (NRMSE) between the original duration curve and the approximated duration curve.
    # @param p Label of the duration curve to evaluate.
    # @param bins Approximated duration curves.
    # @return Value as a float in [0,1].
    def nrmsError(self, p, bins):
        B = self.binsNumber[p]
        if B != bins.binsNumber[p]:
            raise Exception("Invalid number of bins for label %s. Original has %s bins and the approximated %s." % (p, B, bins.binsNumber[p]))

        result = 0.0
        maxDC = None
        minDC = None
        for b in self.binRange(p):
            binValue = (self.binStart[p][b]-self.binStart[p][b-1])/2
            DC = self.binSize[p][b]*binValue
            maxDC = DC if maxDC is None else max(maxDC, DC)
            minDC = DC if minDC is None else min(minDC, DC)
            dSize = DC-bins.binSize[p][b]*binValue
            result += dSize*dSize
        return math.sqrt(result/B)/(maxDC-minDC)

    ## Compute the relative area error between the original duration curve and the approximated duration curve.
    # This measure directly corresponds to the average value of the time series.
    # @param p Label of the duration curve to evaluate.
    # @param bins Approximated duration curves.
    # @return Value as a float in [0,1].
    def relativeAreaError(self, p, bins):
        if self.binsNumber[p] != bins.binsNumber[p]:
            raise Exception("Invalid number of bins for label %s. Original has %s bins and the approximated %s." % (p, self.binsNumber[p], bins.binsNumber[p]))

        totalCurve = 0
        totalApproxCurve = 0.0
        for b in self.binRange(p):
            binValue = (self.binStart[p][b]-self.binStart[p][b-1])/2
            totalCurve += self.binSize[p][b]*binValue
            totalApproxCurve += bins.binSize[p][b]*binValue
        return abs((totalCurve-totalApproxCurve)/totalCurve)

    ## Create bins discretizing the time series.
    # @param data Data with the time series.
    # @param binsPerTimeSeries Number of bins per time series.
    def _createBins(self, data, binsPerTimeSeries):
        self.labels = data.labels

        # Bins number
        self.binsNumber = [binsPerTimeSeries]*len(self.labelRanges())
        self.binStart = []
        for p in self.labelRanges():
            label = data.labels[p]
            self.binStart.append([(label.max-label.min)*b/binsPerTimeSeries+label.min for b in range(binsPerTimeSeries)])
            self.binStart[p].append(label.max)

        # Populate the bins
        self._createBinsFromStartValues(data)
        self._computeCumulatedBinSize()

    ## Create the bins using the starting value of each bin.
    # Assumes that labels and binStart are assigned.
    # @param data Data.
    def _createBinsFromStartValues(self, data):
        self.labels = data.labels # By security

        # Init
        self.binSize = [] # Size of the bin for a given time series binSize[p,b].
        self.A = [] # Number of element for a given time series and bin of a day A[p,b,d].
        for p in self.labelRanges():
            self.binSize.append([])
            self.A.append([])
            for b in range(len(self.binStart[p])-1):
                self.binSize[p].append(0)
                self.A[p].append([0]*len(data.days()))

        # Fill with the data
        dayIndex = 0
        self.days = {}
        for d, dayData in data.timeSeries.items():
            self.days[dayIndex] = d
            for p, values in dayData.items():
                label = data.labels[p]
                for v in values:
                    # Find the bin
                    b = 1
                    while b < len(self.binStart[p])-1:
                        if self.binStart[p][b] > v:
                            break
                        b += 1
                    b -= 1

                    # Populate
                    self.binSize[p][b] += 1
                    self.A[p][b][dayIndex] += 1
            dayIndex += 1

    ## Compute the cumulated bin sizes.
    def _computeCumulatedBinSize(self):
        self.cumulatedBinSize = []
        for p in self.labelRanges():
            self.cumulatedBinSize.append([self.binSize[p][0]])
            for b in range(1, len(self.binSize[p])):
                self.cumulatedBinSize[p].append(self.cumulatedBinSize[p][b-1]+self.binSize[p][b])

    ## Compute the population of the bins for a given parameter.
    # @param p Label index.
    # @return Tuple (min,max) among the bins in [0,1].
    def population(self,p):
        # Population
        pb = self.binSize[p]
        binMin = min(pb)
        binMax = max(pb)
        total = sum(pb)

        return binMin/total, binMax/total

    ## @var labels
    # List with the labels of the time series.
    ## @var days
    # Dictionary taking as key the day index and as value the day itself.
    ## @var binsNumber
    # Number of bins for each label.
    ## @var binStart
    # Starting value of each bin. The maximum is added as an additional element for convenience.
    ## @var binSize
    # For each parameter, size of each bin.
    ## @var cumulatedBinSize
    # Cumulated sum over the bin sizes for each parameter and each bin.
    ## @var A
    # Number of periods in each bin of a given day.
