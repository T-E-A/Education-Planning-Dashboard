# Abira Esther Demello

from MachineLearningLayer.Utils.Forecast import Forecaster
from MachineLearningLayer.Utils.Splitter import Splitter
from DataTransportationLayer.DataServiceAPI import DataService
import pandas as pd
import warnings
from neuralprophet import NeuralProphet, set_log_level
import os
from tqdm import tqdm
import json
import numpy as np

tqdm.pandas()
set_log_level("ERROR")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HYPERPARAMS_PATH = f'{BASE_DIR}/Neural_Prophet/Data/All_Hyperparams.json'
SAVE_PATH = f"{BASE_DIR}/Neural_Prophet/Data/All_Forecasts.parquet"


class Neural_Prophet_Forecaster(Forecaster):
    def __init__(self, data, meta_data):
        self.data = data
        self.meta_data = meta_data
        self.forecast_data = None

    def Generate_Forecasts(self):
        try:
            train = self.meta_data['Sets']['train'][['ds', 'y']].copy()
            validate = self.meta_data['Sets']['validate'].copy()
            test = self.meta_data['Sets']['test'].copy()

            params = self.meta_data['Hyperparams']

            # Build model with tuned hyperparameters
            model = NeuralProphet(
                n_changepoints=params.get("n_changepoints", 10),
                changepoints_range=params.get("changepoints_range", 0.8),
                n_lags=params.get("n_lags", 0),
                yearly_seasonality=params.get("yearly_seasonality", True),
                weekly_seasonality=params.get("weekly_seasonality", False),
                daily_seasonality=params.get("daily_seasonality", False),
                seasonality_mode=params.get("seasonality_mode", "additive"),
                learning_rate=params.get("learning_rate", 0.01),
                epochs=params.get("epochs", 100),
                batch_size=params.get("batch_size", 64),
                loss_func=params.get("loss_func", "MSE"),
            )

            # Fit on training data
            model.fit(train, freq="MS")

            # Validation forecast
            val_future = model.make_future_dataframe(train, periods=len(validate))
            val_forecast = model.predict(val_future)
            val_forecast = val_forecast[val_forecast['ds'] > train['ds'].max()][['ds', 'yhat1']].copy()
            val_forecast = val_forecast.rename(columns={'yhat1': 'yhat'})
            val_forecast = val_forecast.merge(validate[['ds', 'y', 'provinceid', 'noc_groupingid', 'dguid']], on='ds')
            val_forecast['Set'] = 'Validation'

            # Test forecast (extend from train + validate)
            train_val = pd.concat([train, validate[['ds', 'y']]], ignore_index=True)
            model_test = NeuralProphet(
                n_changepoints=params.get("n_changepoints", 10),
                changepoints_range=params.get("changepoints_range", 0.8),
                n_lags=params.get("n_lags", 0),
                yearly_seasonality=params.get("yearly_seasonality", True),
                weekly_seasonality=params.get("weekly_seasonality", False),
                daily_seasonality=params.get("daily_seasonality", False),
                seasonality_mode=params.get("seasonality_mode", "additive"),
                learning_rate=params.get("learning_rate", 0.01),
                epochs=params.get("epochs", 100),
                batch_size=params.get("batch_size", 64),
                loss_func=params.get("loss_func", "MSE"),
            )
            model_test.fit(train_val, freq="MS")

            test_future = model_test.make_future_dataframe(train_val, periods=len(test))
            test_forecast = model_test.predict(test_future)
            test_forecast = test_forecast[test_forecast['ds'] > train_val['ds'].max()][['ds', 'yhat1']].copy()
            test_forecast = test_forecast.rename(columns={'yhat1': 'yhat'})
            test_forecast = test_forecast.merge(test[['ds', 'y', 'provinceid', 'noc_groupingid', 'dguid']], on='ds')
            test_forecast['Set'] = 'Test'

            # Future forecast (72 months ahead)
            max_ds = test['ds'].max()
            full_data = pd.concat([train, validate[['ds', 'y']], test[['ds', 'y']]], ignore_index=True)

            model_future = NeuralProphet(
                n_changepoints=params.get("n_changepoints", 10),
                changepoints_range=params.get("changepoints_range", 0.8),
                n_lags=params.get("n_lags", 0),
                yearly_seasonality=params.get("yearly_seasonality", True),
                weekly_seasonality=params.get("weekly_seasonality", False),
                daily_seasonality=params.get("daily_seasonality", False),
                seasonality_mode=params.get("seasonality_mode", "additive"),
                learning_rate=params.get("learning_rate", 0.01),
                epochs=params.get("epochs", 100),
                batch_size=params.get("batch_size", 64),
                loss_func=params.get("loss_func", "MSE"),
            )
            model_future.fit(full_data, freq="MS")

            future_df = model_future.make_future_dataframe(full_data, periods=72)
            future_forecast = model_future.predict(future_df)
            future_forecast = future_forecast[future_forecast['ds'] > max_ds][['ds', 'yhat1']].copy()
            future_forecast = future_forecast.rename(columns={'yhat1': 'yhat'})
            future_forecast['y'] = np.nan
            future_forecast['provinceid'] = validate['provinceid'].iloc[0]
            future_forecast['noc_groupingid'] = validate['noc_groupingid'].iloc[0]
            future_forecast['dguid'] = validate['dguid'].iloc[0]
            future_forecast['Set'] = 'Future'

            # Add confidence intervals (approximate using historical std)
            hist_std = full_data['y'].std()
            for df in [val_forecast, test_forecast, future_forecast]:
                df['yhat_lower'] = df['yhat'] - 1.96 * hist_std * 0.1
                df['yhat_upper'] = df['yhat'] + 1.96 * hist_std * 0.1

            # Combine all forecasts
            forecast_data = pd.concat([val_forecast, test_forecast, future_forecast], axis=0)
            forecast_data['ID'] = self.meta_data['ID']
            forecast_data['year'] = forecast_data['ds'].dt.year

            self.forecast_data = forecast_data

        except Exception as e:
            print(f"Generate_Forecasts error for {self.meta_data['ID']}: {e}")

    def Save_Forecasts(self):
        return self.forecast_data


