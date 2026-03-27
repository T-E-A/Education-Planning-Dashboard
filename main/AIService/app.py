import MainService.AISystem as AISystem 
from fastapi import FastAPI
from pydantic import BaseModel
import json


class CompetencyList(BaseModel):
    compentency_list : list[int] 

class QueryRequest(BaseModel):
    user_query: str
    session_id: str

class QuarterlyAnalysisRequest(BaseModel):
    AllSamples: dict
    Cluster: int

def Generate_App() -> FastAPI:
    app = FastAPI(title="Eduction Planning Dashboard: [AI Service Running]")

    @app.get("/health/")
    def health_check():
        return {"status": "ok"}

    @app.get("/")
    def root():
        return {"Welcome": "Education Planning Dashboard: [AI Service] is running",
                "Directory": {
                    "Ask Match Maker Agent": "/ask_match_maker_agent/",
                    "Ask Chat Bot a Question": "/query_chatbot/",
                    "Get Chat History": "/get_chat_history/",
                    "Get Quarterly Cluster Analysis":"/ask_quarterly_agent_analysis/"
                    
                }
                
                }


    @app.post('/ask_match_maker_agent/')
    def Query_Match_Making_Agent(request: CompetencyList):
        '''
            Returns: A summary of matched Occupations based on the inputed user vector.
            Args:
                params = {
                    'compentency_list': list[int] => each value of 1 to 5 represents the user's self-assessed competency in each category
                }
        '''
        try:
            params = {
                'user_input_vector': request.compentency_list
            }
            answer = AISystem.DescribeMatchedOccupations(params=params)

            return {'answer':answer}
    
        except Exception as e:
            return {'answer': f'I cannot provide job matches due to system error [{e}]'}


    @app.post("/query_chatbot/")
    def Query_Chat_Bot(request: QueryRequest):
        '''
            Returns: The chatbot's response to the user's query
            Args:
                params = {
                    'user_query': str => the user's prompt to the chatbot
                    'session_id': str => the unique identifier for the user's session, allowing the chatbot to maintain and track the confersation history and context across multiple interations.
                }
        '''
        try:
            params = {
                'user_query': request.user_query,
                'session_id': request.session_id
            }

            answer = AISystem.AskChatAgent(params=params)
    
            return {
                "answer": answer,
            }
        except Exception as e:
            return {
                "answer": f"I cannot answer that question due to system error [{e}]"
            }

    @app.get('/get_chat_history/')
    def Get_Chat_History():
        '''
            Returns: The entire conversation history of the current session, including all user queries and chatbot responses
        '''
        
        try:
        
            return AISystem.GetChatHistory()

        except Exception as e:
            return f"Error getting history => {e}"
    
    @app.post("/ask_quarterly_agent_analysis/")
    def Get_Quarterly_Analysis(request: QuarterlyAnalysisRequest):
        '''
            Returns: The chatbot's response to the user's query
            Args:
                params = {
                    'AllSamples': dict => a dictionary containing all the data samples for the quarter, where each key is a unique identifier for a sample and each value is the corresponding data for that sample.
                    'Cluster': int => the specific cluster number for which the user wants to obtain analysis and insights.
                }
        '''
        
        try:
            params = {
                'AllSamples':request.AllSamples,
                'Cluster': request.Cluster
            }

            answer = AISystem.AskQuarterlyAgent(params=params)

            return {
                "answer": answer,
            }

        except Exception as e:
            return 
    
    return app


app = Generate_App()