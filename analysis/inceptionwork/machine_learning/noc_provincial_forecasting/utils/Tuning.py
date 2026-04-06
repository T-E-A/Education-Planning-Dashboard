from abc import ABC, abstractmethod


class Tuner(ABC):
    def __init__(self, data, meta_data):
        self.data = data
        self.meta_data = meta_data
    
    @abstractmethod
    def TuneModel(self):
        pass

    
    @abstractmethod
    def Save_Hyperparams(self):
        pass
    