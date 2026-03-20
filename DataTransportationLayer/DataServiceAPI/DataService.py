# By: Tejas Kumar
# This module serves as a helper to make API calls to the DataLayer endpoints
# It defines functions and parameters to send to the API and returns the relevant information in the form of dataframes.
# This helps separate the data retrieval mechanism into a single module.

print("Importing Data Service API")
import pandas as pd
import polars as pl
import httpx
import os 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dp_Forecast_Data = pl.scan_parquet(f'{BASE_DIR}/DataServiceAPI/tempData/All_Forecasts.parquet')

base_uri = 'http://127.0.0.1:8000/api/'

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

# Generic function for making a request to the API given a formatted URL
def Make_Request(url: str):
    try:
        print(f"URL => {url}")
        response = client.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Request failed for {url}: {e}")
        return []

#region Request Functions

def RequestLatestKPIForProgram(ProgramID: int, Year=2020) -> pd.DataFrame:
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
    try:
        url_to_call = f"{base_uri}{api_routes[1]}/?programcategoryid={ProgramID}&universityid={UniversityID}"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestKPIForProgramAndUniversity(ProgramID={ProgramID}, UniversityID={UniversityID}) => {e}")
        return pd.DataFrame()

def RequestProgramCategories() -> pd.DataFrame:
    try:
        url_to_call = f"{base_uri}{api_routes[2]}/"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestProgramCategories => {e}")
        return pd.DataFrame()

def RequestNOCGroupingOptions() -> pd.DataFrame:
    try:
        url_to_call = f"{base_uri}{api_routes[5]}/"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestNOCGroupingOptions => {e}")
        return pd.DataFrame()

def RequestProgramNOCLinks(ProgramID: int) -> pd.DataFrame:
    try:
        url_to_call = f"{base_uri}{api_routes[3]}/?programid={ProgramID}"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestProgramNOCLinks(ProgramID={ProgramID}) => {e}")
        return pd.DataFrame()

def RequestNOCGroupLaborStatistics(DGUID: str, NOC_GroupingID: int) -> pd.DataFrame:
    try:
        url_to_call = f"{base_uri}{api_routes[4]}/?dguid={DGUID}&noc_groupingid={NOC_GroupingID}"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestNOCGroupLaborStatistics(DGUID={DGUID}, NOC_GroupingID={NOC_GroupingID}) => {e}")
        return pd.DataFrame()

def RequestEROptions(ProvinceID: int) -> pd.DataFrame:
    try:
        url_to_call = f"{base_uri}{api_routes[7]}/?provinceid={ProvinceID}"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestEROptions(ProvinceID={ProvinceID}) => {e}")
        return pd.DataFrame()

def RequestEconomicRegionEmploymentEstimate(NOC_GroupingID: int, ProvinceID: int) -> pd.DataFrame:
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
    try:
        url_to_call = f"{base_uri}{api_routes[8]}/"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"RequestProvince() => {e}")
        return pd.DataFrame()

#endregion



#region Temporary Functions 


# def Request_Provincial_NOC_Forecast(provinceID : int, noc_groupingid : int) -> pd.DataFrame:
#     try:
#         Data = dp_Forecast_Data.filter((pl.col('provinceid')==provinceID) & (pl.col('noc_groupingid')==noc_groupingid)).collect().to_pandas().sort_values(by='ds')
#         return Data
        

#     except Exception as e:
#         print(f"Request_Provincial_NOC_Forecast(provinceID : {provinceID}, noc_groupingid : {noc_groupingid}) => {e}")
#         return pd.DataFrame()
    
def Request_Provincial_NOC_Forecast(provinceID : int, noc_groupingid : int) -> pd.DataFrame:
    try:
        url_to_call = f"{base_uri}{api_routes[10]}/?provinceid={provinceID}&noc_groupingid={noc_groupingid}"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)
        

    except Exception as e:
        print(f"Request_Provincial_NOC_Forecast(provinceID : {provinceID}, noc_groupingid : {noc_groupingid}) => {e}")
        return pd.DataFrame()
    

# def Request_All_Province_NOC_Forecast(noc_groupingid : int) -> pd.DataFrame:
#     try: 
#         Data = dp_Forecast_Data.filter(pl.col('noc_groupingid')==noc_groupingid).group_by(['provinceid','year']).agg(
#             pl.col('yhat').sum().round(2).alias('Employment Forecast')
#         ).collect().to_pandas()

#         ProvinceData = RequestProvince()

#         Data = Data.merge(ProvinceData[['provinceid','province_shorthand']], how='left')

#         return Data
    
#     except Exception as e:
#         print(f"Request_All_Province_NOC_Forecast(noc_groupingid : {noc_groupingid})")
#         return pd.DataFrame()

def Request_All_Province_NOC_Forecast(noc_groupingid : int) -> pd.DataFrame:
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

#region Seasonal Decompostion Data Requests 
def RequestionSeasonalDecomp(provinceid):
    try:
        url_to_call = f"{base_uri}{api_routes[11]}/?provinceid={provinceid}"
        data = Make_Request(url=url_to_call)
        return pd.DataFrame(data)

    except Exception as e:
        print(f"RequestSeasonalDecompo() => {e}")
        return pd.DataFrame()


#endregion

#region Post Functions

def Post_Prediction_Cache(payload: dict) -> dict:
    try:
        url_to_call = f"{base_uri}{api_routes[10]}/"
        response = client.post(url_to_call, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Post_Prediction_Cache => {e}")
        return {}

#endregion