##@package samplingdaysselector
# @author Sebastien MATHIEU

from __future__ import division

import math, time, random

from .daysselector import DaysSelector
from .minpopbins import MinPopBins as Bins


## Select representative days by random sampling.
class SamplingDaysSelector(DaysSelector):
    ## Constructor
    # @param binsPerTimeSeries Number of bins discretizing the time series.
    # @param numberRepresentativeDays Number of representative days to select.
    # @param timelimit Time limit for the process.
    # @param verbose Verbose boolean.
    def __init__(self, numberRepresentativeDays=24, timelimit=60, binsPerTimeSeries=40, verbose=False):
        self.binsPerTimeSeries = binsPerTimeSeries
        self.numberRepresentativeDays = numberRepresentativeDays
        self.timelimit = timelimit
        self.verbose = verbose

    def selectDays(self, data):
        # Prepare parameters
        random.seed(42)
        bins = Bins(data, self.binsPerTimeSeries)
        D = len(data.days())

        # Sample
        samples = 0
        bestObj = None
        bestSelection = None
        tic = time.time()
        if self.verbose:
            print("Random sampling of representative days...")
        while time.time() - tic < self.timelimit:
            # Select days
            selectedDays = set()
            while len(selectedDays) < self.numberRepresentativeDays:
                selectedDays.add(random.randrange(0, D))

            # Obtain weights & evaluate
            objValue, selectedDaysWeights = self._evaluateDays(list(selectedDays), bins)
            if bestObj is None or bestObj > objValue:
                bestObj = objValue
                bestSelection = selectedDaysWeights

                # Print
                if self.verbose:
                    print('\tNew incumbent with an objective value of %.2f.' % bestObj)

            # Iterate
            samples += 1

        if self.verbose:
            print("Best solution found has an objective value of %.2f after %s samples." % (bestObj, samples))

        # Reformat selection
        return {bins.days[d]: v for d, v in bestSelection.items()}

    ## Evaluate a set of selected days.
    # @param selectedDays List of selected days index.
    # @param bins Bins of the time series.
    # @return (objValue,selectedDaysWeights) The objective value of the selected days and their weights in a dictionary.
    def _evaluateDays(self, selectedDays, bins):
        # Allocate results
        objValue = 0.0
        selectedDaysWeights = {d: 0 for d in selectedDays}

        # Assign each original day to one selected day
        pRange = range(len(bins.labels))
        bRange = range(self.binsPerTimeSeries)
        for j in range(len(bins.days)):
            # Find the closest day
            dCandidate = 0
            candidateDist = len(bins.days) * self.binsPerTimeSeries * len(bins.labels)
            for i in range(len(selectedDays)):
                dDist = self._daysDistance(i, j, pRange, bRange, bins.A)
                if dDist < candidateDist:
                    dCandidate = i
                    candidateDist = dDist

            # Assign weight
            selectedDaysWeights[selectedDays[dCandidate]] += 1

        # Compute objective value
        for p in pRange:
            for b in bRange:
                error = bins.cumulatedBinSize[p][b]
                for d in selectedDays:
                    error -= bins.A[p][b][d]
                objValue += abs(error)

        return objValue, selectedDaysWeights

    ## Compute the distance between two days.
    # @param d1 First day.
    # @param d2 Second day.
    # @param pRange Range of the parameters.
    # @param bRange Range of the bins.
    # @param A Number of periods in each bin of a given day.
    # @return Distance.
    def _daysDistance(self, d1, d2, pRange, bRange, A):
        dist = 0
        for p in pRange:
            for b in bRange:
                dist += abs(A[p][b][d1] - A[p][b][d2])
        return dist

    ## @var binsPerTimeSeries
    # Number of bins discretizing the time series.
    ## @var numberRepresentativeDays
    # Number of representative days to select.
    ## @var timeLimit
    # Time limit for the optimization in seconds.
    ## @var verbose
    # Verbose (True or False).
