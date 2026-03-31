from MainService import DataRequester as DataService
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd 
import numpy as np
import polars as pl
import calendar

logger = logging.getLogger(__name__)


#region [Rename Dicts]
# used to rename raw API column names to cleaner readable labels for the dashboard

Latest_KPI_Rename_Dict = {
    'employment_rate_2_years_after_graduating_field': '2020 Employment Rate 2 Years after Graduation',
    'employment_rate_6_months_after_graduating_field': '2020 Employment Rate 6 Months after Graduation',
    'graduation_rate': '2020 Graduation Rate',
    'university':'University',
    'programcategoryid':'ProgramID',
    'universityid':'UniversityID',
    'lat':'Lat',
    'lon':'Lon',
    'year':'Year'
}

All_KPI_Rename_Dict = {
    'employment_rate_2_years_after_graduating_field': 'Employment Rate 2 Years after Graduation',
    'employment_rate_6_months_after_graduating_field': 'Employment Rate 6 Months after Graduation',
    'graduation_rate': 'Graduation Rate',
    'university':'University',
    'programcategoryid':'ProgramID',
    'universityid':'UniversityID',
    'lat':'Lat',
    'lon':'Lon',
    'year':'Year'
}

Program_Links_Rename_Dict = {
    'programid' : 'ProgramID',
    'program' : 'Program',
    'broad_occupation_category':'Broad Occupation Category',
    'sub_major_group': 'Sub-Major Group',
    'unit_group_occupation': 'Unit Group Occupation'
}

Province_Employment_History_Dict = {
    'datestamp': 'ds',
    'employment':'Employment (Persons in Thousands)',
    'employment_moving_average':'3-Month Moving Average',
    'employment_upper_band':'Upper Band',
    'employment_lower_band': 'Lower Band'
}

Economic_Region_Employment_Dict = {
    'economicregion':'Economic Region',
    'employment_pct_change': 'Monthly PCT',
}
#endregion


#region [KPI Functions]

def Get_All_Program_University_Data():
    """
    Returns: a list of dicts of all program university KPI data across all years,
    Args: none
    """
    try:

        df = DataService.RequestAllKPIs()
        df = df.fillna(0)
        df = df.rename(columns=All_KPI_Rename_Dict)
        return df.to_dict(orient='records')
        
    except Exception as e:
        logger.exception(f'[{e}]')
        return []

def Get_Latest_Program_University_Data():
    """
    Returns: a list of dicts of the latest program university KPI data,
    """
    try:
        df = DataService.RequestLatestKPIs()
        df = df.fillna(0)
        df = df.rename(columns=Latest_KPI_Rename_Dict)
        return df.to_dict(orient='records')

    except Exception as e:
        logger.exception(f'[{e}]')
        return []

def Get_University_KPI_Data():
    """
    Returns: a dict with 'All' and 'Latest' keys, each containing their respective KPI records, empty dict on failure
    """
    try:
        Data_Directory = {
            'All': {},
            'Latest':{}
        }

        # map keys to their respective functions so we can run them in parallel
        Data_Directory_Threads = {
            'All': Get_All_Program_University_Data,
            'Latest': Get_Latest_Program_University_Data
        }

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            future_to_key = {
                executor.submit(func): key
                for key, func in Data_Directory_Threads.items()
            }

            # Collect results as they finish
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    Data_Directory[key] = future.result()
                except Exception as e:
                    logging.getLogger(__name__).exception(
                        f"Error in {key} thread [{e}]"
                    )
                    Data_Directory[key] = {}

        return Data_Directory
    except Exception as e:
        logger.exception(f'[{e}]')
        return {}
#endregion

#region [Progam - NOC Links]

def Get_Program_To_Occupation_Data(ProgramID: int) -> list:
    """
    Returns: a list of dicts mapping the given program to its linked NOC occupations, returns an empty list on failure
    Args:
        ProgramID: int -> the ID of the program to look up NOC links for
    """
    try:
        df = DataService.RequestProgramNOCLinks(ProgramID=ProgramID)

        df = df.rename(columns=Program_Links_Rename_Dict)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.exception(f'[{e}]')
        return []
#endregion

#region [Historical NOC Grouping Data]

