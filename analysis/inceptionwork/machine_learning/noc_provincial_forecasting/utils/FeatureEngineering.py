from abc import ABC, abstractmethod


class FeatureEngineer(ABC):

    @abstractmethod
    def Add_Lags(self):
        pass

    @abstractmethod
    def Add_Indicators(self):
        pass 
    
    @abstractmethod
    def Add_Supplementary_Features(self):
        pass

    @abstractmethod 
    def Add_Date_Features(self):
        pass
    
    @abstractmethod
    def Assign_Directional_Class(self):
        pass