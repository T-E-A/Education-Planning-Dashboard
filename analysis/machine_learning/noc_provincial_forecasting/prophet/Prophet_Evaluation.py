from MachineLearningLayer.Utils.Evaluation import Evaluater
from MachineLearningLayer import DataService
import pandas as pd
import polars as pl
import os
import warnings
from ydata_profiling import ProfileReport
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, root_mean_squared_error
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Prophet_Evaluator(Evaluater):
    def __init__(self, forecast_data):
        self.forecast_data = forecast_data
        self.evaluation_data = None


    def Calculate_Regression_Metrics(self):
        try:
            df = self.forecast_data.copy()

            df_Province = DataService.GetProvinceNames()
            df_NOCGroups = DataService.GetNOCGroupingNames()
            
            df = df.merge(df_Province, on='provinceid', how='left')
            df = df.merge(df_NOCGroups, on='noc_groupingid', how='left')

            df_Eval = df.groupby(['provinceid','province_shorthand','noc_groupingid','noc_grouping']).apply(
                lambda df: pd.DataFrame({
                    "r2": [r2_score(df['y'].to_numpy(), df['yhat'].to_numpy())],
                    "euclidean distance": [np.linalg.norm(df['y'].to_numpy() - df['yhat'].to_numpy())],
                    "mae": [mean_absolute_error(df['y'].to_numpy(), df['yhat'].to_numpy())],
                    "rmse": [root_mean_squared_error(df['y'].to_numpy(), df['yhat'].to_numpy())],
                    "mse": [mean_squared_error(df['y'].to_numpy(), df['yhat'].to_numpy())],
                    'Average Actual': [df['y'].mean()],
                    'CV RMSE': [root_mean_squared_error(df['y'].to_numpy(), df['yhat'].to_numpy()) / df['y'].mean()],
                    'CV MAE': [mean_absolute_error(df['y'].to_numpy(), df['yhat'].to_numpy()) / df['y'].mean()],
                    'MAPE': [ (abs(df['y'] - df['yhat']) / df['y']).mean() * 100 ]
            })
            ).reset_index().sort_values(by=['r2'], ascending=False).drop('level_4', axis=1)

            print(f"--Metrics Caluclated-- =>\n{df_Eval.head(10)}")

            self.evaluation_data = df_Eval
        

        except Exception as e:
            print(f"Prophet_Evaluator.Calculate_Regression_Metrics() => {e}")
            pass
    
    def Save_Metrics(self):
        try:
            if self.evaluation_data is not None:
                df = self.evaluation_data.copy()
                
                
                df.to_csv(f'{BASE_DIR}/Prophet/Data/Evaluation_Metrics.csv', index=False)
                print("---Evaluation Metrics CSV File Saved---\n")

                profile = ProfileReport(df, title="Prophet Evaluation Metrics Report", explorative=True)
                profile.to_file(f"{BASE_DIR}/Prophet/Data/Reports/Evaluation_Metrics_Report.html")
                print("---Evaluation Metrics Report Saved---\n")

                
            else:
               pass
        except Exception as e:
            print(f"Prophet_Evaluator.Save_Metrics() => {e}")
            pass

if __name__ == '__main__':

    warnings.filterwarnings('ignore')

    print(f"---Loading Forecast Data---\n")
    df_forecast = pl.scan_parquet(f'{BASE_DIR}/Prophet/Data/All_Forecasts.parquet')

    forecast_data = df_forecast.filter(pl.col('Set').is_in(['Validation','Test'])).collect().to_pandas()

    EvaluatorObj = Prophet_Evaluator(forecast_data=forecast_data)

    print(f"---Calculating Evaluation Metrics---\n")
    EvaluatorObj.Calculate_Regression_Metrics()

    print(f"---Saving Evaluation Metrics---\n")
    EvaluatorObj.Save_Metrics()
