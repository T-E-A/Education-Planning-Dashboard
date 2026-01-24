from MachineLearningLayer.Utils.Forecast import Forecaster
from MachineLearningLayer.Utils.Splitter import Splitter
from DataTransportationLayer.DataServiceAPI import DataService
import pandas as pd
import warnings
from lightGBM import LGBMRegressor
from mlforecast import MLForecast
from mlforecast.lag_transforms import RollingMean
import os
from tqdm import tqdm
tqdm.pandas()
import json
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HypereparamsPath = f'{BASE_DIR}/LGBM/Data/All_Hyperparams.json'

SAVE_PATH = f"{BASE_DIR}/LGBM/Data/All_Forecasts.parquet"

class LGBM_Forecaster(Forecaster):
    def __init__(self, data, meta_data):
        self.data = data
        self.meta_data = meta_data
        self.forecast_data = None


    def PreProcess_Sets(self):
        try:
            print(f"Pre Processing Sets")
            train = self.meta_data['Sets']['train'].copy()
            validate = self.meta_data['Sets']['validate'].copy()
            test = self.meta_data['Sets']['test'].copy()

            train['ds'] = pd.to_datetime(train['ds'])
            validate['ds'] = pd.to_datetime(validate['ds'])
            test['ds'] = pd.to_datetime(test['ds'])

            train = train[train['year']>=2002]
            
            train_reduced = train[self.needed + self.cate + self.exog]
            validate_reduced = validate[self.needed + self.cate + self.exog]
            test_reduced = test[self.needed + self.cate + self.exog]

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
            
            lgbm_regression_model = LGBMRegressor(
                **params,
                objective='reg:squarederror'
            )
            
            lgbm_q10_model = LGBMRegressor(
                **params,
                objective='reg:quantileerror',
                alpha=0.10
            )
            
            lgbm_q90_model = LGBMRegressor(
                **params,
                objective='reg:quantileerror',
                alpha=0.90
            )
            
            fsct = MLForecast(
                models=[lgbm_regression_model, lgbm_q10_model, lgbm_q90_model],
                freq='MS',
                lags=[1,2,3,6,12],
                transforms=[
                    RollingMean(window=3, min_periods=1)
                ],
                static_features=[]
            )
        
            stepSize = len(validate) + len(test) // 4
        
            print(f"Training and Testing")
        
            cv_df = fsct.cross_validation(
                df=set,
                h=4,
                n_windows=stepSize,
                static_features=[]
            )
        
            cv_df[['LGBMRegression_Pred','LGBM_Q10','LGBM_Q90']] = cv_df[['LGBM_regression','LGBM_quantile_0.1','LGBM_quantile_0.9']].round(2)
        
            cv_df['year'] = cv_df['ds'].dt.year
        
            set_map = {
                2024: 'Validation',
                2025: 'Test'
            }
        
            cv_df['Set'] = cv_df['year'].map(set_map)
        
            valAndTest = cv_df[cv_df['Set']!='Training']
        
            fsct.fit(df=set, static_features=[])
            futureframe = fsct.make_future_dataframe(h=72)
        
            futureframe['ds'] = pd.to_datetime(futureframe['ds'])
        
            futureframe = Add_Exog(DataCopy=futureframe)
        
            futureforecast = fsct.predict(h=72, Xdf=futureframe)
        
            futureforecast[['LGBMRegression_Pred','LGBM_Q10','LGBM_Q90']] = futureforecast[['LGBM_regression','LGBM_quantile_0.1','LGBM_quantile_0.9']].round(2)
        
            futureforecast['year'] = futureforecast['ds'].dt.year

            futureforecast['Set'] = 'Future'
        
            maxDs = valAndTest['ds'].max()
        
            futureforecast = futureforecast[futureforecast['ds']> maxDs]
            futureforecast = futureforecast.drop_duplicates(subset='ds')
        
            forecast_data = pd.concat([valAndTest, futureforecast], axis=0)
        
            Key = self.meta_data['Key']
        
            forecast_data['Key'] = Key
        
        
            self.forecast_data = forecast_data
        
        except Exception as e:
            print(f"Forecasting Exception -> [{e}]")
            pass
        
    def Save_Forecasts(self):
        return self.forecast_data
    
def Load_Data(path=f'{BASE_DIR}/LGBM/Data/FeatureEngineered_Data.csv'):
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
                ForecastObj = LGBM_Forecaster(data=data, meta_data=meta_data)

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