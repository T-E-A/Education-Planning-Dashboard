import pandas as pd
import polars as pl
import httpx
import os 
import logging
import time

logger = logging.getLogger(__name__)

# Base URI for the Django API, defaults to localhost if env variable is not set 
base_uri = os.getenv("BASE_URI", "http://127.0.0.1:8000/api/")

# base_uri = 'http://127.0.0.1:8000/api/'

print(f"BASE URI for Data Processor Container => {base_uri}")

# maps route IDs to their corresponding API endpoint names
api_routes = {
    1: 'program_university_kpi_latest',
    2: 'program_category',
    3: 'program_noc_link',
    4: 'provincial_noc_group_labor_statistic',
    5: 'noc_grouping',
    6: 'economic_region_employment_estimate',
    7: 'economicregion',
    8: 'province',
    9: 'university',
    10: 'prediction_cache',
    11: 'seasonal_decomposition'
}

# Instantiating a synchronous client with 120s timeout
client = httpx.Client(timeout=500.0)

def Check_Heartbeat(retries: int = 0,maxRetries: int = 20, delay: float = 5.0):
    """
    Returns: 1 if the Django API is reachable, 0 if it fails after all retries
    Args:
        retries: int --> current retry attempt, starts at 0
        maxRetries: int --> max number of retries before giving up, default is 20
        delay: float --> seconds to wait between retries, default is 5.0
    """
    try:
        response = client.get(base_uri)

        logger.info(f"Attempting to connect to [Django API Service is available]: Trial {retries}")
        if response.status_code == 200:
            logger.info('Education Planning Dashboard: [Django API Service is available]')
            return 1
        else:
            logger.info('Education Planning Dashboard: [Django API Service is unavailable]')
            logger.info('Retrying for Connection')
        
        retries = 0
        if retries < maxRetries:
            time.sleep(delay)
            retries += 1
            Check_Heartbeat(retries=retries)
        else:
            logger.info(f'Could not Connect to [Djang API Service] after {retries}')
            return 0
        
    except Exception as e:
        logger.exception(f'[{e}]')
        return 0


# Generic function for making a request to the API given a formatted URL
def Make_Request(url: str):
    """
    Returns: the JSON response from the API as a list or dict, empty list on failure
    Args:
        url: str => the full URL to send the GET request to
    """
    try:
        logger.info(f"URL => {url}")
        response = client.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Request failed for {url}: {e}")
        return []

#region Request Functions

def RequestUniversities():
    """
    Returns: a DataFrame of all universities
    Args: none
    """
    try:
        url_to_call = f"{base_uri}{api_routes[9]}/"
        data = Make_Request(url=url_to_call)

        df = pd.DataFrame(data)

        return df

    except Exception as e:
        return pd.DataFrame()

def RequestLatestKPIs(Year=2020) -> pd.DataFrame:
    """
    Returns: a DataFrame of the latest KPIs merged with university location data
    Args:
        Year: int --> the year to filter KPIs by, default year is 2020
    """
    try:
        url_to_call = f"{base_uri}{api_routes[1]}/?year={Year}"
        second_url_to_call = f"{base_uri}{api_routes[9]}/"
        data = Make_Request(url=url_to_call)
        uniData = Make_Request(url=second_url_to_call)

        df_KPI = pd.DataFrame(data)

        df_UniData = pd.DataFrame(uniData)
        df_UniData = df_UniData[['universityid','address','lat','lon']]

        df = df_UniData.merge(df_KPI, on='universityid')
        return df
    except Exception as e:
        print(f"RequestLatestKPIForProgram() => {e}")
        return pd.DataFrame()

def RequestAllKPIs():
    """
    Returns: a DataFrame of all KPIs across all years merged with university location data,
    Args: none
    """
    try:
        url_to_call = f"{base_uri}{api_routes[1]}/"
        second_url_to_call = f"{base_uri}{api_routes[9]}/"
        data = Make_Request(url=url_to_call)
        uniData = Make_Request(url=second_url_to_call)

        df_KPI = pd.DataFrame(data)

        df_UniData = pd.DataFrame(uniData)
        df_UniData = df_UniData[['universityid','address','lat','lon']]

        df = df_UniData.merge(df_KPI, on='universityid')
        return df
    
    except Exception as e:
        return pd.DataFrame()