def Get_NOC_Historical_Data(NOC_GroupingID,DGUID='2021A000235'):
    """
    Returns: a list of dicts of historical labour statistics for a NOC group in a given region, empty list on failure
    Args:
        NOC_GroupingID: int => the NOC grouping ID to pull history for
        DGUID: str => the dissemination geo unique ID for the region, defaults to '2021A000235'
    """
    try:
        df = DataService.RequestNOCGroupLaborStatistics(NOC_GroupingID=NOC_GroupingID,DGUID=DGUID)
        
        df = df.rename(columns=Province_Employment_History_Dict)

        return df.to_dict(orient='records')

    except Exception as e:
        logger.exception(f'[{e}]')
        return []

def Get_Latest_ER_NOC_PCT(NOC_GroupingID, provinceID=35):
    """
    Returns: a list of dicts of the latest economic region employment % change for a NOC group, 
    Args:
        NOC_GroupingID: int => the NOC grouping ID to filter by
        provinceID: int => the province ID to pull economic regions for, defaults to 35 (Ontario)
    """
    try:
        df = DataService.RequestEconomicRegionEmploymentEstimate(NOC_GroupingID=NOC_GroupingID, ProvinceID=provinceID)
        
        df['employment_pct_change'] = pd.to_numeric(df['employment_pct_change'], errors='coerce').fillna(0)

        # label each region as increasing, decreasing, or no change based on the pct value
        conditions = [
            df['employment_pct_change'] > 0,
            df['employment_pct_change'] < 0,
            df['employment_pct_change'] == 0
        ]
        choices = ['Increase', 'Decrease', 'No Change']
        df['Change'] = np.select(conditions, choices, default='No Data').astype(str)
        
        df = df.rename(columns=Economic_Region_Employment_Dict)

        return df.to_dict(orient='records')

    except Exception as e:
        logger.exception(f'[{e}]')
        return []

def Get_NOC_Historical(NOC_GroupingID, provinceID=35, DGUID='2021A000235'):
    """
    Returns: a dict with 'PROV' and 'ER' keys containing provincial history and economic region data, empty dict on failure
    Args:
        NOC_GroupingID: int --> the NOC grouping ID to pull data for
        provinceID: int --> the province ID, defaults to 35 (Ontario)
        DGUID: str --> the dissemination geo unique ID for the region, defaults to '2021A000235'
    """
    try:
        
        Data_Directory = {
            'PROV': {},
            'ER': {}
        }

        # Map keys to their respective functions and args so we can both in parallel
        tasks = {
            'PROV': (Get_NOC_Historical_Data, (NOC_GroupingID, DGUID)),
            'ER': (Get_Latest_ER_NOC_PCT, (NOC_GroupingID, provinceID))
        }

        # Submit all tasks
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_key = {
                executor.submit(func, *args): key for key, (func, args) in tasks.items()
            }

            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    Data_Directory[key] = future.result()
                except Exception as e:
                    logger.exception(f'Error in thread for {key}: [{e}]')
                    Data_Directory[key] = []

        return Data_Directory

    except Exception as e:
        logger.exception(f'[{e}]')
        return {}
#endregion

#region [Provincial Forecast]
def Get_Provincial_NOC_Forecast(provinceid : int, noc_groupingid : int) -> list:
    """
    Returns: a list of dicts of forecasted employment data for a NOC group in a specific province, empty list on failure
    Args:
        provinceid: int --> the ID of the province to filter by
        noc_groupingid: int --> the NOC grouping ID to filter by
    """
    try:
        df = DataService.Request_Provincial_NOC_Forecast(provinceID=provinceid, noc_groupingid=noc_groupingid)

        df['yhat'] = df['yhat'].round(2)
        df['yhat_lower'] = df['yhat_lower'].round(2)
        df['yhat_upper'] = df['yhat_upper'].round(2)

        df = df.fillna(0)

        return df.to_dict(orient='records')

    except Exception as e:
        logger.exception(f'[{e}]')
        return []

