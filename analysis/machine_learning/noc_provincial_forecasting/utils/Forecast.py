from abc import ABC, abstractmethod


class Forecaster(ABC):
    def __init__(self, data, meta_data):
        self.data = data
        self.meta_data = meta_data

    @abstractmethod
    def Generate_Forecasts(self):
        pass

    @abstractmethod
    def Save_Forecasts(self):
        pass