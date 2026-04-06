from abc import ABC, abstractmethod


class Evaluater(ABC):

    @abstractmethod
    def Calculate_Regression_Metrics(self):
        pass

    @abstractmethod
    def Save_Metrics(self):
        pass