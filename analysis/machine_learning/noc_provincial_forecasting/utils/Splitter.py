import pandas as pd 

class Splitter():
    def __init__(self, Data: pd.DataFrame, Set_Year_Markers):
        self.Data = Data
        self.Set_Year_Markers = Set_Year_Markers
    
    def Get_Training_Set(self, validateStart):
        try:
            trainSet = self.Data[self.Data['year'] < validateStart]
            return trainSet
        except:
            return pd.DataFrame()
    
    def Get_Validation_Set(self, validateStart,testStart):
        try:
            validateSet = self.Data[(self.Data['year'] >= validateStart) & (self.Data['year'] < testStart)]
            return validateSet

        except: 
            return pd.DataFrame()
    
    def Get_Test_Set(self, testStart):
        try:
            testSet = self.Data[self.Data['year'] >= testStart]
            return testSet
        except:
            return pd.DataFrame()
    
    def Generate_Sets(self):
        All_Sets = {
            'train': self.Get_Training_Set(validateStart=self.Set_Year_Markers['validateStart']),
            'validate': self.Get_Validation_Set(validateStart=self.Set_Year_Markers['validateStart'],
                                                testStart=self.Set_Year_Markers['testStart']
                                                ),
            'test': self.Get_Test_Set(testStart=self.Set_Year_Markers['testStart'])
                                            
        }

        return All_Sets