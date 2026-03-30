from MainService.AI_Orchestration import AgentOrchestrator
import logging

logger = logging.getLogger(__name__)

#region [AI Orchestration]

Orchestrator = AgentOrchestrator()

#endregion


def DescribeMatchedOccupations(params):
    '''
        Returns: The orchestrated responce from AI_Orchestration.py's Ask_Match_Making_Agent function
    '''
    try:
        
        return Orchestrator.Ask_Match_Making_Agent(params)

    except Exception as e:
        logger.exception(f'{e}')
        raise 

def AskChatAgent(params):
    '''
        Returns: The orchestrated responce from AI_Orchestration.py's Ask_Chat_Agent function
    '''
    try:
        
        return Orchestrator.Ask_Chat_Agent(params)

    except Exception as e:
        logger.exception(f'{e}')
        raise

def GetChatHistory():
    '''
        Returns: The orchestrated responce from AI_Orchestration.py's Ask_Chat_Agent_For_History function
    '''
    try:
        
        return Orchestrator.Ask_Chat_Agent_For_History()

    except Exception as e:
        logger.exception(f'{e}')
        raise

def AskQuarterlyAgent(params):
    '''
        Returns: The orchestrated responce from AI_Orchestration.py's Ask_Quarterly_Agent function
    '''
    try:

        return Orchestrator.Ask_Quarterly_Agent(params=params)

    except Exception as e:
        logger.exception(f'{e}')
        raise