def Load_Data(path=f'{BASE_DIR}/Neural_Prophet/Data/Neural_PreProcessed_Data.csv'):
    df = pd.read_csv(path)
    df['ds'] = pd.to_datetime(df['ds'])
    ids = df['ID'].unique().tolist()
    return df, ids


def Load_Hyperparams(path=HYPERPARAMS_PATH):
    with open(path, 'r') as f:
        return json.load(f)


def Generate_Sets(df):
    Set_Year_Markers = {
        'validateStart': 2024,
        'testStart': 2025
    }
    splitter = Splitter(Data=df, Set_Year_Markers=Set_Year_Markers)
    return splitter.Generate_Sets()


def Generate_All_Forecasts(df, Hyperparams):
    try:
        ids = list(Hyperparams.keys())
        All_Forecasts = []

        for series_id in tqdm(ids, desc='Generating forecasts', unit='series'):
            print(f"\n# Processing {series_id} #")

            data = df[df['ID'] == series_id].copy()
            data = data.sort_values(by='ds', ascending=True)

            All_Sets = Generate_Sets(df=data)
            params = Hyperparams[series_id]

            meta_data = {
                'ID': series_id,
                'Sets': All_Sets,
                'Hyperparams': params
            }

            forecaster = Neural_Prophet_Forecaster(data=data, meta_data=meta_data)
            forecaster.Generate_Forecasts()

            forecast_data = forecaster.Save_Forecasts()
            if forecast_data is not None:
                All_Forecasts.append(forecast_data)

        # Combine all forecasts
        df_All_Forecasts = pd.concat(All_Forecasts, axis=0).reset_index(drop=True)

        # Prepare for database
        df_All_Forecasts_DB = df_All_Forecasts.rename(columns={
            'ds': 'datestamp',
            'provinceid': 'provinceid',
            'dguid': 'dguid',
            'noc_groupingid': 'noc_groupingid',
            'y': 'y',
            'yhat_lower': 'yhat_lower',
            'yhat': 'yhat',
            'yhat_upper': 'yhat_upper',
            'Set': 'set'
        })

        df_All_Forecasts_DB['datestamp'] = pd.to_datetime(df_All_Forecasts_DB['datestamp']).dt.strftime('%Y-%m-%dT%H:%M:%S')
        df_All_Forecasts_DB['entryid'] = range(1, len(df_All_Forecasts_DB) + 1)
        df_All_Forecasts_DB = df_All_Forecasts_DB.drop(columns=['ID', 'year'], errors='ignore')
        df_All_Forecasts_DB.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

        # Post to cache (optional - uncomment if API is running)
        # records = df_All_Forecasts_DB.to_dict(orient="records")
        # response = DataService.Post_Prediction_Cache(payload=records)
        # print(f"Post Response => {response}")

        # Save to parquet
        df_All_Forecasts.to_parquet(SAVE_PATH, index=False)
        print(f"\n--- Forecasts saved to {SAVE_PATH} ---")

        print(df_All_Forecasts[['ID', 'ds', 'y', 'yhat']].head(20))

    except Exception as e:
        print(f"Generate_All_Forecasts error: {e}")


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    print("--- Loading Hyperparams ---\n")
    Hyperparams = Load_Hyperparams()

    print("--- Loading Data ---\n")
    df, _ = Load_Data()

    print(f"--- Generating Forecasts for {len(Hyperparams)} series ---\n")
    Generate_All_Forecasts(df=df, Hyperparams=Hyperparams)
