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

class XGB_FeatureEngineer(FeatureEngineer):
    def __init__(self, Data):
        super().__init__()
        self.Data = Data
        print(f"Data Passed =>\n{Data}\n")
        
    
    def Add_Lags(self):
        try:
            DataCopy = self.Data.copy()
            DataCopy['datestamp'] = pd.to_datetime(DataCopy['datestamp'])
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
            DataCopy['datestamp'] = pd.to_datetime(DataCopy['datestamp'])
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

    def Add_Date_Features(self):
        try:
            DataCopy = self.Data.copy()
            DataCopy['datestamp'] = pd.to_datetime(DataCopy['datestamp'])

            #Getting Numeric Representation of Date Stamp 
            DataCopy['dayofyear'] = DataCopy['datestamp'].dt.dayofyear      
            DataCopy['month'] = DataCopy['datestamp'].dt.month        
            DataCopy['quarter'] = DataCopy['datestamp'].dt.quarter         
            DataCopy['week'] = DataCopy['datestamp'].dt.isocalendar().week  

            #Transforming Date Features to Cyclical Representation 
            # Day of year - 365 days 
            DataCopy['dayofyear_sin'] = np.sin(2 * np.pi * DataCopy['dayofyear'] / 365)
            DataCopy['dayofyear_cos'] = np.cos(2 * np.pi * DataCopy['dayofyear'] / 365)

            # Month - 12 Months 
            DataCopy['month_sin'] = np.sin(2 * np.pi * DataCopy['month'] / 12)
            DataCopy['month_cos'] = np.cos(2 * np.pi * DataCopy['month'] / 12)

            # Quarter - 4 Quarters
            DataCopy['quarter_sin'] = np.sin(2 * np.pi * DataCopy['quarter'] / 4)
            DataCopy['quarter_cos'] = np.cos(2 * np.pi * DataCopy['quarter'] / 4)

            # Calendar Week - 52 
            DataCopy['week_sin'] = np.sin(2 * np.pi * DataCopy['week'] / 52)
            DataCopy['week_cos'] = np.cos(2 * np.pi * DataCopy['week'] / 52)

            self.Data = DataCopy
        except Exception as e:
            print(f'Add_Date_Features() Error => [{e}]')
    
    def SaveSample(self):
        try:
            self.Data.to_csv(f'{BASE_DIR}/XGB/Data/FeatureEngineered_Data.csv',index=False)
        except Exception as e:
            print(f"Error Saving File => [{e}]")

def main():

    Data = pd.read_csv(f'{BASE_DIR}/XGB/Data/PreProcessed_Data.csv')

    Engineer = XGB_FeatureEngineer(Data=Data)

    print(f"---Generating Lag Features---\n")
    Engineer.Add_Lags()

    print(f"---Generating Indicator Features---\n")
    Engineer.Add_Indicators()

    print(f"---Generating Exogenous Data based Features---\n")
    Engineer.Add_Date_Features()

    print(f'---Saving Feature Engineered Data---\n')
    Engineer.SaveSample()


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    main()



    

        