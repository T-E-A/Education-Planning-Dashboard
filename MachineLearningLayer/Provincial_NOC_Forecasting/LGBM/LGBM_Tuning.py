from MachineLearningLayer.Utils.Tuning import Tuner
from MachineLearningLayer.Utils.Splitter import Splitter
import pandas as pd
import warnings
import optuna
from lightgbm import LGBMRegressor
import os
from tqdm import tqdm
tqdm.pandas()
from sklearn.metrics import  r2_score, mean_pinball_loss
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_PATH = f"{BASE_DIR}/LGBM/Data/All_Hyperparams.json"

def trial_score(trial, r2_weight=0.55, pin_ball_loss=0.45):
    r2 = trial.values[0]
    pbL = trial.values[1]
    return (r2_weight * r2) - (pin_ball_loss * pbL)

class TunerClass(Tuner):
    def __init__(self, data, meta_data):
        self.data = data
        self.meta_data = meta_data
        self.best_params = None

    def TuneModel(self):
        try:
            train = self.meta_data['Sets']['train'][['ds','y']]
            validate = self.meta_data['Sets']['validate'][['ds','y']]
            

            def objective(trial):
                params = {
                    "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
                    "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
                    "num_leaves": trial.suggest_int("num_leaves", 20, 150),
                    "max_depth": trial.suggest_int("max_depth", 5, 30),
                    "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
                    "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                    "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                    "reg_alpha": trial.suggest_float("reg_alpha", 0.0, 1.0),
                    "reg_lambda": trial.suggest_float("reg_lambda", 0.0, 1.0),
                    "early_stoppinground": trial.suggest_int("early_stoppinground", 10, 50),
                }

                model = LGBMRegressor(
                    n_estimators=params["n_estimators"],
                    learning_rate=params["learning_rate"],
                    num_leaves=params["num_leaves"],
                    max_depth=params["max_depth"],
                    min_child_samples=params["min_child_samples"],
                    subsample=params["subsample"],
                    colsample_bytree=params["colsample_bytree"],
                    reg_alpha=params["reg_alpha"],
                    reg_lambda=params["reg_lambda"],
                    early_stoppinground=params["early_stoppinground"],
                )

                model.fit(train[['ds']], train['y'])

                preds = model.predict(validate[['ds']])

                r2 = r2_score(validate['y'], preds)
                pbl = mean_pinball_loss(validate['y'], preds, alpha=0.5)

                return r2, pbl

            study = optuna.create_study(directions=["maximize", "minimize"])
            study.optimize(objective, n_trials=20, timeout=120)
            
            best_params = study.best_params
            self.best_params = best_params
        
        except Exception as e:
            print(f"Tune Exception -> [{e}]")
            pass

        def Save_Hyperparams(self):
            return self.best_params

def Load_Data(path=f"{BASE_DIR}/LGBM/Data/PreProcessed_Data.csv"):
    df = pd.read_csv(path)
    
    df['datestamp'] = pd.to_datetime(df['datestamp'])
    df = df.rename(columns={'datestamp':'ds','employment':'y','noc_groupingid':'unique_id'})
    
    keys = df['Key'].unique().tolist()
    
    return df, keys

def Generate_Sets(df):
    Set_Year_Marker = {
        'validateStart': 2024,
        'testStart': 2025
    }
    
    SplittObj = Splitter(Data=df, Set_Year_Markers=Set_Year_Marker)
    
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
            json.dump(All_Hyperparams, file)
    
    except Exception as e:
        print(f"Error during tuning: {e}")

if __name__ == '__main__':
    
    print(f"---Loading Data---\n")
    df, keys = Load_Data()
    
    print(f"---Running Tune---\n")
    Tune_All(df, keys)