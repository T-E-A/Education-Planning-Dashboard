import httpx
import logging
from AIRequests.AIRequestsRoutes import AI_Request_API_Routes as Routes

logger = logging.getLogger(__name__)

#region [Generic Request]
def Make_Request(url: str, method: str = "GET", params: dict = None, json: dict = None):
    try:
        logger.info(f"Requesting URL: {url} | Method: {method}")

        timeout = httpx.Timeout(
            connect=10.0,   # time to establish connection
            read=4000.0,     # time to wait for response (IMPORTANT)
            write=10.0,
            pool=10.0
        )

        with httpx.Client(timeout=timeout) as client:
            if method.upper() == "GET":
                response = client.get(url, params=params)
            elif method.upper() == "POST":
                response = client.post(url, json=json)
            else:
                raise ValueError(f"Unsupported method: {method}")

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

    return {'answer': 'Unable to Provide an Answer due to Application System Issues'}
#endregion

def Ask_For_University_Budge_Match(params):
    
    return Make_Request(
            url=Routes.GET_FEE_MATCH.url,
            method="POST",
            params=params,
            json=params,
            )

def Ask_AI_Service_For_Budget_Analysis(params):
    return Make_Request(
        url=Routes.GET_BUDGET_ANALYSIS.url,
        method="POST",
        params=params,
        json=params
    )

def Ask_AI_Service_For_Income_Distribution_Analysis(params):
    return Make_Request(
        url=Routes.GET_INCOME_DISTRIBUTION_ANALYSIS.url,
        method="POST",
        params=params,
        json=params
    )

def Ask_Pathways_Agent(params):
    return Make_Request(
        url=Routes.PATHWAYS_AGENT.url,
        method="POST",
        params=params,
        json=params,
    )

def Ask_ChatBot(params):
    return Make_Request(
        url=Routes.CHAT_BOT.url,
        method="POST",
        params=params,
        json=params,
    )

def Ask_For_Forecast_Analysis(params):
    return Make_Request(
        url=Routes.GET_FORECAST_ANALYSIS.url,
        method="POST",
        params=params,
        json=params,

    )

def Ask_For_Cluster_Quarterly_Analysis(params):
    return Make_Request(
        url=Routes.ASK_QUARTERLY_ANALYSIS.url,
        method="POST",
        params=params,
        json=params,

    )

def Ask_Match_Maker_Agent(params):
    return Make_Request(
        url=Routes.ASK_MATCH_MAKER.url,
        method="POST",
        params=params,
        json=params
    )
