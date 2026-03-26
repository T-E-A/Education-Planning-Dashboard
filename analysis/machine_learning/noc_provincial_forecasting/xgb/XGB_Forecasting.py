from MachineLearningLayer.Utils.Forecast import Forecaster
from MachineLearningLayer.Utils.Splitter import Splitter
import pandas as pd
import warnings
from xgboost import XGBRegressor
from mlforecast import MLForecast
from mlforecast.lag_transforms import RollingMean
import os
from tqdm import tqdm
tqdm.pandas()
import json
import numpy as np


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HypereparamsPath = f'{BASE_DIR}/XGB/Data/All_Hyperparams.json'

SAVE_PATH = f"{BASE_DIR}/XGB/Data/All_Forecasts.parquet"

def Add_Exog(DataCopy):
            
        DataCopy['dayofyear'] = DataCopy['ds'].dt.dayofyear      
        DataCopy['month'] = DataCopy['ds'].dt.month        
        DataCopy['quarter'] = DataCopy['ds'].dt.quarter         
        DataCopy['week'] = DataCopy['ds'].dt.isocalendar().week  

            
        DataCopy['dayofyear_sin'] = np.sin(2 * np.pi * DataCopy['dayofyear'] / 365)
        DataCopy['dayofyear_cos'] = np.cos(2 * np.pi * DataCopy['dayofyear'] / 365)

             
        DataCopy['month_sin'] = np.sin(2 * np.pi * DataCopy['month'] / 12)
        DataCopy['month_cos'] = np.cos(2 * np.pi * DataCopy['month'] / 12)

            
        DataCopy['quarter_sin'] = np.sin(2 * np.pi * DataCopy['quarter'] / 4)
        DataCopy['quarter_cos'] = np.cos(2 * np.pi * DataCopy['quarter'] / 4)

            
        DataCopy['week_sin'] = np.sin(2 * np.pi * DataCopy['week'] / 52)
        DataCopy['week_cos'] = np.cos(2 * np.pi * DataCopy['week'] / 52)
        
        return DataCopy

class XGB_Forecaster(Forecaster):
    def __init__(self, data, meta_data):
        self.data = data
        self.meta_data = meta_data
        self.forecast_data = None
        self.exog  = [
                'dayofyear_sin',
                'dayofyear_cos',
                'month_sin',
                'month_cos',
                'quarter_sin',
                'quarter_cos',
                'week_sin',
                'week_cos'
            ]

        self.cate = [
            'dayofyear',
            'month',
            'quarter',
            'week'
        ]

        self.needed = [
            'unique_id',
            'ds',
            'y'
        ]
    
    def PreProcess_Sets(self):
        try:
            print(f"Pre Processing Sets")
            train = self.meta_data['Sets']['train'].copy()
            validate = self.meta_data['Sets']['validate'].copy()
            test = self.meta_data['Sets']['test'].copy()

            # print(f"Test =>\n{test}")

            # print(f"Copied")

            train['ds'] = pd.to_datetime(train['ds'])
            validate['ds'] = pd.to_datetime(validate['ds'])
            test['ds'] = pd.to_datetime(test['ds'])

            # print(f"DS Converted")

            train = train[train['year']>=2002]

            # print(f"Train Reduced")

            
            
            train_reduced = train[self.needed + self.cate + self.exog]
            validate_reduced = validate[self.needed + self.cate + self.exog]
            test_reduced = test[self.needed + self.cate + self.exog]

            # print(f'Training =>\n{train_reduced}\n')
            # print(f'Validation =>\n{validate_reduced}\n')
            # print(f'Test =>\n{test_reduced}\n')

            

            self.meta_data['Sets']['train'] = train_reduced
            self.meta_data['Sets']['validate'] = validate_reduced
            self.meta_data['Sets']['test'] = test_reduced

            
            

        except:
            pass
    
 
    def Generate_Forecasts(self):
        try:
            
            train = self.meta_data['Sets']['train']
            validate = self.meta_data['Sets']['validate']
            test = self.meta_data['Sets']['test']

            train = self.meta_data['Sets']['train']
            validate = self.meta_data['Sets']['validate']


            set = pd.concat([train, validate, test], axis=0)

            set = set.sort_values(by='ds', ascending=True)

            set = set.dropna()

            params = self.meta_data['Hyperparams']

            regression_model = XGBRegressor(
                    **params,
                    objective='reg:squarederror'
                )

            q10_model = XGBRegressor(
                    **params,
                    objective='reg:quantileerror',
                    quantile_alpha=0.10
                )

            q90_model = XGBRegressor(
                    **params,
                    objective='reg:quantileerror',
                    quantile_alpha=0.90
                )
            
            fsct = MLForecast(
                    models=[regression_model, q10_model, q90_model],
                    freq='MS',
                    lags=[1,2,3,4,10,11,12],
                    lag_transforms={
                        1:[RollingMean(window_size=4, min_samples=4)],
                        2:[RollingMean(window_size=4, min_samples=4)],
                        3:[RollingMean(window_size=4, min_samples=4)],
                        4:[RollingMean(window_size=4, min_samples=4)],
                        10:[RollingMean(window_size=4, min_samples=4)],
                        11:[RollingMean(window_size=4, min_samples=4)],
                        12:[RollingMean(window_size=4, min_samples=4)],
                    }
                )

            

            stepSize = (len(validate) + len(test)) // 4

            print(f"Training and Testing")
            cv_df = fsct.cross_validation(
                    df=set,
                    h=4,
                    n_windows=stepSize,
                    static_features=[]
            )

            
            cv_df[['XGBRegressor','XGBRegressor2','XGBRegressor3']] = cv_df[['XGBRegressor','XGBRegressor2','XGBRegressor3']].round(2)

            cv_df = cv_df.rename(columns={'XGBRegressor':'yhat', 'XGBRegressor2':'yhat_lower', 'XGBRegressor3':'yhat_upper'})

            cv_df['year'] = cv_df['ds'].dt.year

            set_map = {
                2024: 'Validation',
                2025: 'Test'
            }

            cv_df['Set'] = cv_df['year'].map(set_map)
            

            valAndTest = cv_df[cv_df['Set']!='Training']
            # print(f"CV Output =>\n{valAndTest}")

            fsct.fit(df=set, static_features=[])
            futureframe = fsct.make_future_dataframe(h=72)

            futureframe['ds'] = pd.to_datetime(futureframe['ds'])

            futureframe = Add_Exog(DataCopy=futureframe)

            futureforecast = fsct.predict(
                h=72,
                X_df=futureframe
            )


            futureforecast[['XGBRegressor','XGBRegressor2','XGBRegressor3']] = futureforecast[['XGBRegressor','XGBRegressor2','XGBRegressor3']].round(2)

            futureforecast = futureforecast.rename(columns={'XGBRegressor':'yhat', 'XGBRegressor2':'yhat_lower', 'XGBRegressor3':'yhat_upper'})

            futureforecast['year'] = futureforecast['ds'].dt.year

            futureforecast['Set'] = 'Future'

            # print(f"Future Coutcome=>\n{futureforecast}")

            maxDs = valAndTest['ds'].max()

            futureforecast = futureforecast[futureforecast['ds']> maxDs]
            futureforecast = futureforecast.drop_duplicates(subset='ds')

            forecast_data = pd.concat([valAndTest, futureforecast], axis=0)

            Key = self.meta_data['Key']
            
            forecast_data['Key'] = Key


            self.forecast_data = forecast_data


        except Exception as e:
            print(f"{e}")
            pass
    
    def Save_Forecasts(self):
        return self.forecast_data


