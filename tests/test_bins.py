import unittest

from daysxtractor import parseFile
from daysxtractor import Bins


## Test the bins.
class TestBins(unittest.TestCase):

    def setUp(self):
        self.data = parseFile('unittestdata.xlsx')
        self.bins = Bins(self.data, 20)

    ## Test the maximum population of the bins
    def testPopulations(self):
        maxPopulations = {'Wind power': 35.72, 'Load': 9.07, 'Energy prices': 23.52}  # Maximum populations in %
        for p in self.bins.labelRanges():
            populationMin, populationMax = self.bins.population(p)
            self.assertAlmostEqual(populationMax*100, maxPopulations[self.bins.labels[p].name], 2)