from MachineLearningLayer import DataService 
from MachineLearningLayer.Utils.PreProcessing import PreProcessesor
import pandas as pd
import polars as pl
import warnings
import os
from tqdm import tqdm
tqdm.pandas()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Prophet_PreProcessesor(PreProcessesor):

    def __init__(self):
        super().__init__()
        self.Data = None
        self.ValidGroups = None

        

    def GetData(self):
        Data = DataService.GetAllProvincialNOCHistoricData()

        DataReduced = Data[['provinceid','dguid','datestamp','noc_groupingid','employment']]
        DataReduced['datestamp'] = pd.to_datetime(DataReduced['datestamp'])
        DataReduced['year'] = DataReduced['datestamp'].dt.year

        self.Data = DataReduced


    def ProcessNulls(self):
        DataCopy = self.Data.copy()

        DataCopy = DataCopy.sort_values(by=['provinceid','noc_groupingid', 'datestamp'], ascending=True)

        #Using Linear interpolation to handle nulls that land in the middle: 
        DataCopy['employment'] = DataCopy.groupby(['provinceid','noc_groupingid'])['employment'].transform(lambda x: x.interpolate(method='linear'))

        #Using backwards and forwards fill to fill in null that start at the front or end of the distribution 
        DataCopy['employment'] = DataCopy.groupby(['provinceid','noc_groupingid'])['employment'].transform(lambda x: x.fillna(method='ffill').fillna(method='bfill'))

        self.Data = DataCopy
        
    
    def EvaluateSetSizes(self, trainingYear, validationYear, testYear):
        
        DataCopy = pl.from_pandas(self.Data)

        trainMin = trainingYear['threshold']
        validationMin = validationYear['threshold']
        testMin = testYear['threshold']

        TrainSet = DataCopy.filter(pl.col('year') < validationYear['year'])
        ValSet = DataCopy.filter((pl.col('year') >= validationYear['year']) & (pl.col('year') < testYear['year']))
        TestSet = DataCopy.filter((pl.col('year') >= testYear['year']))

        TrainSet_Count = TrainSet.group_by(['provinceid','noc_groupingid']).agg(
            pl.col('datestamp').n_unique().alias('Train Count')
        ).to_pandas()

        ValSet_Count = ValSet.group_by(['provinceid', 'noc_groupingid']).agg(
            pl.col('datestamp').n_unique().alias('Validate Count')
        ).to_pandas()

        TestSet_Count = TestSet.group_by(['provinceid', 'noc_groupingid']).agg(
            pl.col('datestamp').n_unique().alias('Test Count')
        ).to_pandas()

        All_Counts = TrainSet_Count.merge(ValSet_Count, on=['provinceid','noc_groupingid'])
        All_Counts = All_Counts.merge(TestSet_Count, on=['provinceid', 'noc_groupingid'])

        All_Counts['Valid'] = (All_Counts['Train Count'] >= trainMin) & (All_Counts['Validate Count'] >= validationMin) & (All_Counts['Test Count'] >= testMin)

        All_Counts = All_Counts.sort_values(by=['provinceid','noc_groupingid'], ascending=True)
        self.ValidGroups = All_Counts



    
    def ReduceSampleSize(self):
        All_Counts_Copy = self.ValidGroups.copy()

        All_Counts_Copy = All_Counts_Copy[All_Counts_Copy['Valid']==True]

        self.Data = self.Data.merge(All_Counts_Copy[['provinceid','noc_groupingid']], on=['provinceid','noc_groupingid'], how='inner')

        self.Data['Key'] = self.Data.progress_apply(lambda x: (x['provinceid'], x['noc_groupingid']), axis=1)

    
    def SaveSample(self):
        self.Data.to_csv(f'{BASE_DIR}/XGB/Data/PreProcessed_Data.csv',index=False)
    


if __name__ == '__main__':

    warnings.filterwarnings('ignore')


    Processor = Prophet_PreProcessesor()
    
    print(f"---Retrieving Data---")
    Processor.GetData()
    print(f"Data =>\n{Processor.Data}")
    print(f"Number of Nulls =>\n{Processor.Data['employment'].isna().sum()}")

    print(f"---Processing Nulls---")
    Processor.ProcessNulls()
    print(f"Data =>\n{Processor.Data}")
    print(f"Number of Nulls =>\n{Processor.Data['employment'].isna().sum()}")

    print(f"---Count Sets for Valid Groupings---")
    trainingYear = {
        'year': 2000,
        'threshold': ((2024 - 2000) * 12) - 10
    }

    validationYear = {
        'year': 2024,
        'threshold': 10
    }

    testYear = {
        'year': 2025,
        'threshold': 5,
    }
    
    Processor.EvaluateSetSizes(trainingYear=trainingYear, validationYear=validationYear, testYear=testYear)
    print(f"Counts =>\n{Processor.ValidGroups}")

    print(f"---Reducing Sample Size---\n")
    Processor.ReduceSampleSize()
    print(f"Data =>\n{Processor.Data}")

    print(f'---Saving File---\n')
    Processor.SaveSample()



    

