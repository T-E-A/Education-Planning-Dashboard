from MachineLearningLayer.Utils.Tuning import Tuner
from MachineLearningLayer.Utils.Splitter import Splitter
import pandas as pd
import warnings
import optuna
from xgboost import XGBRegressor
from mlforecast import MLForecast
from mlforecast.lag_transforms import RollingMean
import os
from tqdm import tqdm
tqdm.pandas()
from sklearn.metrics import  root_mean_squared_error, mean_pinball_loss
import json
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_PATH = f"{BASE_DIR}/XGB/Data/All_Hyperparams.json"


def trial_score(trial, r2_weight=0.55, pin_ball_loss=0.45):
    r2 = trial.values[0]
    pbL = trial.values[1]
    return (r2_weight * r2) - (pin_ball_loss * pbL)

def pinball(g, q, col):
    return mean_pinball_loss(g['y'], g[col], alpha=q)

def pinball_vec(y, y_pred, q):
    e = y - y_pred
    return np.mean(np.maximum(q*e, (q-1)*e))


class TunerClass(Tuner):
    def __init__(self, data, meta_data):
        self.data = data
        self.meta_data = meta_data
        self.best_params = None
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
            train = self.meta_data['Sets']['train'].copy()
            validate = self.meta_data['Sets']['validate'].copy()

            train['ds'] = pd.to_datetime(train['ds'])
            validate['ds'] = pd.to_datetime(validate['ds'])

            train = train[train['year']>=2002]
            train_reduced = train[self.needed + self.cate + self.exog]
            validate_reduced = validate[self.needed + self.cate + self.exog]

            self.meta_data['Sets']['train'] = train_reduced
            self.meta_data['Sets']['validate'] = validate_reduced
            

        except:
            pass

    def TuneModel(self):
        try:
            train = self.meta_data['Sets']['train']
            validate = self.meta_data['Sets']['validate']

            set = pd.concat([train, validate], axis=0)
            # print(set)
            # print(train)

            # print(validate)
            

            def objective(trial):
                params = {
                    # Core boosting params
                    "n_estimators": trial.suggest_int("n_estimators", 200, 2000),
                    "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                    "max_depth": trial.suggest_int("max_depth", 2, 12),
                    "min_child_weight": trial.suggest_float("min_child_weight", 0.5, 20.0, log=True),

                    # Subsampling
                    "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                    "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                    "colsample_bylevel": trial.suggest_float("colsample_bylevel", 0.5, 1.0),

                    # Regularization
                    "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),   # L1
                    "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True), # L2
                    "gamma": trial.suggest_float("gamma", 0.0, 10.0),

                    # Tree construction
                    "max_delta_step": trial.suggest_int("max_delta_step", 0, 10),

                    # Other
                    "tree_method": "hist",  # or "gpu_hist" if using GPU
                    "random_state": 42,
                    "verbosity": 0,
                }


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

                fsct.fit(df=train, static_features=[])


                cv_df = fsct.cross_validation(
                    df=set,
                    h=4,
                    n_windows=3,
                    static_features=[]
                )

                

                cv_df[['XGBRegressor','XGBRegressor2','XGBRegressor3']] = cv_df[['XGBRegressor','XGBRegressor2','XGBRegressor3']].round(2)
                # print(f'Cross Validation Frame =>\n{cv_df}\n')

                # cv_df.to_csv('Sample.csv',index=False)
                # return 0.5

                rmse = root_mean_squared_error(y_true=cv_df['y'], y_pred=cv_df['XGBRegressor'])
                # loss_lower = mean_pinball_loss(cv_df['y'], cv_df['XGBRegressor2'], alpha=0.10)
                # loss_upper = mean_pinball_loss(cv_df['y'], cv_df['XGBRegressor3'], alpha=0.90)
                # loss_median = mean_pinball_loss(cv_df['y'], cv_df['XGBRegressor'], alpha=0.5)

                # pinball_loss_total = (loss_lower + loss_median + loss_upper)/3

                
                return rmse


            study = optuna.create_study(direction='minimize')
            study.optimize(objective, n_trials=20, timeout=120)

            
            best_params = study.best_params

            self.best_params = best_params

        except Exception as e:
            print(f"Tune Exception -> [{e}]")
            pass
    
    def Save_Hyperparams(self):
        return self.best_params



def Load_Data(path=f'{BASE_DIR}/XGB/Data/FeatureEngineered_Data.csv'):
    df = pd.read_csv(path)
    
    df['datestamp'] = pd.to_datetime(df['datestamp'])
    df = df.rename(columns={'provinceid':'unique_id','datestamp':'ds','employment':'y'})

    keys = df['Key'].unique().tolist()

    return df, keys


def Generate_Sets(df):
    Set_Year_Markers = {
        'validateStart': 2024,
        'testStart': 2025
    }

    SplittObj = Splitter(Data=df, Set_Year_Markers=Set_Year_Markers)

    All_Sets = SplittObj.Generate_Sets()

    return All_Sets


def Tune_All(df, keys):
    try:
        
        All_Hyperparams = {}
        for key in tqdm(keys, desc='Processing Keys', unit='(provinceid, noc_groupingid)'):

            print(f"#Processing {key}#\n")

            data = df[df['Key']==key]

            
            data = data.sort_values(by='ds', ascending=True)

            All_Sets = Generate_Sets(df=data)

            meta_data = {
                'Key': key,
                'Sets': All_Sets
            }

            try:
                TuneObj = TunerClass(data=data, meta_data=meta_data)
                TuneObj.PreProcess_Sets()
                TuneObj.TuneModel()

                best_params = TuneObj.Save_Hyperparams()

                All_Hyperparams[key] = best_params
            except:
                continue
        
        
        with open(SAVE_PATH, "w") as file:
            json.dump(All_Hyperparams, file, indent=4)

        


    except Exception as e:
        print(f"Tune_All() => {e}")

if __name__ == '__main__':

    print(f"---Loading Data---\n")
    data, keys = Load_Data()

    print(f"---Running Tune---\n")

    Tune_All(df=data, keys=keys)
