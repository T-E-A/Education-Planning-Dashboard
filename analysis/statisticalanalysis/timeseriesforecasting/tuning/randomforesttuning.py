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

output_folder = 'results/randomforest'
os.makedirs(output_folder, exist_ok=True)

ouput_file = 'rf_hyperparams.json'

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
        validationStart = maxDate - relativedelta(years=4*3)
        trainEnd = validationStart - relativedelta(years=4)

        data = data[data['ds'] <= validationStart]
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

def save(results):
    method = inspect.currentframe().f_code.co_name
    try:
        logger.info(f"{method}() Called")

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)

        
        logger.info(f"{method}() Complete")

        return 1
    except Exception as e:
        logger.exception(f"{method} => {str(e)}")
        return 0
# #endregion 


def rf_objective(trial, df):



    params = {
        "n_estimators": trial.suggest_int("n_estimators", 200, 1000),
        "max_depth": trial.suggest_int("max_depth", 4, 20),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
        "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
        "bootstrap": trial.suggest_categorical("bootstrap", [True, False]),
        "n_jobs": -1,
        "random_state": 42
    }

    rfModel = RandomForestRegressor(
        **params
    )

    try:

        fsct = MLForecast(
                    models=[rfModel],
                    freq='MS',
                    lags=[1,7,13],
                    lag_transforms={
                        1:[RollingMean(window_size=3, min_samples=3), RollingMean(window_size=6, min_samples=6), RollingMean(window_size=12, min_samples=12)],

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

        GroupedSeries = cv_df.groupby(['unique_id','cutoff']).apply(
            lambda x: pd.Series({
                'RMSE': root_mean_squared_error(x['y'], x['RandomForestRegressor']),
                'AVG_Y':x['y'].mean()
            })
        ).reset_index()

        GroupedSeries['CV_RMSE'] = GroupedSeries['RMSE']/GroupedSeries['AVG_Y']

        Cuttoff_Avg_CV_RMSE = GroupedSeries.groupby(['cutoff']).apply(
            lambda x: pd.Series(
                {
                    'AVG_CV_RMSE': x['CV_RMSE'].mean()
                }
            )
        ).reset_index()

        Cuttoff_Avg_CV_RMSE['cutoff'] = pd.to_datetime(Cuttoff_Avg_CV_RMSE['cutoff'])
        Cuttoff_Avg_CV_RMSE = Cuttoff_Avg_CV_RMSE.sort_values(by=['cutoff'], ascending=True)

        weights = [0.2, 0.3, 0.5]

        Cuttoff_Avg_CV_RMSE['Weighted_AVG_CV_RMSE'] = Cuttoff_Avg_CV_RMSE['AVG_CV_RMSE'] * weights

        print(Cuttoff_Avg_CV_RMSE)

        return Cuttoff_Avg_CV_RMSE['Weighted_AVG_CV_RMSE'].sum()
      
        
    
    except Exception as e:
        print(f"Tuning Error => {e}")
        return float("inf")


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
            study = optuna.create_study(direction='minimize')

            study.optimize(lambda trial: rf_objective(trial, 
                                                            data), n_trials=30)

            results = {
                    'best_params': study.best_params,
                    'best_rmse': study.best_value
            }
                    
        except Exception as e:
            logger.exception(f'{method} => {str(e)}')

        
        logger.info(f'{method} => Trials Complete')

        result = save(results=results)

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