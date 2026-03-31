from MainService import ProcessingServiceSystem as ProcessorObj
from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import logging
import os

#region [Setting Logger]
logger = logging.getLogger()
#endregion

#region [Requests]

class ProgramRelatedRequest(BaseModel):
    ProgramID: int

class NOCGroupHistorical(BaseModel):
    NOC_GroupingID: int
    provinceid: int
    DGUID: str

class NOCGroupForecastRequest(BaseModel):
    NOC_GroupingID: int
    provinceid : int

class TrendAnalysisDataRequest(BaseModel):
    provinceid: int
    month: int
    quarter: int

#endregion



def Generate_App() -> FastAPI:
    """
    Returns: a configured FastAPI app instance with all routes registered
    """
    try:
        ProcessorObj.Load_All_Options_Dicts()

    except:
        logger.info(['Django API Service is unavailable -> tearing down service'])
        exit()


    app = FastAPI(title="Education Planning Dashboard: [Data Processing Service]")

    @app.get("/health/")
    def health_check(): 
        """
        Returns: a simple ok status to confirm the service is alive
        Args: None
        """
        return {"status": "ok"}

    @app.get("/")
    def root():
        """
        Returns: a welcome message and a directory of all available endpoints
        """
        try:

            return {"Welcome": "Education Planning Dashboard: [Data Processing Service] is running",
                "Directory": {
                    "Service Check": "/service_check/",
                    "Get Options": "/get_options_dicts/",
                    "Get KPI Data": "/get_kpi_data/",
                    "Get Program to NOC Pathways": "/get_program_to_noc_pathways/",
                    "Get NOC Grouping Historical Data": "/get_noc_group_historical/",
                    "Get NOC Grouping Provincial Forecast Data": "/get_noc_grouping_provincial_forecast/",
                    "Get Clustered Series for a Province": "/get_trend_analysis_set/"
                    }
                
                    }

        except Exception as e:
            logger.exception(f'[{e}]')



    #region [Service Check] 
    @app.get("/service_check/", summary="Check if all services are running", response_description="Status of all services")
    def service_check() -> JSONResponse:
        """
        Returns: JSONResponse with HTTP 200 if all services are up, 503 if any are down, 500 on exception
        """
        try:
            services_ok = ProcessorObj.Check_Services_Heartbeat()
            if services_ok:
                response_content = {
                    "status": status.HTTP_200_OK,
                    "services": {
                        "Data Processing Service": "Running",
                        "Django API Service": "Running"
                    },
                    "message": "All services are running"
                }
                return JSONResponse(status_code=status.HTTP_200_OK, content=response_content)

            else:
                # if heartbeat returns False
                response_content = {
                    "status": status.HTTP_503_SERVICE_UNAVAILABLE,
                    "services": {
                        "Data Processing Service": "Not Responding",
                        "Django API Service": "Not Responding"
                    },
                    "message": "Some services may be down"
                }
                return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=response_content)

        except Exception as e:
            logger.exception(f"Service check failed: {e}")
            response_content = {
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "services": {
                    "Data Processing Service": "Running",
                    "Django API Service": f"Error when launching => [{e}]"
                },
                "message": "Service check encountered an exception"
            }
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response_content)
#endregion

#region [GET Methods]
    @app.get("/get_options_dicts/")
    def Get_Options_Dicts() -> dict:
        """
        Returns: a dict of all available options/dropdowns used across the dashboard
        """
        try:
        
            return ProcessorObj.Options_Directory

        except Exception as e:
            logger.exception(f'[{e}]')

    @app.get("/get_kpi_data/")
    def Get_KPI_Data() -> dict:
        """
        Returns: a dict of KPI data for the dashboard, empty dict on failure
        Args: none
        """
        try:
        
            return ProcessorObj.Load_All_KPI_Data()

        except Exception as e:
            logger.exception(f'[{e}]')
            return {}

    @app.get("/get_program_to_noc_pathways/")
    def Get_Program_To_NOC_Pathways(request: ProgramRelatedRequest = Depends()) -> list:
        """
        Returns: a list of NOC pathways linked to the given program, empty list on failure
        Args:
            request = {
                'ProgramID': int => the ID of the program to look up
            }
        """
        try:
            ProgramID = int(request.ProgramID)
            return ProcessorObj.Get_Program_To_NOC_Pathways(ProgramID=ProgramID)

        except Exception as e:
            logger.exception(f'[{e}]')
            return []

    @app.get("/get_noc_group_historical/")
    def Get_NOC_Group_Historical(request: NOCGroupHistorical = Depends()) -> dict:
        """
        Returns: a dict of historical labour market data for the given NOC group and region, empty dict on failure
        Args:
            request = {
                'NOC_GroupingID': int --> the NOC grouping ID,
                'provinceid': int --> the province ID,
                'DGUID': str --> the dissemination geography unique ID for the region; used to uniquely identify and link various geo locations
            }
        """
        try:
        
            NOC_GroupingID = request.NOC_GroupingID
            provinceid = request.provinceid
            DGUID = request.DGUID

            return ProcessorObj.Get_NOC_History(NOC_GroupingID, provinceid, DGUID)

        except Exception as e:
            logger.exception(f'[{e}]')
            return {}

    @app.get("/get_noc_grouping_provincial_forecast/")
    def Get_NOC_Group_Provincial_Forecast(request: NOCGroupForecastRequest = Depends()) -> dict:
        """
        Returns: a dict of forecasted labour data for the NOC group in the given province, empty dict on failure
        Args:
            request = {
                'NOC_GroupingID': int => the NOC grouping ID,
                'provinceid': int => the province ID
            }
        """
        try:
        
            NOC_GroupingID = request.NOC_GroupingID
            provinceid = request.provinceid

            return ProcessorObj.Get_Forecast_History(provinceid=provinceid, noc_groupingid=NOC_GroupingID)

        except Exception as e:
            logger.exception(f'[{e}]')
            return {}

    @app.get("/get_trend_analysis_set/")
    def Get_Trend_Analysis_Set(request: TrendAnalysisDataRequest = Depends()) -> dict:
        """
        Returns: a dict of clustered trend series for the given province, month, and quarter, empty dict on failure
        Args:
            request = {
                'provinceid': int => the province ID,
                'month': int => the month number, ex. 3 for March,
                'quarter': int => the quarter number, ex. 1 for Q1
            }
        """

        try:
        
            provinceid = request.provinceid
            month = request.month
            quarter = request.quarter

            return ProcessorObj.Get_Trend_Analysis_Data(provinceid=provinceid, month=month, quarter=quarter)

        except Exception as e:
            logger.exception(f'[{e}]')
            return {}
    
    return app

app = Generate_App()
