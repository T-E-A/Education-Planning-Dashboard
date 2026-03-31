from Agents import (JobDescriptor, 
                    ChatAssistant, 
                    QuarterlyAnalysisAgent, 
                    SummarizeBudgeAgent, 
                    IncomeDistAgent, 
                    PathwaysAgents,
                    ForecastAnalysisAgent)

from MLHelpers import MatchMaker, DomesticFeeMatcher, InternationalFeeMatcher
from RetrievalHelpers import Retriever
import logging
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver
import inspect 

logger = logging.getLogger(__name__)


class AgentOrchestrator():
    def __init__(self):
        self.RetrieverObj = Retriever.Retriever()
        self.MatchMakerObj = MatchMaker.Matcher()
        self.DomesticFeeMatcherObj = DomesticFeeMatcher.DomesticFeeMatcher()
        self.InternationalFeeMatcherObj = InternationalFeeMatcher.InternationalFeeMatcher()
        self.ChatBotObj = ChatAssistant.ChatAgent()
        self.QuarterlyAnalysisObj = QuarterlyAnalysisAgent.QuarterlyAnalyzer()
        self.BudgeAgent = SummarizeBudgeAgent.BudgetAnalyzer()
        

        pathways_memory = InMemorySaver()

        self.IncomeDistAgentObj = IncomeDistAgent.IncomeAnalysisAgent(memory=pathways_memory)
        self.PathWaysAgentObj = PathwaysAgents.CareerPathwaysAgent(memory=pathways_memory)

        self.ForecastAnalysisAgentsObj = ForecastAnalysisAgent.ForecastAnalysisAgents(memory=pathways_memory)
        

    def Ask_For_Income_Distribution_Analysis(self, params):
        '''
            Returns: The chatbot's response to the income distribution query
            Args:
                params = {
                    'session_id': str => the session id to use for the agent's memory (optional, defaults to 'default')
                    'data': dict => the data to be analyzed by the agent, expected to contain necessary information for income distribution analysis
                }
        '''
        try:

            session_id = params.get('session_id', None)
            data = params.get('data', {})

            response = self.IncomeDistAgentObj.Ask_Agent(Data=data, session_id=session_id)

            
            return response
        except Exception as e:
            logger.exception(e)
            return "I cannot provide an income distribution analysis at this time."

    def Ask_For_Fee_Match(self, params):
        '''
        Returns: A list of univeristy ids that were match, ex. [2.0, 10.0]
        Args:
            params = {
                'StudentType': int type => 1 for domestic, 2 for interational 
                'Vector': list[float] => the fees vector, ex. [2450.0, 500.3]
             }
        '''
        
        try:

            StudentType = params.get('StudentType',-1)
            Vector = params.get('Vector',None)

            if StudentType == 1:
                if Vector:
                    return self.DomesticFeeMatcherObj.Get_Universities(user_input=Vector)
                return []
            elif StudentType == 2:
                if Vector:
                    return self.InternationalFeeMatcherObj.Get_Universities(user_input=Vector)
                return []
            else:
                return []


        except Exception as e:
            logger.exception(e)
            return []     
    
    def Ask_Match_Making_Agent(self, params):
        '''
            Returns: A summary of matched Occupations based on the inputed user vector.
            Args:
                params = {
                    'RetrievedDescriptions': list[str] => a list of relevant job descriptions retrieved based on the matched occupations, providing context for the agent to generate summaries.
                    'MatchedList': list[str] => a list of occupation titles that were identified as matches
                }
        '''
        
        try:
            
            user_input_vector = params['user_input_vector']
            session_id = params['session_id']

            MatchedList = self.MatchMakerObj.Get_Jobs(user_input_vector)
            MatchedListString = ", ".join(MatchedList)
            
            RetrievedDescriptions = self.RetrieverObj.Query(MatchedListString, 
                                                            n_results=9, 
                                                            meta_filter={"content":"NOC"})
            
            DescriptorObj = JobDescriptor.Descriptor()

            params = {
                'Context': RetrievedDescriptions,
                'MatchedList': MatchedList
            }

            Job_Summaries = DescriptorObj.Describe(params=params)

            print(f"Asking Pathways Agent Now")
            PathwayAgentResponse = self.PathWaysAgentObj.Ask_Agent(docs=Job_Summaries, 
                                                                   query="Give a quick 3 sentence summary of which jobs require the lowest education credential and which jobs require the highest",
                                                                   session_id=session_id
                                                                   )

            response = "## 🎯 Matches\n\n"

            for match in Job_Summaries['Matches']:
                response += f"### {match['Occupation Title']}\n\n"

                response += f"**Description**  \n"
                response += f"{match['Description']}\n\n"

                response += f"**Education / Credentials Required**  \n"
                response += f"{match['Education/Credentials Required']}\n\n"

                response += "---\n\n"   # divider line between matches
            
            print(f"Appending Pathways Agent Response")
            response += f"### Summary\n"
            response += f"{PathwayAgentResponse}"
            
            del DescriptorObj

            return response
        
        except Exception as e:
            logger.exception(f'{e}')
            return f"I cannot produce an answer due to system error {e}"

    def Ask_Chat_Agent(self, params):
        '''
            Returns: The formatted chatbot's response to the user's query
            Args:
                params = {
                    '**params: see query_chatbot endpoint in app.py for details**'
                }
        '''
        
        try:

            user_query = params.get('user_query','')

            logger.info('Retrieving Context')
            context = self.RetrieverObj.Query(user_query)
            logger.info(f'Retrieved {len(context)} documents')

            params_extended = {
                **params,
                'context': context
            }

            response = self.ChatBotObj.Ask_Chat_Agent(params=params_extended)

            formatted = "\n**Answer**:\n"
            formatted += f"{response.answer}\n\n"
            formatted += "**Sources**:\n"

            for url in response.sources:
                formatted += f"\n{url}\n"

            return formatted

        
        except Exception as e:
            logger.exception(f'[{e}]')
            return f"I cannot answer this question due to system error => [{e}]"

    def Ask_Chat_Agent_For_History(self):
        '''
            Returns: The serialized conversation history for the specified session.
        '''
        
        try:
        
            History =  self.ChatBotObj.Serialize_Sessions()
            return History

        except Exception as e:
            print(f"{e}")
            logger.exception(f'[{e}]')
            return {f"{e}"}
    
    def Ask_Quarterly_Agent(self, params):
        '''
            Returns: The chatbot's response to the quarterly analysis query
        '''
        
        try:
            
            return self.QuarterlyAnalysisObj.Ask_Agent(params=params)

        except Exception as e:
            logger.exception(f'{e}')
    
    def Ask_Budget_Analysis_Agent(self, params):
        '''
            Returns: The chatbot's response to the budget analysis query
            Args:
                params = {
                    'session_id': str => the session id to use for the agent's memory (optional, defaults to 'default')
                    'data': dict => the data to be analyzed by the agent, expected to contain necessary information for budget analysis
                }
        '''
        
        try:

            session_id = params.get('session_id','default')

            
            response = self.BudgeAgent.Ask_Agent(params=params)

            
            
            return response

        except Exception as e:
            logger.exception(e)
            return "I cannot provide a budget analysis at this time."
    
    def Ask_Pathways_Agent(self, params):
        '''
            Returns: The chatbot's response to the careers pathways query
            Args:
                params = {
                    'session_id': str => the session id to use for the agent's memory (optional, defaults to 'default')
                    'query': str => the user's query for the pathways agent
                }
        '''
        
        try:
            
            session_id = params.get('session_id','default')
            Query = params.get('query', 'Do not answer this')

            if session_id:
                response = self.PathWaysAgentObj.Ask_Agent(docs=None, query=Query, session_id=session_id)
            
            return response

        except Exception as e:
            logger.exception(e)
            return "Pathways Agent Here! I cannot provide a message at the moment please contact AI Service Admin"
        
    def Ask_Forecast_Analysis_Agents(self, params):
        '''
            Returns: The chatbot's response to the forecast analysis query for the selected forecasts
            Args:
                params = {
                    'session_id': str => the session id to use for the agent's memory (optional, defaults to 'default')
                    'query': str => the user's query for the forecast analysis agent
                }
        '''
        method = inspect.currentframe().f_code.co_name
        try:
            logger.info(f"{method}()")

            response = self.ForecastAnalysisAgentsObj.Ask_Agents(params=params)

            return response

        except Exception as e:
            logger.exception(e)
            return "Unable to generate forecast analysis."


