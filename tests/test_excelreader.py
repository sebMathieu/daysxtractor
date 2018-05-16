import unittest

from daysxtractor import parseFile


## Test the excel reader.
class TestExcelReader(unittest.TestCase):

    def setUp(self):
        self.data = parseFile('unittestdata.xlsx')

    ## Test the number of elements read.
    def testLength(self):
        self.assertEqual(len(self.data.days()), 31)

    ## Test the computed averages.
    def testAverages(self):
        averages = {'Wind power': '1.93', 'Load': '10590.58', 'Energy prices': '53.91'}
        for l in self.data.labels:
            self.assertEqual('%.2f' % l.average, averages[l.name])


if __name__ == '__main__':
    unittest.main()

