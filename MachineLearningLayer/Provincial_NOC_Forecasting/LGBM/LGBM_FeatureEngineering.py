from MachineLearningLayer.Utils.FeatureEngineering import FeatureEngineer
import pandas as pd
import polars as pl
import numpy
import warnings
import os
from tqdm import tqdm
import numpy as np
tqdm.pandas()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class LGBM_FeatureEngineer(FeatureEngineer):
    def __init__(self, Data):
        super().__init__()
        self.Data = Data
        print(f"Data Passed =>\n{Data}\n")
        
    def Add_Lags(self):
        try:
            DataCopy = self.Data.copy()
            DataCopy['datestampe'] = pd.to_datetime(DataCopy['datestamp'])
            DataCopy = DataCopy.sort_values(by=['provinceid','noc_groupingid','datestamp'], ascending=True)

            lags = [i for i in range(1,13)]
            for l in tqdm(lags, desc='Adding Lags', unit='lag number'): #adding a full 12 month lag 
                DataCopy[f'ER_t_{l}'] = DataCopy.groupby(['provinceid','noc_groupingid'])['employment'].transform(lambda x: x.shift(l))
        
            self.Data = DataCopy
        except Exception as e:
            print(f"Add_Lags() Error => [{e}]")
            pass
    
    def Add_Indicators(self):
        try:
            DataCopy = self.Data.copy()
            DataCopy['datestampe'] = pd.to_datetime(DataCopy['datestamp'])
            DataCopy = DataCopy.sort_values(by=['provinceid','noc_groupingid','datestamp'], ascending=True)

            #Taking Moving Averages and std of lags 
            lags = [i for i in range(1,13)]

            for l in tqdm(lags, desc='Generating Indicators for Lags', unit='Lag Number'):
                DataCopy[f'ER_t_{l}_rollingmean'] =  DataCopy.groupby(['provinceid','noc_groupingid'])[f'ER_t_{l}'].transform(lambda x: x.rolling(window=4, min_periods=4).mean())
                DataCopy[f'ER_t_{l}_rollingstd'] =  DataCopy.groupby(['provinceid','noc_groupingid'])[f'ER_t_{l}'].transform(lambda x: x.rolling(window=8, min_periods=4).std())

            self.Data = DataCopy
        
        except Exception as e:
            print(f'Add_Indicators() Error => [{e}]')
            pass
    
    def Add_Supplementary_Features(self):
        return super().Assign_Directional_Class()
    
    def Assign_Directional_Class(self):
        return super().Assign_Directional_Class()
    
    def SaveSample(self):
        try:
            self.Data.to_csv(f'{BASE_DIR}/LGBM/Data/FeatureEngineered_Data.csv', index=False)
        except Exception as e:
            print(f"Error Saving File=> [{e}]")
            pass

def main():
    
    Data = pd.read_csv(path=f'{BASE_DIR}/LGBM/Data/PreProcessed_Data.csv')

    Engineer = LGBM_FeatureEngineer(Data=Data)
        
    print(f"---Generating Lag Features---\n")
    Engineer.Add_Lags()

    print(f"---Generating Indicator Features---\n")
    Engineer.Add_Indicators()
    
    print(f'---Saving Feature Engineered Data---\n')
    Engineer.SaveSample()


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    
    main()