def Get_NOC_Forecast_All_Provinces(noc_groupingid : int) -> list:
    """
    Returns: a list of dicts with yearly employment forecasts per province pivoted by year, empty list on failure
    Args:
        noc_groupingid: int -> the NOC grouping ID to get forecasts for
    """
    try:
        df = DataService.Request_All_Province_NOC_Forecast(noc_groupingid=noc_groupingid)

        df = df.rename(columns={'province_shorthand':'Province','year':'Year'})

        # only keep forecast years from 2026 onwards
        df = df[df['Year']>=2026]
        

        Years = sorted(df['Year'].unique())

        df = df.sort_values(by=['provinceid','Year'], ascending=[True,True])

        # pivot so each year becomes its own column with province as the row
        df_pivot = df.pivot(index='Province', columns='Year', values='Employment Forecast')

        df_pivot['Province'] = df_pivot.index
        df_pivot = df_pivot.reset_index(drop=True)

        df_pivot = df_pivot[['Province'] + Years]

        df_pivot = df_pivot.fillna(0)

        
        return df_pivot.to_dict(orient='records')
    

    except Exception as e:
        logger.exception(f'[{e}]')
        return []

def Get_Forecast_Data(provinceid: int, noc_groupingid: int) -> dict:
    """
    Returns: a dict with 'PROV' and 'ALL' keys containing provincial and all-province forecast data, empty dict on failure
    Args:
        provinceid: int -> the ID of the province for the provincial forecast
        noc_groupingid: int -> the NOC grouping ID to get forecasts for
    """

    try:
        Data_Directory = {
            'PROV': {},
            'ALL': {}
        }

        # Map keys to their respective functions; run both forecast functions in parallel
        tasks = {
            'PROV': (Get_Provincial_NOC_Forecast, (provinceid, noc_groupingid)),
            'ALL': (Get_NOC_Forecast_All_Provinces, (noc_groupingid,))
        }

        # Submit all tasks
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_key = {
                executor.submit(func, *args): key for key, (func, args) in tasks.items()
            }

            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    Data_Directory[key] = future.result()
                except Exception as e:
                    logger.exception(f'Error in thread for {key}: [{e}]')
                    Data_Directory[key] = []

        return Data_Directory
        

    except Exception as e:
        logger.exception(f'[{e}]')
        return {}

#endregion 

#region [Seasonal Decomp and TS Clustering Requests]
def Transform_Set(Data: pd.DataFrame):
    """
    Returns: the same DataFrame with added date-related columns (Year, Month_Num, Month_Name, Quarter)
    Args:
        Data: pd.DataFrame => the raw seasonal decomposition DataFrame with a 'datestamp' column
    """
    try:
        
        Data['datestamp'] = pd.to_datetime(Data['datestamp'])
        Data['Year'] = Data['datestamp'].dt.year
        Data['Month_Num'] = Data['datestamp'].dt.month
        Data['Month_Name'] = Data['datestamp'].dt.month_name()
        Data['Quarter'] = Data['datestamp'].dt.quarter


        return Data

    except Exception as e:
        logger.exception(f'[{e}]')
        return Data

def Get_Decomp_Set(provinceid):
    """
    Returns: a Polars DataFrame of the seasonal decomposition data for a given province
    Args:
        provinceid: int --> the ID of the province to pull decomposition data for
    """
    try:
        
        df_Decomp_Set = DataService.RequestionSeasonalDecomp(provinceid=provinceid)
        df_Decomp_Set = Transform_Set(Data=df_Decomp_Set)
        dp_Decomp_Set = pl.from_pandas(df_Decomp_Set)

        return dp_Decomp_Set

    except Exception as e:
        logger.exception(f'[{e}]')
        return dp_Decomp_Set

def Filter_Set(dp_Decomp_Set):
    """
    Returns: a filtered Polars DataFrame containing only rows between 2022 and 2024, empty Polars DataFrame on failure
    Args:
        dp_Decomp_Set: pl.DataFrame => the full decomposition dataset to filter
    """
    try:
        
        dp_Filtered_Set = dp_Decomp_Set.filter((pl.col('Year')>= 2022) & (pl.col('Year')<= 2024))
        return dp_Filtered_Set
    
    except Exception as e:
        logger.exception(f'[{e}]')
        return pl.DataFrame()

