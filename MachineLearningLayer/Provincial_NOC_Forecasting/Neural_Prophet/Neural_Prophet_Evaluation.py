# Abira Esther Demello

from MachineLearningLayer.Utils.Evaluation import Evaluater
import pandas as pd
import polars as pl
import os
import warnings
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, root_mean_squared_error
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Neural_Prophet_Evaluator(Evaluater):
    def __init__(self, forecast_data):
        self.forecast_data = forecast_data
        self.evaluation_data = None

    def Calculate_Regression_Metrics(self):
        try:
            df = self.forecast_data.copy()

            # Try to get province and NOC group names from API first
            has_names = False
            try:
                from MachineLearningLayer import DataService
                df_Province = DataService.GetProvinceNames()
                df_NOCGroups = DataService.GetNOCGroupingNames()
                df = df.merge(df_Province, on='provinceid', how='left')
                df = df.merge(df_NOCGroups, on='noc_groupingid', how='left')
                has_names = True
            except:
                pass

            # Fallback: Load from CSV files directly
            if not has_names:
                try:
                    df_Province = pd.read_csv('DataFiles/Tbl_Provinces.csv')
                    df_Province.columns = df_Province.columns.str.lower()
                    df_Province = df_Province[['provinceid', 'province_shorthand']].drop_duplicates()
                    
                    df_NOCGroups = pd.read_csv('DataFiles/Tbl_NOC_TS_Groupings.csv')
                    df_NOCGroups.columns = df_NOCGroups.columns.str.lower()
                    df_NOCGroups = df_NOCGroups[['noc_groupingid', 'noc_grouping']].drop_duplicates()
                    
                    df = df.merge(df_Province, on='provinceid', how='left')
                    df = df.merge(df_NOCGroups, on='noc_groupingid', how='left')
                    has_names = True
                except Exception as e:
                    print(f"Could not load province/NOC names from files: {e}")
                    df['province_shorthand'] = df['provinceid'].astype(str)
                    df['noc_grouping'] = df['noc_groupingid'].astype(str)

            # Calculate metrics per group (matching Prophet's format exactly)
            df_Eval = df.groupby(['provinceid', 'province_shorthand', 'noc_groupingid', 'noc_grouping']).apply(
                lambda grp: pd.DataFrame({
                    "r2": [r2_score(grp['y'].to_numpy(), grp['yhat'].to_numpy())],
                    "euclidean distance": [np.linalg.norm(grp['y'].to_numpy() - grp['yhat'].to_numpy())],
                    "mae": [mean_absolute_error(grp['y'].to_numpy(), grp['yhat'].to_numpy())],
                    "rmse": [root_mean_squared_error(grp['y'].to_numpy(), grp['yhat'].to_numpy())],
                    "mse": [mean_squared_error(grp['y'].to_numpy(), grp['yhat'].to_numpy())],
                    'Average Actual': [grp['y'].mean()],
                    'CV RMSE': [root_mean_squared_error(grp['y'].to_numpy(), grp['yhat'].to_numpy()) / grp['y'].mean() if grp['y'].mean() != 0 else np.nan],
                    'CV MAE': [mean_absolute_error(grp['y'].to_numpy(), grp['yhat'].to_numpy()) / grp['y'].mean() if grp['y'].mean() != 0 else np.nan],
                    'MAPE': [(np.abs(grp['y'] - grp['yhat']) / grp['y'].replace(0, np.nan)).mean() * 100]
                })
            ).reset_index().drop('level_4', axis=1, errors='ignore')

            df_Eval = df_Eval.sort_values(by=['r2'], ascending=False)

            print(f"-- Metrics Calculated --\n{df_Eval.head(10)}")

            self.evaluation_data = df_Eval

        except Exception as e:
            print(f"Calculate_Regression_Metrics error: {e}")
            import traceback
            traceback.print_exc()

    def Save_Metrics(self):
        try:
            if self.evaluation_data is not None:
                df = self.evaluation_data.copy()

                # Save CSV
                output_path = f'{BASE_DIR}/Neural_Prophet/Data/Evaluation_Metrics.csv'
                df.to_csv(output_path, index=False)
                print(f"--- Evaluation Metrics saved to {output_path} ---\n")

                # Generate HTML report
                reports_dir = f"{BASE_DIR}/Neural_Prophet/Data/Reports"
                os.makedirs(reports_dir, exist_ok=True)
                
                # Try ydata_profiling first, fallback to simple HTML
                try:
                    from ydata_profiling import ProfileReport
                    profile = ProfileReport(df, title="Neural Prophet Evaluation Metrics Report", explorative=True)
                    profile.to_file(f"{reports_dir}/Evaluation_Metrics_Report.html")
                    print(f"--- Evaluation Report (ydata_profiling) saved ---\n")
                except ImportError:
                    # Generate simple HTML report
                    html_report = self._generate_simple_html_report(df)
                    with open(f"{reports_dir}/Evaluation_Metrics_Report.html", 'w') as f:
                        f.write(html_report)
                    print(f"--- Evaluation Report (simple HTML) saved ---\n")

        except Exception as e:
            print(f"Save_Metrics error: {e}")

    def _generate_simple_html_report(self, df):
        """Generate a comprehensive HTML report similar to ydata-profiling."""
        
        # Calculate detailed statistics
        numeric_cols = ['r2', 'euclidean distance', 'mae', 'rmse', 'mse', 'Average Actual', 'CV RMSE', 'CV MAE', 'MAPE']
        stats = df[numeric_cols].describe().round(4)
        
        # Count performance categories
        excellent = len(df[df['r2'] >= 0.7])
        good = len(df[(df['r2'] >= 0.4) & (df['r2'] < 0.7)])
        fair = len(df[(df['r2'] >= 0) & (df['r2'] < 0.4)])
        poor = len(df[df['r2'] < 0])
        
        # Province breakdown
        province_stats = df.groupby('province_shorthand').agg({
            'r2': ['mean', 'std', 'min', 'max', 'count'],
            'MAPE': 'mean'
        }).round(4)
        province_stats.columns = ['R² Mean', 'R² Std', 'R² Min', 'R² Max', 'Count', 'MAPE Mean']
        province_stats = province_stats.reset_index().sort_values('R² Mean', ascending=False)
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Neural Prophet Evaluation Metrics Report</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 28px; }}
        .header p {{ margin: 0; opacity: 0.9; }}
        .card {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #333; margin-top: 0; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .metric-card .value {{ font-size: 32px; font-weight: bold; }}
        .metric-card .label {{ font-size: 14px; opacity: 0.9; margin-top: 5px; }}
        .performance-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
        .perf-card {{ padding: 15px; border-radius: 8px; text-align: center; }}
        .perf-excellent {{ background: #d4edda; color: #155724; }}
        .perf-good {{ background: #cce5ff; color: #004085; }}
        .perf-fair {{ background: #fff3cd; color: #856404; }}
        .perf-poor {{ background: #f8d7da; color: #721c24; }}
        .perf-card .count {{ font-size: 28px; font-weight: bold; }}
        .perf-card .label {{ font-size: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }}
        th {{ background: #667eea; color: white; padding: 12px 8px; text-align: left; position: sticky; top: 0; }}
        td {{ padding: 10px 8px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f8f9fa; }}
        .table-container {{ max-height: 500px; overflow-y: auto; }}
        .stats-table th {{ background: #f8f9fa; color: #333; }}
        .highlight-good {{ background: #d4edda; }}
        .highlight-bad {{ background: #f8d7da; }}
        .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        @media (max-width: 768px) {{ .two-col {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Neural Prophet Evaluation Report</h1>
            <p>Comprehensive analysis of {len(df)} province-NOC time series forecasts</p>
        </div>
        
        <div class="card">
            <h2>Key Performance Metrics</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="value">{df['r2'].mean():.4f}</div>
                    <div class="label">Mean R² Score</div>
                </div>
                <div class="metric-card">
                    <div class="value">{df['mae'].mean():.2f}</div>
                    <div class="label">Mean Absolute Error</div>
                </div>
                <div class="metric-card">
                    <div class="value">{df['rmse'].mean():.2f}</div>
                    <div class="label">Root Mean Square Error</div>
                </div>
                <div class="metric-card">
                    <div class="value">{df['MAPE'].mean():.1f}%</div>
                    <div class="label">Mean Absolute % Error</div>
                </div>
            </div>
            
            <h3>Model Performance Distribution</h3>
            <div class="performance-grid">
                <div class="perf-card perf-excellent">
                    <div class="count">{excellent}</div>
                    <div class="label">Excellent (R² ≥ 0.7)</div>
                </div>
                <div class="perf-card perf-good">
                    <div class="count">{good}</div>
                    <div class="label">Good (0.4 ≤ R² < 0.7)</div>
                </div>
                <div class="perf-card perf-fair">
                    <div class="count">{fair}</div>
                    <div class="label">Fair (0 ≤ R² < 0.4)</div>
                </div>
                <div class="perf-card perf-poor">
                    <div class="count">{poor}</div>
                    <div class="label">Poor (R² < 0)</div>
                </div>
            </div>
        </div>
        
        <div class="two-col">
            <div class="card">
                <h2>Statistical Summary</h2>
                <table class="stats-table">
                    <tr><th>Metric</th><th>Mean</th><th>Std</th><th>Min</th><th>25%</th><th>50%</th><th>75%</th><th>Max</th></tr>
                    <tr><td>R²</td><td>{stats.loc['mean','r2']:.4f}</td><td>{stats.loc['std','r2']:.4f}</td><td>{stats.loc['min','r2']:.4f}</td><td>{stats.loc['25%','r2']:.4f}</td><td>{stats.loc['50%','r2']:.4f}</td><td>{stats.loc['75%','r2']:.4f}</td><td>{stats.loc['max','r2']:.4f}</td></tr>
                    <tr><td>MAE</td><td>{stats.loc['mean','mae']:.4f}</td><td>{stats.loc['std','mae']:.4f}</td><td>{stats.loc['min','mae']:.4f}</td><td>{stats.loc['25%','mae']:.4f}</td><td>{stats.loc['50%','mae']:.4f}</td><td>{stats.loc['75%','mae']:.4f}</td><td>{stats.loc['max','mae']:.4f}</td></tr>
                    <tr><td>RMSE</td><td>{stats.loc['mean','rmse']:.4f}</td><td>{stats.loc['std','rmse']:.4f}</td><td>{stats.loc['min','rmse']:.4f}</td><td>{stats.loc['25%','rmse']:.4f}</td><td>{stats.loc['50%','rmse']:.4f}</td><td>{stats.loc['75%','rmse']:.4f}</td><td>{stats.loc['max','rmse']:.4f}</td></tr>
                    <tr><td>MAPE (%)</td><td>{stats.loc['mean','MAPE']:.2f}</td><td>{stats.loc['std','MAPE']:.2f}</td><td>{stats.loc['min','MAPE']:.2f}</td><td>{stats.loc['25%','MAPE']:.2f}</td><td>{stats.loc['50%','MAPE']:.2f}</td><td>{stats.loc['75%','MAPE']:.2f}</td><td>{stats.loc['max','MAPE']:.2f}</td></tr>
                </table>
            </div>
            
            <div class="card">
                <h2>Performance by Province</h2>
                <div class="table-container">
                    {province_stats.to_html(index=False, classes='stats-table')}
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Top 10 Best Performing Series</h2>
            <div class="table-container">
                {df.head(10).to_html(index=False)}
            </div>
        </div>
        
        <div class="card">
            <h2>Bottom 10 Worst Performing Series</h2>
            <div class="table-container">
                {df.tail(10).to_html(index=False)}
            </div>
        </div>
        
        <div class="card">
            <h2>All Series Metrics</h2>
            <div class="table-container">
                {df.to_html(index=False)}
            </div>
        </div>
    </div>
</body>
</html>"""


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    print("--- Loading Forecast Data ---\n")
    df_forecast = pl.scan_parquet(f'{BASE_DIR}/Neural_Prophet/Data/All_Forecasts.parquet')

    # Filter to validation and test sets only (where we have actual values)
    forecast_data = df_forecast.filter(
        pl.col('Set').is_in(['Validation', 'Test'])
    ).collect().to_pandas()

    print(f"Loaded {len(forecast_data)} forecast records for evaluation")

    evaluator = Neural_Prophet_Evaluator(forecast_data=forecast_data)

    print("--- Calculating Evaluation Metrics ---\n")
    evaluator.Calculate_Regression_Metrics()

    print("--- Saving Evaluation Metrics ---\n")
    evaluator.Save_Metrics()