def Load_Data(path=f'{BASE_DIR}/XGB/Data/FeatureEngineered_Data.csv'):
    df = pd.read_csv(path)
    
    df['datestamp'] = pd.to_datetime(df['datestamp'])
    df = df.rename(columns={'provinceid':'unique_id','datestamp':'ds','employment':'y'})
    df['provinceid'] = df['unique_id']

    keys = df['Key'].unique().tolist()

    return df, keys

def Generate_Sets(df):
    Set_Year_Markers = {
        'validateStart': 2024,
        'testStart': 2025
    }

    SplittObj = Splitter(Data=df, Set_Year_Markers=Set_Year_Markers)

    All_Sets = SplittObj.Generate_Sets()

    print(f"Sets-Generated")

    return All_Sets

def Load_Hyperparams(path=HypereparamsPath):
    with open(path, 'r') as f:
        Hyperparams = json.load(f)
    
    return Hyperparams


def Generate_All_Forecasts(df , Hyperparams):
    try:

        keys = list(Hyperparams.keys())
        All_Forecasts = []
        for key in tqdm(keys, desc='Processing Keys', unit='(provinceid, noc_groupingid)'):
            print(f"#Processing {key}#\n")

            

            data = df[df['Key']==key]
            data = data.sort_values(by='ds', ascending=True)

            # print(data)

            province_id = data['provinceid'].unique().tolist()[0]
            noc_groupingid = data['noc_groupingid'].unique().tolist()[0]
            dguid = data['dguid'].unique().tolist()[0]

            All_Sets = Generate_Sets(df=data)

            params = Hyperparams[key]


            meta_data = {
                'Key': key,
                'Sets': All_Sets,
                'Hyperparams': params
            }

            try:
                ForecastObj = XGB_Forecaster(data=data, meta_data=meta_data)

                ForecastObj.PreProcess_Sets()
            
                ForecastObj.Generate_Forecasts()

                forecast_data = ForecastObj.Save_Forecasts()

                forecast_data['provinceid'] = province_id
                forecast_data['dguid'] = dguid
                forecast_data['noc_groupingid'] = noc_groupingid

                print(forecast_data[['Key','provinceid','noc_groupingid','ds','y','yhat_lower','yhat','yhat_upper']])

                All_Forecasts.append(forecast_data)
            except:
                continue

        df_All_Forecasts = pd.concat(All_Forecasts, axis=0)

        
        df_All_Forecasts = df_All_Forecasts.reset_index(drop=True)

        df_All_Forecasts_DB = df_All_Forecasts.rename(columns={
    'ds': 'datestamp',
    'Set': 'set'
        })


        
        df_All_Forecasts_DB['entryid'] = range(1, len(df_All_Forecasts_DB) + 1)


        df_All_Forecasts_DB = df_All_Forecasts_DB.drop(columns=['year'])

        

        df_All_Forecasts_DB.to_parquet(SAVE_PATH, index=False)

        


        print(df_All_Forecasts_DB[['Key','provinceid','noc_groupingid','ds','y','yhat_lower','yhat','yhat_upper']])

        print(f"---Forecasts Saved---")



    except Exception as e:
        print(f"Exceptions => [{e}]")
        pass

if __name__ == '__main__':

    print(f"---Loading Hyperparams---\n")
    Hyperparams = Load_Hyperparams()

    print(f"---Loading Data---\n")
    df, _ = Load_Data()

    print(f"---Generating Forecasts---\n")
    Generate_All_Forecasts(df=df, Hyperparams=Hyperparams)