from enum import Enum
import os


BASE_URI = os.getenv("PROCESSING_SERVICE_URI", "http://127.0.0.1:8012/")

class Data_Processing_API_Routes(str, Enum):
    SERVICE_CHECK = "service_check/"
    GET_OPTIONS = "get_options_dicts/"
    GET_KPI_DATA = "get_kpi_data/"
    PROGRAM_TO_NOC = "get_program_to_noc_pathways/"
    NOC_GROUP_HISTORICAL = "get_noc_group_historical/"
    NOC_GROUP_PROV_FORECAST = "get_noc_grouping_provincial_forecast/"
    PROVINCE_CLUSTERED_SERIES = "get_trend_analysis_set/"

    @property
    def url(self) -> str:
        """Return the full URL for this route."""
        return f"{BASE_URI}{self.value}"