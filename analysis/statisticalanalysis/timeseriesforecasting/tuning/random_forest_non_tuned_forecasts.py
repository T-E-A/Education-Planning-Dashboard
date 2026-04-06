import pandas as pd 
import json 
import os
import logging
import inspect
import sys
from dateutil.relativedelta import relativedelta
from sklearn.metrics import root_mean_squared_error
import numpy as np
from tqdm import tqdm
import optuna
from sklearn.ensemble import RandomForestRegressor
from mlforecast import MLForecast
from mlforecast.lag_transforms import RollingMean

#region [Setting Paths and Logger]
log_path = f'Logs'

print(f"Making Logs")
os.makedirs(log_path, exist_ok=True)

script_name = os.path.splitext(os.path.basename(inspect.getfile(inspect.currentframe())))[0]
log_file = os.path.join(log_path, f"{script_name}.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
)

logger = logging.getLogger(__name__)

logger.info(f"{script_name} - Started")

output_folder = 'forecastsamples'
os.makedirs(output_folder, exist_ok=True)

ouput_file = 'randomforest_non_tuned_forecast.parquet'


output_path = os.path.join(output_folder, ouput_file)



data_path = 'forecasting-data-set.parquet'
columns_json_path = 'forecast_set_columns.json'
#endregion 

#region [Loading Data]
try:
    df = pd.read_parquet(data_path)
except Exception as e:
    logger.exception(f'{str(e)} - Exiting')
    exit

try: 
    with open(columns_json_path, 'r') as f:
        columns_dict = json.load(f)
except Exception as e:
    logger.exception(f"{str(e)} - Exiting")


exog_cols = columns_dict.get('ExogenousFeature',[])
#endregion


# #region [Preparing Data]
def Prepare_Data():
    method = inspect.currentframe().f_code.co_name
    try:
        
        logger.info(f"{method}() Called")

        Id = columns_dict.get('Id',["unique_id"])
        Datestamp = columns_dict.get('Datestamp',["datestamp"])
        Target = columns_dict.get('Target',['y'])
        Exog = columns_dict.get('ExogenousFeature', [''])

        data = df[Id+Datestamp+Target+Exog]
        data = data.rename(columns={'datestamp':'ds'})
        data['ds'] = pd.to_datetime(data['ds'])
        data = data.sort_values(by=['unique_id','ds'], ascending=True)

        maxDate = data['ds'].max()
        #getting 4 Years before, we dont tune on test set
        validationStart = maxDate - relativedelta(years=4)
        trainEnd = validationStart - relativedelta(years=4)

        # data = data[data['ds'] <= validationStart]
        data = data.sort_values(by=['unique_id','ds'], ascending=True)

        print(f"Max date in dataset: {maxDate}")
        print(f"Validation date (4 years before): {validationStart}")
        print(f"Training Date (4 Years before Validation): {trainEnd}")
        print(f"Data shape after cutoff filter: {data.shape}")

        logger.info(f"{method}() Complete")

        return data, validationStart, trainEnd

    except Exception as e:
        logger.exception(f"{method} => {str(e)}")
        return pd.DataFrame(), None, None
# #endregion

# #region [Saving]
def save(df_All_Forecasts):
    method = inspect.currentframe().f_code.co_name
    try:
        logger.info(f"{method}() Called")

        df_All_Forecasts.to_parquet(output_path, index=False)
        

        return 1
    except Exception as e:
        logger.exception(f"{method} => {str(e)}")
        return 0
# #endregion 



#region [Forecast Generation]
def generate_forecasts(df):


    rfModel = RandomForestRegressor()

    try:

        fsct = MLForecast(
                    models=[rfModel],
                    freq='MS',
                    lags=[1,7,13],
                    lag_transforms={
                        1:[RollingMean(window_size=3, min_samples=3), RollingMean(window_size=6, min_samples=6), RollingMean(window_size=12, min_samples=12), RollingMean(window_size=36, min_samples=36), RollingMean(window_size=48, min_samples=48)],
                        7:[RollingMean(window_size=3, min_samples=3), RollingMean(window_size=6, min_samples=6), RollingMean(window_size=12, min_samples=12), RollingMean(window_size=36, min_samples=36), RollingMean(window_size=48, min_samples=48)],
                        13:[RollingMean(window_size=3, min_samples=3), RollingMean(window_size=6, min_samples=6), RollingMean(window_size=12, min_samples=12), RollingMean(window_size=36, min_samples=36), RollingMean(window_size=48, min_samples=48)]

                    }   
                )
        
        #In Built Cross Validation
        cv_df = fsct.cross_validation(
                    df=df,
                    h=48,            # 4 year forecast horizon => 48 Months
                    n_windows=3,      # produce 3 forecasts => 3 Cross Validations 
                    step_size=48,     # move forward 4 years each window => move the training window 4 years later 
                    static_features=[]
        )

        return cv_df
    
    except Exception as e:
        print(f"Tuning Error => {e}")
        return pd.DataFrame()
#endregion 


#region [Main Function]
def main():
    method = inspect.currentframe().f_code.co_name
    try:
        logger.info(f"{method}() Called")

        data, validationStart, trainEnd = Prepare_Data()

        if len(data) == 0:
            logger.error(f'{method} => Prepared data is empty')
            exit()
        
        try:
            
            df_All_Forecasts = generate_forecasts(df=data)

            
                    
        except Exception as e:
            logger.exception(f'{method} => {str(e)}')

        
        logger.info(f'{method} => Trials Complete')

        result = save(df_All_Forecasts=df_All_Forecasts)

        print(df_All_Forecasts)

        if result:
            logger.info(f"{method}() Complete => data saved in {output_path}")
        else:
            logger.error(f'{method} => Unable to save file')

        exit()
    except Exception as e:
        logger.exception(f"{method} => {str(e)}")
        exit()
# #endregion


if __name__ == '__main__':

    main()