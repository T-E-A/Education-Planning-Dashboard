import pandas as pd 
import json 
from statsforecast import StatsForecast
from statsforecast.models import (

    SeasonalNaive, MSTL, 
    SeasonalExponentialSmoothing,
    AutoARIMA
    )
import os
import logging
import inspect
import sys
from tqdm import tqdm


#region [Setting Paths and Logger]

log_path = f'Logs'

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

output_folder = 'generated_cross_validation'
os.makedirs(output_folder, exist_ok=True)

ouput_file = 'cross_validated_data.parquet'
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

#endregion

print(df)
print(columns_dict)

#region [Preparing Data]
def Prepare_Data():
    method = inspect.currentframe().f_code.co_name
    try:
        
        logger.info(f"{method}() Called")

        Id = columns_dict.get('Id',["unique_id"])
        Datestamp = columns_dict.get('Datestamp',["datestamp"])
        Target = columns_dict.get('Target',['y'])
        #No Exog Columns for now

        data = df[Id+Datestamp+Target]
        data = data.rename(columns={'datestamp':'ds'})
        data['ds'] = pd.to_datetime(data['ds'])
        data = data.sort_values(by=['unique_id','ds'], ascending=True)

        logger.info(f"{method}() Complete")

        return data

    except Exception as e:
        logger.exception(f"{method} => {str(e)}")
        return pd.DataFrame()
#endregion

#region [Forecast Generation]

def generate_cross_validation(data:pd.DataFrame, sf):
    method = inspect.currentframe().f_code.co_name
    try:
        logger.info(f"{method}() Called")

        cv_df = sf.cross_validation(
            df=data,
            h=48,          
            step_size=48,  
            n_windows=2
        )
        logger.info(f"{method}() Complete")

        return cv_df
    except Exception as e:
        logger.exception(f"{method} => {str(e)}")
        return pd.DataFrame()

    

def combine(dfs:list):
    method = inspect.currentframe().f_code.co_name
    try:
        logger.info(f"{method}() Called")

        df_Final = pd.concat(dfs, axis=0)
        df_Final = df_Final.sort_values(by=['unique_id','ds'], ascending=True)

        logger.info(f"{method}() Complete")

        return df_Final
    except Exception as e:
        logger.exception(f"{method} => {str(e)}")
        return pd.DataFrame()
#endregion

#region [Saving]

def save(df_Final:pd.DataFrame):
    method = inspect.currentframe().f_code.co_name
    try:
        logger.info(f"{method}() Called")

        df_Final.to_parquet(output_path, index=False)
        
        logger.info(f"{method}() Complete")

        return 1
    except Exception as e:
        logger.exception(f"{method} => {str(e)}")
        return 0
#endregion 


#region [Main Function]
def main():
    method = inspect.currentframe().f_code.co_name
    try:
        logger.info(f"{method}() Called")

        data = Prepare_Data()

        unique_ids = data['unique_id'].unique().tolist()

        if len(data) == 0:
            logger.error(f'{method} => Prepared data is empty')
            exit()
        season_length=12
        models=[ 
            MSTL(season_length=[3,6,12,24,48]),
            SeasonalNaive(season_length=season_length),
            SeasonalExponentialSmoothing(alpha=0.9, season_length=season_length),
            AutoARIMA(season_length=season_length),
        ]

        sf = StatsForecast(
            models=models,
            freq="MS",
            n_jobs=-1
        )
        
        cv_df_list = []
        for uid in tqdm(unique_ids, desc='Processing Unique Ids', unit='Series'):
            
            Sample = data[data['unique_id']==uid]
        
            cv_df = generate_cross_validation(data=Sample, sf=sf)
            if len(cv_df) == 0:
                logger.error(f'{method} => cv_df is empty for {uid}')
                exit()

            cv_df_list.append(cv_df)
        
        logger.info(f'{method} => CV Loop Complete.')

        df_Final = combine(dfs=cv_df_list)
        print(df_Final)
        result = save(df_Final=df_Final)

        if result:
            logger.info(f"{method}() Complete => data saved in {output_path}")
            print(f"Final Result =>\n{df_Final}")
        else:
            logger.error(f'{method} => Unable to save file')

        exit()
    except Exception as e:
        logger.exception(f"{method} => {str(e)}")
        exit()
#endregion


if __name__ == '__main__':

    main()