def Generate_Cluster_Month_Comparison(dp_Filtered_Set,month):
    """
    Returns: a pandas DataFrame comparing clusters by their average seasonal trend for a given month, 
    Args:
        dp_Filtered_Set: pl.DataFrame => the filtered decomposition dataset
        month: int => the month number to filter by, ex. 4 for April
    """
    try:

        change_cols = {'seasonal_3': f'Average Trend for {calendar.month_name[month]}',
                       'trend_cluster':'Cluster'  
                       }

        df_Comp = dp_Filtered_Set.filter(pl.col('Month_Num')==month).group_by('trend_cluster').agg(
            pl.col('noc_groupingid').n_unique().alias('Number of NOC Groupings'),
            (pl.col('seasonal_3').mean()*1000).round(3).alias('seasonal_3')
        ).to_pandas().sort_values(by=f'seasonal_3', ascending=False).reset_index(drop=True)

        # label each cluster as increasing, decreasing, or no change
        conditions = [
            df_Comp['seasonal_3'] > 0,
            df_Comp['seasonal_3'] < 0,
            df_Comp['seasonal_3'] == 0
        ]
        choices = ['Increase', 'Decrease', 'No Change']
        df_Comp['Month Trend Segment'] = np.select(conditions, choices, default='No Data').astype(str)

        df_Comp = df_Comp.rename(columns=change_cols)
        
    
        return df_Comp

    except Exception as e:
        logger.exception(f'[{e}]')
        return pd.DataFrame()

def Generate_Cluster_Quarter_Comparison(dp_Filtered_Set,quarter):
    """
    Returns: a pandas DataFrame comparing clusters by their average seasonal trend for a given quarter, empty DataFrame on failure
    Args:
        dp_Filtered_Set: pl.DataFrame => the filtered decomposition dataset
        quarter: int => the quarter number to filter by, ex. 1 for Q1
    """
    try:

        change_cols = {'seasonal_3': f'Average Trend for Q{quarter}',
                       'trend_cluster':'Cluster'  
                       }

        df_Comp = dp_Filtered_Set.filter(pl.col('Quarter')==quarter).group_by('trend_cluster').agg(
            (pl.col('seasonal_3').mean()*1000).round(3).alias('seasonal_3')
        ).to_pandas().sort_values(by='seasonal_3', ascending=False).reset_index(drop=True)

        # label each cluster as increasing, decreasing, or no change
        conditions = [
            df_Comp['seasonal_3'] > 0,
            df_Comp['seasonal_3'] < 0,
            df_Comp['seasonal_3'] == 0
        ]
        choices = ['Increase', 'Decrease', 'No Change']
        df_Comp['Quarter Trend Segment'] = np.select(conditions, choices, default='No Data').astype(str)

        df_Comp = df_Comp.rename(columns=change_cols)
        
    
        return df_Comp

    except Exception as e:
        logger.exception(f'[{e}]')
        return pd.DataFrame()

def Generate_Processed_Clustered_NOC_Sets(provinceid: int, quarter: int, month: int) -> dict:
    """
    Returns: a dict with 'FullSet', 'AnalysisSet', and 'ClusterDict' containing the full decomp data, combined cluster analysis, and a cluster ID to name mapping, empty dict on failure
    Args:
        provinceid: int => the ID of the province to generate cluster sets for
        quarter: int => the quarter number to use in the analysis, ex. 1 for Q1
        month: int => the month number to use in the analysis, ex. 1 for January
    """
    try:
        
        dp_Decomp_Set = Get_Decomp_Set(provinceid=provinceid)

        dp_Filtered_Set = Filter_Set(dp_Decomp_Set=dp_Decomp_Set)

        df_Monthly_Comp = Generate_Cluster_Month_Comparison(dp_Filtered_Set, month)
        df_Quarter_Comp = Generate_Cluster_Quarter_Comparison(dp_Filtered_Set, quarter)

        # merge monthly and quarterly comparisons on cluster and add a readable cluster name 
        df_Combined_Analysis = df_Quarter_Comp.merge(df_Monthly_Comp, on=['Cluster'], how='inner')
        df_Combined_Analysis['Cluster Name'] = df_Combined_Analysis['Cluster'].apply(lambda x: f"Cluster [{x}]")
        df_Combined_Analysis = df_Combined_Analysis.sort_values(by=[f'Average Trend for Q{quarter}'], ascending=False)

        ClusterID_ClusterName_Dict = df_Combined_Analysis.set_index('Cluster')['Cluster Name'].to_dict()

        Payloads = {
            'FullSet': dp_Decomp_Set.to_pandas().to_dict(orient='records'),
            'AnalysisSet': df_Combined_Analysis.to_dict(orient='records'),
            'ClusterDict':ClusterID_ClusterName_Dict
        }

        return Payloads

    except Exception as e:
        logger.exception(f'[{e}]')
        return {}

#endregion