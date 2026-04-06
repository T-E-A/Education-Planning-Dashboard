from abc import ABC, abstractmethod

class PreProcessesor(ABC):
    
    @abstractmethod
    def GetData(self):
        """
        Implement logic for retrieving the appropriate data. 
        """
        pass

    

    @abstractmethod
    def ProcessNulls(self):
        pass 
    
    @abstractmethod
    def EvaluateSetSizes(self, trainingYear: dict, validationYear: dict, testYear: dict): 
        """
        Implement Logic for splitting the data based on the year and determining. 
        trainingYear => a dictionary containing end of training period and minimum number of samples per group. 
        validationYear => a dictionary containing end of validation period and minimum number of samples per group.
        testYear => a dictionary containing STAR of the test period and minimum number of samples per group.
        """

    @abstractmethod
    def ReduceSampleSize(self):
        """
        Reduce the entire Sample to only those groups (Province of Economic Region) that have the minimum number of samples per set 
        """
    @abstractmethod
    def SaveSample(self):
        """
        Save the sample size for further processing. 

        """