import httpx
import logging
from DataProcessingRequests.DataProcessingRoutes import Data_Processing_API_Routes as Routes

logger = logging.getLogger(__name__)

#region [Generic Request]
def Make_Request(url: str, params: dict = None):
    try:
        logger.info(f"Requesting URL: {url} | Params: {params}")
        print(f"Requesting URL: {url} | Params: {params}")

        with httpx.Client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logger.exception(f"Request failed: {e}")
        print(f"[RequestError] {e}")
    except httpx.HTTPStatusError as e:
        logger.exception(f"HTTP error: {e}")
        print(f"[HTTPStatusError] {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"[Exception] {e}")
    return []
#endregion

#region [Service_Check]
def Service_Check():
    return Make_Request(url=Routes.SERVICE_CHECK.url)
#endregion

#region [Get_Options_Dicts]
def Get_Options_Dict():
    return Make_Request(url=Routes.GET_OPTIONS.url)
#endregion 

#region [Get_KPI_Data]
def Get_KPI_Data():
    return Make_Request(url=Routes.GET_KPI_DATA.url)
#endregion

#region [PROGRAM_TO_NOC]
def Get_Program_To_NOC_Data(ProgramID: int):
    return Make_Request(url=Routes.PROGRAM_TO_NOC.url, params={"ProgramID": ProgramID})
#endregion 

#region [NOC_GROUP_HISTORICAL]
def Get_NOC_Historical(NOC_GroupingID: int, provinceid: int, DGUID: str):
    return Make_Request(
        url=Routes.NOC_GROUP_HISTORICAL.url,
        params={"NOC_GroupingID": NOC_GroupingID, "provinceid": provinceid, "DGUID": DGUID}
    )
#endregion

#region [NOC_GROUP_PROV_FORECAST]
def Get_NOC_Forecast(NOC_GroupingID: int, provinceid: int):
    return Make_Request(
        url=Routes.NOC_GROUP_PROV_FORECAST.url, 
        params={"NOC_GroupingID": NOC_GroupingID, "provinceid": provinceid}
    )
#endregion

#region [PROVINCE_CLUSTERED_SERIES]
def Get_Province_Clustered_Series(provinceid: int, month: int, quarter: int):
    return Make_Request(
        url=Routes.PROVINCE_CLUSTERED_SERIES.url, 
        params={"provinceid": provinceid, "month": month, "quarter": quarter}
    )
#endregion
