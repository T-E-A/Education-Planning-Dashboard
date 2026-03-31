from MainService import DataUtils, OptionsUtils, DataRequester
import pandas as pd 
import polars as pl
import logging

logger = logging.getLogger(__name__)

#region [Services Heartbeat Check]

def Check_Services_Heartbeat():
    """
    Returns: True if the Django API is reachable, False otherwise
    Args: None
    """
    try:
        
        Heartbeat = DataRequester.Check_Heartbeat()
        if Heartbeat:
            return True
        else:
            return False

    except Exception as e:
        logger.info(f'[{e}]')

#endregion

#region [Global Vars]
# holds all dropdown/options dicts loaded at startup, access across the service

Options_Directory = {
    'Programs': {},
    'Universities': {},
    'Provinces':{},
    'NOCGrouping':{}
}

# KPI measure label dicts pulled from OptionUtils.py file for the lastest and all-year data
Latest_KPI_Measure_Dict = OptionsUtils.Program_Post_Grad_Employment_Rate_Latest_Dict
All_KPI_Measure_Dict = OptionsUtils.Program_Post_Grad_Employment_Rate_All_Dict
#endregion

#region [Options Loading]

def Load_All_Options_Dicts() -> dict:
    """
    Returns: a dict of all options/dropdowns loaded into the global Options_Directory, empty dict on failure
    Args: none
    """
    try:
        global Options_Directory

        Options_Directory = OptionsUtils.Get_All_Options_Dicts()

        return Options_Directory

    except Exception as e:
        logger.exception(f'Error [{e}]')
        return {}
#endregion 

#region [Univeristy KPI Related Functions]

def Load_All_KPI_Data() -> list:
    """
    Returns: a list of dicts containing all university KPI data across all years and programs, empty list on failure
    Args: none
    """
    try:
        
        return DataUtils.Get_University_KPI_Data()

    except Exception as e:
        logger.exception(f'Error [{e}]')
        return []
#endregion

#region [Program - NOC Link Functions]

def Get_Program_To_NOC_Pathways(ProgramID: int) -> list:
    """
    Returns: a list of dicts of NOC occupation pathways linked to the given program, empty list otherwise
    Args:
        ProgramID: int -> the ID of the program to get NOC pathways for
    """
    try:
        
        return DataUtils.Get_Program_To_Occupation_Data(ProgramID)


    except Exception as e:
        logger.exception(f"[{e}]")
        return []
#endregion


#region [NOC History Analysis]

def Get_NOC_History(NOC_GroupingID, provinceID=35, DGUID='2021A000235'):
    """
    Returns: a dict with 'PROV' and 'ER' keys containing provincial labour history and economic region data, empty dict on failure
    Args:
        NOC_GroupingID: int => the NOC grouping ID to pull history for
        provinceID: int => the province ID, defaults to 35 (Ontario)
        DGUID: str => the dissemination geo unique ID for the region, defaults to '2021A000235'
    """
    try:
        
        return DataUtils.Get_NOC_Historical(NOC_GroupingID, provinceID, DGUID)

    except Exception as e:
        logger.exception(f"[{e}]")
        return {}
#endregion

#region [Forecast Retrieval]

def Get_Forecast_History(provinceid: int, noc_groupingid: int) -> dict:
    """
    Returns: a dict with 'PROV' and 'ALL' keys containing provincial and all-province forecast data, empty dict on failure
    Args:
        provinceid: int => the ID of the province to get the forecast for
        noc_groupingid: int => the NOC grouping ID to get forecasts for
    """
    try:

        return DataUtils.Get_Forecast_Data(provinceid=provinceid, noc_groupingid=noc_groupingid)

    except Exception as e:
        logger.exception(f"[{e}]")
        return {}
#endregion

#region [Trend Analysis Data]

def Get_Trend_Analysis_Data(provinceid, month, quarter):
    """
    Returns: a dict with 'FullSet', 'AnalysisSet', and 'ClusterDict' for the given province, month, and quarter, empty dict on failure
    Args:
        provinceid: int -> the ID of the province to generate trend analysis for
        month: int -> the month number to use in the analysis, ex. 3 for March
        quarter: int -> the quarter number to use in the analysis, ex. 1 for Q1
    """
    try:

        return DataUtils.Generate_Processed_Clustered_NOC_Sets(provinceid=provinceid, quarter=quarter, month=month)

    except Exception as e:
        logger.exception(f"[{e}]")
        return {}
#endregion

