##@package daysselector
# @author Sebastien MATHIEU

from abc import ABCMeta, abstractmethod


## Abstract class of a day selector.
class DaysSelector:
    __metaclass__ = ABCMeta

    ## Select representative days from time series.
    # @param data Data with the time series.
    # @return Dictionary with the select days and their weights.
    @abstractmethod
    def selectDays(self, data):
        return None
