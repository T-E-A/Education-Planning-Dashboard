from MainService.AI_Orchestration import AgentOrchestrator
import logging

logger = logging.getLogger(__name__)

#region [AI Orchestration]

Orchestrator = AgentOrchestrator()

#endregion


def DescribeMatchedOccupations(params):
    '''
        Returns: A list of matched occupations based on the input parameters.
        Args:
            Args:
                params = {
                    'user_input_vector': list[int] => the user's input vector representing their skills, preferences, or other relevant attributes for job matching.
                    'session_id': str => the session id to use for the agent's memory (optional, defaults to 'default')
                    'RetrievedDescriptions': list[str] => a list of relevant job descriptions retrieved based on the matched occupations, providing context for the agent to generate summaries.
                    'MatchedList': list[str] => a list of occupation titles that were identified as matches
                }
    '''
    try:
        
        return Orchestrator.Ask_Match_Making_Agent(params)

    except Exception as e:
        logger.exception(f'{e}')
        raise 

def AskChatAgent(params):
    '''
        Returns: The formatted chatbot's response to the user's query
        Args:
            params = {
                'user_query': str => the user's input query for the chatbot
                }
    '''
    
    try:
        
        return Orchestrator.Ask_Chat_Agent(params)

    except Exception as e:
        logger.exception(f'{e}')
        raise

def GetChatHistory():
    '''
        Returns: The serialized conversation history for the specified session.
    '''
    try:
        
        return Orchestrator.Ask_Chat_Agent_For_History()

    except Exception as e:
        logger.exception(f'{e}')
        raise

def AskQuarterlyAgent(params):
    '''
        Returns: The chatbot's response to the quarterly analysis query
    '''
    try:

        return Orchestrator.Ask_Quarterly_Agent(params=params)

    except Exception as e:
        logger.exception(f'{e}')
        raise

def AskForFeeMatch(params):
    try:

        '''
        Returns: A list of univeristy ids that were match, ex. [2.0, 10.0]
        Args:
            params = {
                'StudentType': int type => 1 for domestic, 2 for interational 
                'Vector': list[float] => the fees vector, ex. [2450.0, 500.3]
             }
        '''
        
        return Orchestrator.Ask_For_Fee_Match(params=params)

    except Exception as e:
        logger.exception(e)
        raise

def AskBudgetAgent(params):
    try:
        '''
        Returns: A string object that is a budget analysis
        Args:
            params = {
                'Data': A nested dictionary of data.
             }
        '''
        return Orchestrator.Ask_Budget_Analysis_Agent(params=params)

    except Exception as e:
        logger.exception(e)
        raise

def AskForIncomeDistributionAnalysis(params):
    try:
        '''
        Returns: A string object that is an income distribution analysis
        Args:
            params = {
                'data': A json dict of income stats.
                'session_id': Session ID for Pathways page.
             }
        '''
        return Orchestrator.Ask_For_Income_Distribution_Analysis(params=params)

    except Exception as e:
        logger.exception(e)
        raise

def AskPathWaysAgent(params):
    try:
        '''
        Returns: A string object that is an income distribution analysis
        Args:
            params = {
                'query': A json dict of income stats.
                'session_id': Session ID for Pathways page.
             }
        '''
        return Orchestrator.Ask_Pathways_Agent(params=params)

    except Exception as e:
        logger.exception(e)
        raise

def AskForForecastAnalysis(params):
    try:
        '''
        Returns: A string summary of a forecast. 
        Args: 
            params = {

                session_id: uuid of the session,
                Evaluation_Data: list[dict] of forecast evaluation data
                Future_Projections: list[dict] of future projections 
                NOC_Occupation_Group: name of the NOC Occupation

            }
        
        '''

        return Orchestrator.Ask_Forecast_Analysis_Agents(params=params)

    except Exception as e:
        logger.exception(e)
        raise