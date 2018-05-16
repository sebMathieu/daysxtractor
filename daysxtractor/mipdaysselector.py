##@package mipdaysselector
# @author Sebastien MATHIEU

from __future__ import division

import math
from pyomo.environ import *
from pyomo.opt import SolverFactory

from .daysselector import DaysSelector
from .minpopbins import MinPopBins as Bins


## Selector of days based on a mixed-interger linear optimization problem.
# The formulation is a slightly modified version of the paper: K. Poncelet, H. Hoschle, E. Delarue, W. D'haeseleer, "Selecting representative days for investment planning models".
class MIPDaysSelector(DaysSelector):
    ## Constructor.
    # @param binsPerTimeSeries Number of bins discretizing the time series.
    # @param numberRepresentativeDays Number of representative days to select.
    # @param timelimit Time limit for the optimization in seconds.
    # @param solverName Name of the optimization solver to use (cplex, cbc, asl:cplexamp, gurobi, etc.).
    # @param verbose Verbose boolean.
    def __init__(self, numberRepresentativeDays=24, timelimit=60, binsPerTimeSeries=40, solverName='cplex',
                 verbose=False):
        self.binsPerTimeSeries = binsPerTimeSeries
        self.numberRepresentativeDays = numberRepresentativeDays
        self.timeLimit = timelimit
        self.verbose = verbose

        # Prepare the solver
        self.solver = SolverFactory(solverName)
        if self.solver is None:
            raise Exception('Unable to use the solver "%s".' % self.solver)

        # Define the time limit parameter in function of the solver
        if solverName == 'cbc':
            self._timelimitParameter = 'sec'
        else:
            self._timelimitParameter = "timelimit"

    def selectDays(self, data):
        bins = Bins(data, self.binsPerTimeSeries)
        D = len(data.days())

        # Sets of the of the optimization model
        model = ConcreteModel()
        model.days = Set(initialize=bins.daysRange())

        def buildBinSet(model):
            return ((p, b) for p in bins.labelRanges() for b in bins.binRange(p))

        model.binSet = Set(dimen=2, initialize=buildBinSet)

        # Create the variables of the optimization model
        model.u = Var(model.days, domain=Binary)  # Select the day yes/no
        model.w = Var(model.days, domain=NonNegativeReals, bounds=(0, D))  # Weight of the day
        model.e = Var(model.binSet, domain=NonNegativeReals)  # Bin approximation error

        # Create objective
        def obj(m):
            expr = 0.0
            for p in bins.labelRanges():
                for b in bins.binRange(p):
                    # Weights could be added to give more importance to some time series
                    expr += m.e[p, b]
            return expr

        model.obj = Objective(rule=obj)  # By default to minimize

        # Error definition
        errorDefLbExpr = {}
        errorDefUbExpr = {}
        for p in bins.labelRanges():
            errorDefLbExpr[p] = {}
            errorDefUbExpr[p] = {}

            cumulatedBinSize = 0
            cumulatedBinApprox = 0.0
            for b in bins.binRange(p):
                cumulatedBinSize += bins.binSize[p][b]

                binApprox = 0.0
                for d in bins.daysRange():
                    binApprox += model.w[d] * bins.A[p][b][d]
                cumulatedBinApprox += binApprox

                errorDefLbExpr[p][b] = (model.e[p, b] >= cumulatedBinSize - cumulatedBinApprox)
                errorDefUbExpr[p][b] = (model.e[p, b] >= -cumulatedBinSize + cumulatedBinApprox)

        def errorDefLb(m, p, b):
            return errorDefLbExpr[p][b]

        model.errorDefLb = Constraint(model.binSet, rule=errorDefLb)

        def errorDefUb(m, p, b):
            return errorDefUbExpr[p][b]

        model.errorDefUb = Constraint(model.binSet, rule=errorDefUb)

        # Sets the number of representative days
        model.nRepresentativeDays = Constraint(expr=summation(model.u) == self.numberRepresentativeDays)

        # Activate only the weights of selected days
        def weightActivation(m, d):
            return model.w[d] <= model.u[d] * (D / 2 if self.numberRepresentativeDays > 0.02 * D else D)

        model.weightActivation = Constraint(model.days, rule=weightActivation)

        # Weight activation cut
        if self.numberRepresentativeDays < D / 2:
            def weightActivationCut(m, d):
                return model.w[d] >= model.u[d]

            model.weightActivationCut = Constraint(model.days, rule=weightActivationCut)

        # Sum of the weights
        model.sumWeights = Constraint(expr=summation(model.w) == D)

        # Solve
        self.solver.options[self._timelimitParameter] = self.timeLimit
        if self.verbose:
            print('Solving the optimization problem using "%s"...' % self.solver.name)
        self.solver.solve(model, keepfiles=False, tee=self.verbose)  # tee=True to display the solver output
        if len(model.solutions) == 0:
            raise Exception('No solution found.')

        # Load results
        if self.verbose:
            print("Best solution found has an objective value of %.2f." % value(model.obj))
        selectedDays = {}
        for d in bins.daysRange():
            if model.u[d].value > 0.5:
                selectedDays[bins.days[d]] = model.w[d].value

        return selectedDays

## @var binsPerTimeSeries
# Number of bins discretizing the time series.
## @var solver
# Instance of the MIP solver called to solve the optimization problem
## @var numberRepresentativeDays
# Number of representative days to select.
## @var timelimit
# Time limit for the optimization in seconds.
## @var verbose
# Verbose (True or False).
## @var _timelimitParameter
# Name of the timelimit paramater for the instanciated solver.
