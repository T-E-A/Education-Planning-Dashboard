from Agents import JobDescriptor, ChatAssistant, QuarterlyAnalysisAgent
from MLHelpers import MatchMaker
from RetrievalHelpers import Retriever
import logging

logger = logging.getLogger(__name__)


class AgentOrchestrator():
    def __init__(self):
        self.RetrieverObj = Retriever.Retriever()
        self.MatchMakerObj = MatchMaker.Matcher()
        self.ChatBotObj = ChatAssistant.ChatAgent()
        self.QuarterlyAnalysisObj = QuarterlyAnalysisAgent.QuarterlyAnalyzer()
        
    
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

            response = "## 🎯 Matches\n\n"

            for match in Job_Summaries['Matches']:
                response += f"### {match['Occupation Title']}\n\n"

                response += f"**Description**  \n"
                response += f"{match['Description']}\n\n"

                response += f"**Education / Credentials Required**  \n"
                response += f"{match['Education/Credentials Required']}\n\n"

                response += "---\n\n"   # divider line between matches
            
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

            context = self.RetrieverObj.Query(user_query)

            params_extended = {
                **params,
                'context': context
            }

            response = self.ChatBotObj.Ask_Chat_Agent(params=params_extended)

            formatted = "\n**Answer**:\n"
            formatted += f"{response.answer}\n"
            formatted += "**Sources**:\n"

            for url in response.sources:
                formatted += f"{url}\n"

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
            logger.exception(f['e'])


