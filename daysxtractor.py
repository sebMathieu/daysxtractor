##@package daysxtractor
#@author Sebastien MATHIEU

import sys, time, getopt, datetime

from src.mipdaysselector import MIPDaysSelector
import src.excelReader as excelReader
from src.samplingdaysselector import SamplingDaysSelector
from src.minpopbins import MinPopBins as Bins

## Entry point of the program.
# @param argv Program parameters.
def main(argv):
	# Default parameters
	numberRepresentativeDays = 24
	timelimit = 60
	solver = None
	verbose = False
	plot=False

	# Parse parameters
	if len(argv) < 1:
		displayHelp()
		sys.exit(2)
	filePath = argv[-1]

	try:
	   	opts, args = getopt.getopt(argv[0:-1],'n:s:t:vp',['number=','solver=','timelimit=','verbose','plot'])
	except getopt.GetoptError as err:
		displayHelp()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-n', '--number'):
			n = int(arg)
			if n < 1:
				raise Exception('One representative days is the minimum number accepted.')
			numberRepresentativeDays = n
		elif opt in ('-s', '--solver'):
			solver = arg
		elif opt in ('-t', '--timelimit'):
			t = float(arg)
			if t < 0.0:
				raise Exception('Only positive timelimits are accepted.')
			timelimit = t
		elif opt in ('-v', '--verbose'):
			verbose = True
		elif opt in ('-p', '--plot'):
			plot = True

	# Read the data
	data = excelReader.parseFile(filePath)

	# Instantiate the day selector
	daySelector = None
	if solver is None:
		print("WARNING: No optimization solver set. Try using an optimization solver (e.g. cplex, gurobi, cbc, etc.) for better results.")
		daySelector = SamplingDaysSelector(numberRepresentativeDays=numberRepresentativeDays, timelimit=timelimit, verbose=verbose)
	else:
		daySelector = MIPDaysSelector(numberRepresentativeDays=numberRepresentativeDays, timelimit=timelimit, solverName=solver, verbose=verbose)

	# Select days
	tic = time.time()
	representativeDays = daySelector.selectDays(data)
	toc = time.time()

	# Print result
	print("\nRepresentative days and weights found after %.2fs:" % (toc-tic))
	for day in sorted(representativeDays.keys()):
		print("\t%.2f\t-\t%s" % (representativeDays[day], day.strftime("%d %B %Y") if isinstance(day, datetime.datetime) else day))

	bins = Bins(data, daySelector.binsPerTimeSeries)
	representativeBins = Bins()
	representativeBins.createFromRepresentativeDays(bins, representativeDays)

	# Plot
	if plot:
		for label in data.labels:
			data.plotRepresentativeTimeseries(label, representativeDays)

	# Error measures
	print("\nError measures:")
	print("\t- Bins population:")
	for p in bins.labelRanges():
		populationMin, populationMax = bins.population(p)
		print("\t\t%s: min=%.2f%%, max=%.2f%%" % (bins.labels[p].name, populationMin*100.0, populationMax*100.0))

	print("\t- Normalized root-mean-square error:")
	for p in bins.labelRanges():
		print("\t\t%s: %.2f%%" % (bins.labels[p].name, bins.nrmsError(p, representativeBins)*100.0))

	print("\t- Relative area error:")
	for p in bins.labelRanges():
		print("\t\t%s: %.2f%%" % (bins.labels[p].name, bins.relativeAreaError(p, representativeBins)*100.0))

## Display help of the program.
def displayHelp():
	text = ''
	text += 'Usage :\n\tpython daysxtractor.py [options] data.xlsx\n'
	text += 'Extract a given number of representative days of a set of time series.\n'
	text += '\nThe first column of the excel file is the date, the second corresponds to the quarter (which may be empty).\n'
	text += 'Following columns are the different parameters characterizing the parameters.\n'
	text += 'The first two lines compose the header with the title of each column on the first and the units in the second.\n\n'

	text += 'Options:\n'
	text += '\t-n 24\t\t --number 24\t\tNumber of representative days to select.\n'
	text += '\t-s name\t\t --solver name\t\tUse an optimization solver (cplex, gurobi, cbc, asl:scip, etc.).\n'
	text += '\t-t 60\t\t --timelimit 60\t\tSet the time limit to 60 seconds.\n'
	text += '\t-v\t\t --verbose\t\tVerbose mode.\n'
	text += '\t-p\t\t --plot\t\t\tPlot.\n'

	print(text)

# Starting point from python #
if __name__ == "__main__":
	main(sys.argv[1:])