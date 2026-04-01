from enum import Enum
import os


BASE_URI = os.getenv("AI_SERVICE_URI", "http://127.0.0.1:8010/")

class AI_Request_API_Routes(str, Enum):
    HEALTH = "health/"
    ROOT = ""
    ASK_MATCH_MAKER = "ask_match_maker_agent/"
    QUERY_CHATBOT = "query_chatbot/"
    GET_CHAT_HISTORY = "get_chat_history/"
    ASK_QUARTERLY_ANALYSIS = "ask_quarterly_agent_analysis/"
    GET_FEE_MATCH = "ask_for_unversity_fee_match/"
    GET_BUDGET_ANALYSIS = "ask_budget_analysis_agent/"
    GET_INCOME_DISTRIBUTION_ANALYSIS = "ask_income_distribution_agent/"
    PATHWAYS_AGENT = "ask_pathways_agent/"
    CHAT_BOT ="query_chatbot/"
    GET_FORECAST_ANALYSIS = "ask_forecast_analysis/"

    @property
    def url(self) -> str:
        """Return the full URL for this route."""
        return f"{BASE_URI}{self.value}"