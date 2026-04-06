# Abira Esther Demello

from MachineLearningLayer import DataService
from MachineLearningLayer.Utils.PreProcessing import PreProcessesor

import pandas as pd
import polars as pl
import warnings
import os
from tqdm import tqdm

tqdm.pandas()

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Neural_Prophet_PreProcessesor(PreProcessesor):
    """
    Goal:
    Prepare employment time-series data so NeuralProphet can train/forecast.

    NeuralProphet expects (at minimum):
      - ds : datetime column
      - y  : numeric target column
    If you train many series together (one per province+NOC), it also expects:
      - ID : series identifier (string)
    """

    def __init__(self):
        super().__init__()
        self.Data = None
        self.ValidGroups = None

    # STEP 1) Get raw data from your DataService and keep only what we need

    def GetData(self):
        # Pull full dataset from your existing service method
        data = DataService.GetAllProvincialNOCHistoricData()

        # Keep only the columns you actually use in forecasting
        data_reduced = data[['provinceid', 'dguid', 'datestamp', 'noc_groupingid', 'employment']].copy()

        # Make sure datestamp is datetime (critical for time-series)
        data_reduced['datestamp'] = pd.to_datetime(data_reduced['datestamp'])

        # Add year column because you split train/val/test using years
        data_reduced['year'] = data_reduced['datestamp'].dt.year

        self.Data = data_reduced

    
    # STEP 2) Fill nulls (missing employment values) safely per series
    
    def ProcessNulls(self):
        data_copy = self.Data.copy()

        # Sort so interpolation works correctly through time
        data_copy = data_copy.sort_values(by=['provinceid', 'noc_groupingid', 'datestamp'], ascending=True)

        #  Interpolate nulls in the *middle* of each series
        data_copy['employment'] = (
            data_copy
            .groupby(['provinceid', 'noc_groupingid'])['employment']
            .transform(lambda x: x.interpolate(method='linear'))
        )

        # Fill nulls at the *start/end* (interpolation can't fill edges)
        data_copy['employment'] = (
            data_copy
            .groupby(['provinceid', 'noc_groupingid'])['employment']
            .transform(lambda x: x.ffill().bfill())
        )

        self.Data = data_copy

    
    # STEP 3) Check which (province, NOC) groups have enough data for train/val/test splits

    def EvaluateSetSizes(self, trainingYear, validationYear, testYear):
        """
        
        trainingYear example:
          {'year': 2000, 'threshold': something}
        validationYear example:
          {'year': 2024, 'threshold': 10}
        testYear example:
          {'year': 2025, 'threshold': 5}
        """

        data_pl = pl.from_pandas(self.Data)

        train_min = trainingYear['threshold']
        val_min = validationYear['threshold']
        test_min = testYear['threshold']

        # Split logic 

        train_set = data_pl.filter(pl.col('year') < validationYear['year'])
        val_set = data_pl.filter((pl.col('year') >= validationYear['year']) & (pl.col('year') < testYear['year']))
        test_set = data_pl.filter(pl.col('year') >= testYear['year'])

        # Count unique months (datestamp) per group
        train_counts = (
            train_set.group_by(['provinceid', 'noc_groupingid'])
            .agg(pl.col('datestamp').n_unique().alias('Train Count'))
            .to_pandas()
        )

        val_counts = (
            val_set.group_by(['provinceid', 'noc_groupingid'])
            .agg(pl.col('datestamp').n_unique().alias('Validate Count'))
            .to_pandas()
        )

        test_counts = (
            test_set.group_by(['provinceid', 'noc_groupingid'])
            .agg(pl.col('datestamp').n_unique().alias('Test Count'))
            .to_pandas()
        )

        # Merge counts into one table
        all_counts = train_counts.merge(val_counts, on=['provinceid', 'noc_groupingid'])
        all_counts = all_counts.merge(test_counts, on=['provinceid', 'noc_groupingid'])

        # Mark which groups are valid
        all_counts['Valid'] = (
            (all_counts['Train Count'] >= train_min) &
            (all_counts['Validate Count'] >= val_min) &
            (all_counts['Test Count'] >= test_min)
        )

        all_counts = all_counts.sort_values(by=['provinceid', 'noc_groupingid'], ascending=True)
        self.ValidGroups = all_counts

    
    # STEP 4) Reduce dataset to only the valid groups
    
    def ReduceSampleSize(self):
        valid = self.ValidGroups.copy()
        valid = valid[valid['Valid'] == True]

        # Inner join keeps ONLY the good (province, NOC) combos
        self.Data = self.Data.merge(
            valid[['provinceid', 'noc_groupingid']],
            on=['provinceid', 'noc_groupingid'],
            how='inner'
        )

    # STEP 5) Convert into NeuralProphet-friendly format: ds, y, ID
    
    def ConvertToNeuralProphetFormat(self):
        """
        NeuralProphet expects:
          - ds (datetime)
          - y  (numeric)
        For many series in one model, add:
          - ID (string that identifies each series)
        """

        data_copy = self.Data.copy()

        # Create a stable string ID per (province, NOC)
        # Example: "P24_N41"
        data_copy['ID'] = data_copy.apply(
            lambda row: f"P{row['provinceid']}_N{row['noc_groupingid']}",
            axis=1
        )

        # Rename columns to NeuralProphet convention
        data_copy = data_copy.rename(columns={
            'datestamp': 'ds',
            'employment': 'y'
        })

        # Keep useful metadata too (helps debugging + mapping outputs later)
        # NeuralProphet can ignore extra columns, but it's safer to keep it minimal.
        data_copy = data_copy[['ID', 'provinceid', 'noc_groupingid', 'dguid', 'ds', 'y', 'year']]

        # Sort so every series is in time order (important!)
        data_copy = data_copy.sort_values(by=['ID', 'ds'], ascending=True)

        self.Data = data_copy

   
    # STEP 6) Save output for your training script to load
    def SaveSample(self):
        output_dir = f"{BASE_DIR}/Neural_Prophet/Data"
        os.makedirs(output_dir, exist_ok=True)

        self.Data.to_csv(f"{output_dir}/Neural_PreProcessed_Data.csv", index=False)



# Running the pipeline end-to-end 

if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    processor = Neural_Prophet_PreProcessesor()

    logger.info("STEP 1: Retrieving raw employment data")
    processor.GetData()
    logger.info(f"Rows retrieved: {len(processor.Data)}")
    logger.info(f"Null employment values: {processor.Data['employment'].isna().sum()}")

    logger.info("STEP 2: Processing null values")
    processor.ProcessNulls()
    logger.info(f"Null employment values after processing: {processor.Data['employment'].isna().sum()}")

    print(f"\n---Count Sets for Valid Groupings---")
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
        'threshold': 5
    }

    processor.EvaluateSetSizes(trainingYear=trainingYear, validationYear=validationYear, testYear=testYear)
    print(processor.ValidGroups.head(10))

    print(f"\n---Reducing Sample Size---")
    processor.ReduceSampleSize()
    print(processor.Data.head())

    logger.info("STEP 5: Converting data to NeuralProphet format (ds, y, ID)")
    processor.ConvertToNeuralProphetFormat()
    logger.info(f"Columns after conversion: {processor.Data.columns.tolist()}")

    print(f"\n---Saving File---")
    processor.SaveSample()
    print(f"Saved to: {BASE_DIR}/Neural_Prophet/Data/PreProcessed_Data.csv")