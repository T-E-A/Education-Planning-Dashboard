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
from prophet import Prophet

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

ouput_file = 'prophet_non_tuned_forecast.parquet'


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
        #getting 4 Years before
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
        df_All_Forecasts = df_All_Forecasts.sort_values(by=['unique_id','ds'], ascending=True)
        df_All_Forecasts = df_All_Forecasts.drop_duplicates(subset=['unique_id','ds','y'],keep='last')

        df_All_Forecasts.to_parquet(output_path, index=False)
        

        return 1
    except Exception as e:
        logger.exception(f"{method} => {str(e)}")
        return 0
# #endregion 


#region [Forecast Generation Function]



def generate_forecasts(df, exog_cols):


    try:

        max_date = df['ds'].max()
        val1_cutoff = max_date - relativedelta(years=12)
        val2_cutoff = max_date - relativedelta(years=8)
        val3_cutoff = max_date - relativedelta(years=4)

        windows = [
            ("Validation 1", val1_cutoff),
            ("Validation 2", val2_cutoff),
            ("Test", val3_cutoff),
        ]

        all_sets = []
        for name, cutoff in windows:    


            train = df[df["ds"] <= cutoff]
            validate = df[df['ds'] > cutoff].drop('y',axis=1)
            validate_full = df[df['ds'] > cutoff]

            model = Prophet(
                )

            model.add_seasonality(
                    name='quarterly',
                    period=3,  # 3 months 
                    fourier_order=10
                )
        
            for col in exog_cols:
                model.add_regressor(col)

            model.fit(train)
        
            forecast = model.predict(validate)
            forecast = forecast.merge(validate_full, on='ds', how='right')

            forecast['set'] = name
            forecast['cutoff'] = cutoff

            all_sets.append(forecast)

        df_All_Validation_Sets_Forecasts = pd.concat(all_sets, axis=0)
        
       
        return df_All_Validation_Sets_Forecasts
    
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
        
        unique_ids = data['unique_id'].unique().tolist()

        all_forecasts = []

        logger.info(f"{method} => Starting Trials")
        for uid in tqdm(unique_ids, desc="Processing Series", unit='Series'):
            print(f"Processing unique_id: {uid}")

            Sample = data[data['unique_id']==uid]
            Sample = Sample.sort_values(by='ds', ascending=True)

            

            if len(Sample) == 0:
                continue

            try:
                
                df_Series_Forecast = generate_forecasts(df=Sample, exog_cols=exog_cols)

                if len(df_Series_Forecast) != 0:
                    all_forecasts.append(df_Series_Forecast)
                    
            except Exception as e:
                continue
        
        logger.info(f'{method} => Trials Complete')

        df_All_Forecasts = pd.concat(all_forecasts, axis=0)

        print(df_All_Forecasts)

        result = save(df_All_Forecasts=df_All_Forecasts)

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