def RequestLatestKPIForProgram(ProgramID: int, Year=2020) -> pd.DataFrame:
    """
    Returns: a DataFrame of the latest KPIs for a specific program merged with university location data, 
    Args:
        ProgramID: int --> the ID of the program to filter by
        Year: int --> the year to filter KPIs by, default is 2020
    """
    try:
        url_to_call = f"{base_uri}{api_routes[1]}/?programcategoryid={ProgramID}&year={Year}"
        second_url_to_call = f"{base_uri}{api_routes[9]}/"
        data = Make_Request(url=url_to_call)
        uniData = Make_Request(url=second_url_to_call)

        df_KPI = pd.DataFrame(data)

        df_UniData = pd.DataFrame(uniData)
        df_UniData = df_UniData[['universityid','address','lat','lon']]

        df = df_UniData.merge(df_KPI, on='universityid')
        return df
    except Exception as e:
        print(f"RequestLatestKPIForProgram(ProgramID={ProgramID}) => {e}")
        return pd.DataFrame()
    
def RequestKPIForProgram(ProgramID: int) -> pd.DataFrame:
    """
    Returns: a DataFrame of all KPIs for a specific program across all years merged with university location data,
    Args:
        ProgramID: int -> the ID of the program to filter by
    """
    try:
        url_to_call = f"{base_uri}{api_routes[1]}/?programcategoryid={ProgramID}"
        second_url_to_call = f"{base_uri}{api_routes[9]}/"
        data = Make_Request(url=url_to_call)
        uniData = Make_Request(url=second_url_to_call)
        data = Make_Request(url=url_to_call)

        df_KPI = pd.DataFrame(data)
        df_UniData = pd.DataFrame(uniData)
        df_UniData = df_UniData[['universityid','address','lat','lon']]


        df = df_UniData.merge(df_KPI, on='universityid')
        return df
    except Exception as e:
        print(f"RequestKPIForProgram(ProgramID={ProgramID}) => {e}")
        return pd.DataFrame()

def RequestKPIForProgramAndUniversity(ProgramID: int, UniversityID: int) -> pd.DataFrame:
    """
    Returns: a DataFrame of KPIs filtered by both program and university,
    Args:
        ProgramID: int => the ID of the program to filter by
        UniversityID: int => the ID of the university to filter by
    """
    try:
        url_to_call = f"{base_uri}{api_routes[1]}/?programcategoryid={ProgramID}&universityid={UniversityID}"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestKPIForProgramAndUniversity(ProgramID={ProgramID}, UniversityID={UniversityID}) => {e}")
        return pd.DataFrame()

def RequestProgramCategories() -> pd.DataFrame:
    """
    Returns: a DataFrame of all program categories, empty DataFrame on failure
    Args: none
    """
    try:
        url_to_call = f"{base_uri}{api_routes[2]}/"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestProgramCategories => {e}")
        return pd.DataFrame()

def RequestNOCGroupingOptions() -> pd.DataFrame:
    """
    Returns: a DataFrame of all NOC grouping options,
    Args: none
    """
    try:
        url_to_call = f"{base_uri}{api_routes[5]}/"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestNOCGroupingOptions => {e}")
        return pd.DataFrame()

def RequestProgramNOCLinks(ProgramID: int) -> pd.DataFrame:
    """
    Returns: a DataFrame of NOC codes linked to a specific program,
    Args:
        ProgramID: int => the ID of the program to look up NOC links for
    """
    try:
        url_to_call = f"{base_uri}{api_routes[3]}/?programid={ProgramID}"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestProgramNOCLinks(ProgramID={ProgramID}) => {e}")
        return pd.DataFrame()

def RequestNOCGroupLaborStatistics(DGUID: str, NOC_GroupingID: int) -> pd.DataFrame:
    """
    Returns: a DataFrame of labour statistics for a NOC group in a specific region,
    Args:
        DGUID: str --> the dissemination geo unique ID for the region
        NOC_GroupingID: int --> the NOC grouping ID to filter by
    """
    try:
        url_to_call = f"{base_uri}{api_routes[4]}/?dguid={DGUID}&noc_groupingid={NOC_GroupingID}"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestNOCGroupLaborStatistics(DGUID={DGUID}, NOC_GroupingID={NOC_GroupingID}) => {e}")
        return pd.DataFrame()

def RequestEROptions(ProvinceID: int) -> pd.DataFrame:
    """
    Returns: a DataFrame of economic regions for a given province,
    Args:
        ProvinceID: int => the ID of the province to get economic regions for
    """
    try:
        url_to_call = f"{base_uri}{api_routes[7]}/?provinceid={ProvinceID}"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestEROptions(ProvinceID={ProvinceID}) => {e}")
        return pd.DataFrame()

