# Abira Esther Demello

from MachineLearningLayer.Utils.Tuning import Tuner
from MachineLearningLayer.Utils.Splitter import Splitter
import pandas as pd
import warnings
import optuna
from neuralprophet import NeuralProphet, set_log_level
import os
from tqdm import tqdm
from sklearn.metrics import r2_score, mean_pinball_loss
import json

tqdm.pandas()
set_log_level("ERROR")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_PATH = f"{BASE_DIR}/Neural_Prophet/Data/All_Hyperparams.json"


def trial_score(trial, r2_weight=0.55, pinball_weight=0.45):
    """Score trials using weighted combination of R2 and pinball loss."""
    r2 = trial.values[0]
    pbl = trial.values[1]
    return (r2_weight * r2) - (pinball_weight * pbl)


class Neural_Prophet_Tuner(Tuner):
    def __init__(self, data, meta_data):
        self.data = data
        self.meta_data = meta_data
        self.best_params = None

    def TuneModel(self):
        try:
            train = self.meta_data['Sets']['train'][['ds', 'y']].copy()
            validate = self.meta_data['Sets']['validate'].copy()

            def objective(trial):
                params = {
                    "n_changepoints": trial.suggest_int("n_changepoints", 5, 30),
                    "changepoints_range": trial.suggest_float("changepoints_range", 0.5, 0.9),
                    "n_lags": trial.suggest_int("n_lags", 0, 12),
                    "yearly_seasonality": trial.suggest_categorical("yearly_seasonality", [True, False, "auto"]),
                    "weekly_seasonality": trial.suggest_categorical("weekly_seasonality", [False]),
                    "daily_seasonality": trial.suggest_categorical("daily_seasonality", [False]),
                    "seasonality_mode": trial.suggest_categorical("seasonality_mode", ["additive", "multiplicative"]),
                    "learning_rate": trial.suggest_float("learning_rate", 0.001, 0.1, log=True),
                    "epochs": trial.suggest_int("epochs", 50, 150),
                    "batch_size": trial.suggest_categorical("batch_size", [32, 64, 128]),
                    "loss_func": trial.suggest_categorical("loss_func", ["MSE", "Huber"]),
                }

                model = NeuralProphet(
                    n_changepoints=params["n_changepoints"],
                    changepoints_range=params["changepoints_range"],
                    n_lags=params["n_lags"],
                    yearly_seasonality=params["yearly_seasonality"],
                    weekly_seasonality=params["weekly_seasonality"],
                    daily_seasonality=params["daily_seasonality"],
                    seasonality_mode=params["seasonality_mode"],
                    learning_rate=params["learning_rate"],
                    epochs=params["epochs"],
                    batch_size=params["batch_size"],
                    loss_func=params["loss_func"],
                )

                # Fit model
                model.fit(train, freq="MS")

                # Predict on validation set
                future = model.make_future_dataframe(train, periods=len(validate))
                forecast = model.predict(future)

                # Get only future predictions and merge with actual values
                forecast_future = forecast[forecast['ds'] > train['ds'].max()][['ds', 'yhat1']].copy()
                forecast_future = forecast_future.merge(validate[['ds', 'y']], on='ds')

                # Calculate metrics
                y_true = forecast_future['y'].values
                y_pred = forecast_future['yhat1'].values

                r2 = r2_score(y_true, y_pred)
                pinball_loss = mean_pinball_loss(y_true, y_pred, alpha=0.5)

                return r2, pinball_loss

            # Multi-objective optimization
            study = optuna.create_study(directions=['maximize', 'minimize'])
            study.optimize(objective, n_trials=20, timeout=300, show_progress_bar=False)

            # Select best trial from Pareto front
            pareto_trials = study.best_trials
            best_trial = max(pareto_trials, key=lambda t: trial_score(t, 0.55, 0.45))
            self.best_params = best_trial.params

        except Exception as e:
            print(f"TuneModel error: {e}")
            # Default params if tuning fails
            self.best_params = {
                "n_changepoints": 10,
                "changepoints_range": 0.8,
                "n_lags": 6,
                "yearly_seasonality": True,
                "weekly_seasonality": False,
                "daily_seasonality": False,
                "seasonality_mode": "additive",
                "learning_rate": 0.01,
                "epochs": 100,
                "batch_size": 64,
                "loss_func": "MSE",
            }

    def Save_Hyperparams(self):
        return self.best_params


def Load_Data(path=f'{BASE_DIR}/Neural_Prophet/Data/Neural_PreProcessed_Data.csv'):
    df = pd.read_csv(path)
    df['ds'] = pd.to_datetime(df['ds'])
    ids = df['ID'].unique().tolist()
    return df, ids


def Generate_Sets(df):
    Set_Year_Markers = {
        'validateStart': 2024,
        'testStart': 2025
    }
    splitter = Splitter(Data=df, Set_Year_Markers=Set_Year_Markers)
    return splitter.Generate_Sets()


def Tune_All(df, ids):
    try:
        All_Hyperparams = {}

        for series_id in tqdm(ids, desc='Tuning series', unit='series'):
            print(f"\n# Tuning {series_id} #")

            data = df[df['ID'] == series_id].copy()
            data = data.sort_values(by='ds', ascending=True)

            All_Sets = Generate_Sets(df=data)

            meta_data = {
                'ID': series_id,
                'Sets': All_Sets
            }

            tuner = Neural_Prophet_Tuner(data=data, meta_data=meta_data)
            tuner.TuneModel()

            best_params = tuner.Save_Hyperparams()
            All_Hyperparams[series_id] = best_params

        # Save all hyperparameters
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        with open(SAVE_PATH, "w") as f:
            json.dump(All_Hyperparams, f, indent=4)

        print(f"\n--- Hyperparameters saved to {SAVE_PATH} ---")

    except Exception as e:
        print(f"Tune_All error: {e}")


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    print("--- Loading Data ---\n")
    data, ids = Load_Data()

    print(f"--- Running Tuning for {len(ids)} series ---\n")
    Tune_All(df=data, ids=ids)
