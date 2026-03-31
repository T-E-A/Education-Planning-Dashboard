import MainService.AISystem as AISystem 
from fastapi import FastAPI
from pydantic import BaseModel
import json


class CompetencyList(BaseModel):
    compentency_list : list[int] 
    session_id: str

class QueryRequest(BaseModel):
    user_query: str
    session_id: str

class QuarterlyAnalysisRequest(BaseModel):
    AllSamples: dict
    Cluster: int

class FeeMatcherRequest(BaseModel):
    '''
    {
    'StudentType': int type => 1 for domestic, 2 for interational 
    'Vector': list[float] => the fees vector, ex. [2450.0, 500.3]
    }
    '''
    StudentType: int
    Vector: list[float]

class BudgetAnalysisRequest(BaseModel):
    Data: dict

class IncomeDistributionRequest(BaseModel):
    data: list
    session_id: str

class ForecastAnalysisRequest(BaseModel):
    session_id: str
    Evaluation_Data: list
    Future_Projections: list
    NOC_Occupation_Group: str


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
                    "Get Quarterly Cluster Analysis":"/ask_quarterly_agent_analysis/",
                    "Get Fee Matches":"/ask_for_unversity_fee_match/",
                    "Get Income Distribution Analysis":"/ask_income_distribution_agent/",
                    "Ask Pathways Agent": "/ask_pathways_agent/",
                    "Get Forecast Analysis":"/ask_forecast_analysis/",
                    
                }
                
                }


    @app.post('/ask_match_maker_agent/')
    def Query_Match_Making_Agent(request: CompetencyList):
        '''
            Returns: A summary of matched Occupations based on the inputed user vector.
            Args:
                params = {
                    'compentency_list': list[int] => each value of 1 to 5 represents the user's self-assessed competency in each category
                    'session_id': str => the user's session id to store the conversation history
                }
        '''
        try:
            params = {
                'user_input_vector': request.compentency_list,
                'session_id': request.session_id
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
    
    @app.post('/ask_for_unversity_fee_match/')
    def Get_University_Fee_Match(request: FeeMatcherRequest):

        '''
            Returns: A list of universities that match the user's fee requirementsand student type.
            Args: 
                params = {
                    'StudentType': int type => 1 for domestic, 2 for interational 
                    'Vector': list[float] => the fees vector, ex. [2450.0, 500.3]
                }
        '''
        try:
            
            params = {
                'StudentType': request.StudentType,
                'Vector':request.Vector
            }

            answer = AISystem.AskForFeeMatch(params=params)

            return answer

        except Exception as e:
            return []
    
    @app.post("/ask_budget_analysis_agent/")
    def Get_Budget_Analysis(request: BudgetAnalysisRequest):
        '''
            Returns: The chatbot's response to a budget analysis query based on the inputted data.
            Args:
                params = {
                    'Data': dict => a dictionary containing the relevant data for the budget analysis.
                }
        '''
        try:
        
            params = {
                'Data': request.Data
            }

            answer = AISystem.AskBudgetAgent(params=params)

            print(f"Sending this answer {answer}")

            return {'answer':answer}

            
        except Exception as e:
            return {'answer':f"I cannot answer this right now due to system error => {e}"}
    
    @app.post("/ask_income_distribution_agent/")
    def Get_Income_Distribution_Analysis(request: IncomeDistributionRequest):
        '''
            Returns: The chatbot's response to an income distribution analysis query based on the input parameters.
            Args:
                params = {
                    'data': list => a list of data points relevant to the income distribution analysis
                    'session_id': str => the user's session id to store the conversation history and maintain context for future interactions
                }
        '''
        try:
        
            params = {
                'data': request.data,
                'session_id': request.session_id
            }

            answer = AISystem.AskForIncomeDistributionAnalysis(params=params)


            return {'answer':answer}

            
        except Exception as e:
            return {'answer':f"I cannot provide an income distribution analysis at this time due to system error => {e}"}
    
    @app.post('/ask_pathways_agent/')
    def Ask_Pathways_Agent_Query(request: QueryRequest):
        '''
            Returns: The chatbot's response to a pathways agent query based on the user's input query and session history to repond with what career pathways may be available.
            Args:
                params = {
                    'user_query': str => the user's prompt to the pathways agent chatbot
                    'session_id': str => the unique identifier for the user's session, allowing the chatbot to maintain and track the confersation history and context across multiple interations.
                }
        '''
        try:
            
            params = {
                'query': request.user_query,
                'session_id': request.session_id
            }

            answer = AISystem.AskPathWaysAgent(params=params)

            return {'answer':answer}

        except Exception as e:
            return {'answer': f'I cannot provide a Pathways Agent request at the moment due to => {e}'}
    
    @app.post('/ask_forecast_analysis/')
    def Ask_Forecast_Analysis(request: ForecastAnalysisRequest):
        '''
            Returns: The chatbot's response to a forecast analysis query based on the user's input parameters, providing insights and analysis on future trends and projections.
            Args:
                params = {
                    'session_id': str => the unique identifier for the user's session, allowing the chatbot to maintain and track the confersation history and context across multiple interations.
                    'Evaluation_Data': list => a list of data points relevant to the evaluation of current trends and conditions in the relevant field or industry.
                    'Future_Projections': list => a list of data points or projections related to future trends and developments in the relevant field or industry.
                    'NOC_Occupation_Group': str => a string representing the specific NOC occupation group that the forecast analysis should focus on, allowing for more targeted and relevant insights.
                }
        '''
        
        try:
            
            params = {
                'session_id': request.session_id,
                'Evaluation_Data': request.Evaluation_Data,
                'Future_Projections':request.Future_Projections,
                'NOC_Occupation_Group':request.NOC_Occupation_Group
            }

            answer = AISystem.AskForForecastAnalysis(params=params)

            return {'answer':answer}

        except Exception as e:
            return {'answer': "Unable to generate the analysis, something was wrong with the request."}


    return app

    

    


app = Generate_App()