def RequestEconomicRegionEmploymentEstimate(NOC_GroupingID: int, ProvinceID: int) -> pd.DataFrame:
    """
    Returns: a DataFrame of employment estimates per economic region merged with region names, empty DataFrame on failure
    Args:
        NOC_GroupingID: int => the NOC grouping ID to filter employment estimates by
        ProvinceID: int => the province ID used to pull matching economic region names
    """
    try:
        url_to_call = f"{base_uri}{api_routes[6]}/?noc_groupingid={NOC_GroupingID}"
        data = Make_Request(url=url_to_call)
        df = pd.DataFrame(data).groupby('dguid').tail(1)

        df_ER_Names = RequestEROptions(ProvinceID=ProvinceID)
        df_ER_Names = df_ER_Names.rename(columns={'economicregion_dguid':'dguid'})[['dguid','economicregion']]

        df_Merge = df_ER_Names.merge(df, on='dguid', how='right')
        return df_Merge
    except Exception as e:
        print(f"RequestEconomicRegionEmploymentEstimate(NOC_GroupingID={NOC_GroupingID}) => {e}")
        return pd.DataFrame()

def RequestProvince() -> pd.DataFrame:
    """
    Returns: a DataFrame of all provinces, empty DataFrame on failure
    Args: none
    """
    try:
        url_to_call = f"{base_uri}{api_routes[8]}/"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestProvince() => {e}")
        return pd.DataFrame()

#endregion



#region [Forecast Requests]

def Request_Provincial_NOC_Forecast(provinceID : int, noc_groupingid : int) -> pd.DataFrame:
    """
    Returns: a DataFrame of forecasted employment data for a NOC group in a specific province, empty DataFrame on failure
    Args:
        provinceID: int => the ID of the province to filter by
        noc_groupingid: int => the NOC grouping ID to filter by
    """
    try:
        url_to_call = f"{base_uri}{api_routes[10]}/?provinceid={provinceID}&noc_groupingid={noc_groupingid}"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
        

    except Exception as e:
        print(f"Request_Provincial_NOC_Forecast(provinceID : {provinceID}, noc_groupingid : {noc_groupingid}) => {e}")
        return pd.DataFrame()
    

def Request_All_Province_NOC_Forecast(noc_groupingid : int) -> pd.DataFrame:
    """
    Returns: a DataFrame of yearly employment forecasts for a NOC group across all provinces,
    Args:
        noc_groupingid: int -> the NOC grouping ID to get forecasts for
    """
    try:
        url_to_call = f"{base_uri}{api_routes[10]}/?noc_groupingid={noc_groupingid}"
        second_url_to_call = f"{base_uri}{api_routes[8]}/"

        provData = Make_Request(url=second_url_to_call)
        df_prov = pd.DataFrame(provData)
        data = Make_Request(url=url_to_call)
        df = pd.DataFrame(data)
        df['datestamp'] = pd.to_datetime(df['datestamp'])
        df['year'] = df['datestamp'].dt.year
        df = pl.from_pandas(df)
        

        Data = df.group_by(['provinceid','year']).agg(
            pl.col('yhat').sum().round(2).alias('Employment Forecast')
        ).to_pandas()

        Data = Data.merge(df_prov, on='provinceid', how='left')
        print(f"Data =>\n{Data}")
        return Data
    
    except Exception as e:
        print(f"Request_All_Province_NOC_Forecast(noc_groupingid : {noc_groupingid})")
        return pd.DataFrame()

#endregion 

#region [Seasonal Decompostion Data Requests] 
def RequestionSeasonalDecomp(provinceid):
    """
    Returns: a DataFrame of seasonal decomposition data for a given province,
    Args:
        provinceid: int => the ID of the province to get seasonal decomposition data for
    """
    try:
        url_to_call = f"{base_uri}{api_routes[11]}/?provinceid={provinceid}"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)

    except Exception as e:
        print(f"RequestSeasonalDecompo() => {e}")
        return pd.DataFrame()
#endregion

#region [Post Functions]

def Post_Prediction_Cache(payload: dict) -> dict:
    """
    Returns: the API response as a dict after posting a prediction to the cache, empty dict on failure
    Args:
        payload: dict => the prediction data to post, ex. {'provinceid': 1, 'noc_groupingid': 2, 'yhat': 1500.0}
    """
    try:
        url_to_call = f"{base_uri}{api_routes[10]}/"
        response = client.post(url_to_call, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Post_Prediction_Cache => {e}")
        return {}

#endregion


