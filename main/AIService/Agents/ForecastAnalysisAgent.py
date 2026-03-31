import warnings
from pydantic import BaseModel, Field
from tqdm import tqdm
from langchain_core.prompts import PromptTemplate
import logging
import json
import time
from pydantic import BaseModel, Field
from enum import Enum
from Agents.ModelCatalogue import ModelEnum, CreateModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from langchain_core.runnables import RunnableParallel
import inspect

logger = logging.getLogger(__name__)


#region [Structure]
class ForecastSummary(BaseModel):
    province: str = Field(description='The name of the province.',alias="Province")
    confidence: float = Field(description="A numerical figure from 0 to 1, indicating how confident you are in the forecast, where 1 represents the highest confidence", alias='Confidence')
    strenghts: str = Field(description='A description of any strengths you see in the forecast, like high coverage or low overall error as expressed by mape.', alias='Strengths')

class ForecastSummaries(BaseModel):
    forecast_summaries : list[ForecastSummary] = Field(description='The list of forecast summaries', alias='Forecast Summaries') 

class FutureSummary(BaseModel):
    province: str = Field(description='The name of the province in shorthand', alias='Province')
    province_forecast_summary: str = Field(description='A 1 to 2 sentence summary of the future forecasts for the province',alias='Province Summary')

class FutureSummaries(BaseModel):
    future_summaries: list[FutureSummary] = Field(description='The list of future summaries for the provinces', alias='Future Summaries')

class FinalForecastInsight(BaseModel):
    summary: str = Field(description="A high-level summary of the overall forecast quality and outlook across provinces.")
    top_province: str = Field(description="The province that shows the most promise based on forecast trends and reliability.")
    bottom_province: str = Field(description="The province that shows the least promise or weakest outlook.")
    reasoning: str = Field(description="A concise explanation justifying the top and bottom province selections using both forecast quality and projected trends.")
#endregion


#region [Meta Data Descriptions]
Forecast_Meta_Data_Descriptions = {
    "r2": "R-squared (coefficient of determination) measures how well the predicted values (yhat) explain the variance in the actual values (y). Values range from negative infinity to 1, where 1 indicates perfect prediction and lower values indicate poorer fit.",
    "euclidean distance": "The Euclidean distance between actual values (y) and predicted values (yhat), representing the overall magnitude of error across all observations. Larger values indicate greater overall deviation.",
    "mae": "Mean Absolute Error (MAE) is the average absolute difference between actual values (y) and predicted values (yhat). It represents the typical size of prediction errors in the same units as the target variable.",
    "rmse": "Root Mean Squared Error (RMSE) is the square root of the average squared differences between actual values (y) and predicted values (yhat). It penalizes larger errors more heavily than MAE and is expressed in the same units as the target variable.",
    "mse": "Mean Squared Error (MSE) is the average of the squared differences between actual values (y) and predicted values (yhat). It emphasizes larger errors due to squaring and is expressed in squared units.",
    "Average Actual": "The mean (average) of the actual observed values (y) across all records. This provides a baseline scale for interpreting error metrics.",
    "CV RMSE": "Coefficient of Variation of RMSE, calculated as RMSE divided by the mean of actual values (y). It standardizes RMSE relative to the scale of the data, allowing comparison across different datasets.",
    "CV MAE": "Coefficient of Variation of MAE, calculated as MAE divided by the mean of actual values (y). It expresses the average absolute error relative to the scale of the data.",
    "MAPE": "Mean Absolute Percentage Error (MAPE) measures the average percentage difference between actual values (y) and predicted values (yhat). It expresses error as a percentage, making it easy to interpret across different scales. Undefined or unstable when actual values are near or equal to zero.",
    "Coverage": "The proportion of actual values (y) that fall within the predicted lower and upper bounds (yhat_lower and yhat_upper). It measures how well the prediction intervals capture the true values, with higher values indicating better uncertainty calibration.",
    'province_shorthand': "The shorthand for the Canadian Province this forecast was generated for. ex. Ontario == ON, Quebec == QC"
}

Future_Meta_Data_Descriptions = {
    'Province': "The name of the Canadian Province this forecast was generated for.",
    '2026': "The total employment in persons thousands forecasted for 2026",
    '2027': "The total employment in persons thousands forecasted for 2027",
    '2028': "The total employment in persons thousands forecasted for 2028",
    '2029': "The total employment in persons thousands forecasted for 2029",
}
#endregion

#region [Model]
ForecastAnalysisModel = CreateModel(ModelEnum.QWEN_7, schema=ForecastSummaries)
FutureAnalysisModel = CreateModel(ModelEnum.GRANITE, schema=FutureSummaries)
FinalAnalysisModel = CreateModel(ModelEnum.QWEN_14, schema=FinalForecastInsight)
ExplainingModel = CreateModel(ModelEnum.QWEN_14)
#endregion


#region [Prompts]
ForecastAnalysisPrompt = PromptTemplate(
    input_variables=["Forecast_Meta_Data_Descriptions", "Evaluation_Data"],
    template = """
You are a forecasting evaluation expert. Your task is to analyze forecast evaluation metrics and produce structured summaries.

You will be given:
1. A dictionary describing each evaluation metric and what it represents.
2. Evaluation data containing forecast performance across one or more groups (e.g., provinces).

---------------------
METRIC DEFINITIONS:
{Forecast_Meta_Data_Descriptions}
---------------------

EVALUATION DATA:
{Evaluation_Data}
---------------------

INSTRUCTIONS:

For each group in the evaluation data:
- Assess the overall quality of the forecast using the provided metrics.
- Consider:
    - Goodness of fit (e.g., high r2)
    - Error magnitude (e.g., low MAE, RMSE, MAPE)
    - Stability (e.g., CV RMSE, CV MAE)
    - Reliability of uncertainty (e.g., Coverage)
- Use "Average Actual" to contextualize the scale of errors.
- Be cautious if MAPE may be unstable (e.g., values near zero).

OUTPUT REQUIREMENTS:

Return a JSON object that strictly follows this schema:

- forecast_summaries: a list of summaries, where each summary contains:
    - Confidence: a float between 0 and 1
        - High confidence → strong fit, low relative error, good coverage
        - Medium confidence → moderate fit or some instability
        - Low confidence → poor fit, high error, or unreliable coverage
    - strenghts: a concise but informative description of what the model did well
        - Mention specific metrics to justify your reasoning
        - Focus only on strengths (do not include weaknesses)

IMPORTANT:
- Do NOT include any text outside the JSON response.
- Ensure all confidence values are between 0 and 1.
- Keep explanations concise but data-driven.
- Generate one summary per group in the evaluation data.

Return only valid JSON.
"""
)

FutureAnalysisPrompt = PromptTemplate(
    input_variables=['Future_Meta_Data_Descriptions','Future_Projections'],
    template="""
You are an economic forecasting analyst. Your task is to interpret future employment projections and produce concise, structured summaries.

You will be given:
1. A dictionary describing each field in the dataset.
2. A dataset containing future employment projections by province.

---------------------
FIELD DEFINITIONS:
{Future_Meta_Data_Descriptions}
---------------------

FUTURE PROJECTIONS DATA:
{Future_Projections}
---------------------

INSTRUCTIONS:

For each province:
- Analyze the employment trend from 2026 to 2029.
- Identify whether the trend is:
    - Increasing
    - Decreasing
    - Stable / flat
    - Fluctuating
- Highlight any notable patterns (e.g., steady growth, sharp increase, plateau, or volatility).
- Keep the interpretation simple and business-friendly.

OUTPUT REQUIREMENTS:

Return a JSON object that strictly follows this schema:

- future_summaries: a list of summaries, where each summary contains:
    - Province: the province name (use shorthand if appropriate)
    - Province Summary: a clear 1 to 2 sentence summary describing the trend in employment forecasts

WRITING GUIDELINES:
- Be concise (maximum 2 sentences per province).
- Focus on trend and direction, not raw numbers.
- Do NOT repeat the raw values unless necessary for emphasis.
- Do NOT include any text outside the JSON response.

IMPORTANT:
- Ensure the output is valid JSON.
- Generate one summary per province in the dataset.

Return only valid JSON.
"""
)

FinalAnalysisPrompt = PromptTemplate(
    input_variables=[
        "Metric_Summaries",
        "Projection_Summaries",
        "NOC_Occupation_Group"
    ],
    template="""
You are a senior labor market and forecasting analyst.

Your task is to synthesize forecast evaluation results and future projections to provide clear, decision-oriented insights.

---------------------
CONTEXT:
These forecasts are for the following occupation group:
{NOC_Occupation_Group}
---------------------

FORECAST QUALITY SUMMARIES:
{Metric_Summaries}
---------------------

FUTURE PROJECTION SUMMARIES:
{Projection_Summaries}
---------------------

INSTRUCTIONS:

1. Evaluate overall forecast reliability:
   - Use confidence levels and strengths from Metric_Summaries
   - Determine if projections are generally trustworthy or should be interpreted with caution

2. Analyze future outlook:
   - Identify which provinces show strong growth, stability, or decline
   - Consider consistency and direction of trends

3. Combine BOTH perspectives:
   - A province is “promising” if:
        (a) it has strong projected growth AND
        (b) the forecast confidence is reasonably high
   - A province is “less promising” if:
        (a) growth is weak/declining OR
        (b) forecast confidence is low

4. Make a decision:
   - Select ONE top province (most promising)
   - Select ONE bottom province (least promising)

OUTPUT REQUIREMENTS:

Return a JSON object with:

- summary:
    A 2–4 sentence executive-level summary of the overall outlook

- top_province:
    The province that shows the most promise

- bottom_province:
    The province that shows the least promise

- reasoning:
    A clear explanation that references BOTH:
        - forecast quality (confidence, strengths)
        - projection trends (growth, stability, decline)

GUIDELINES:
- Be concise but analytical
- Do NOT repeat raw data
- Focus on insight and decision support
- Do NOT include any text outside the JSON

Return only valid JSON.
"""
)

ExplainingModelPrompt = PromptTemplate(
    input_variables=[
        "Formatted_Analysis"
    ],
    template="""

        You are a labor market analyst explaining forecast results to a user.

        Here is the structured analysis:
        {Formatted_Analysis}

        Explain:
        - Overall outlook
        - Most promising province
        - Least promising province
        - Why

        Be conversational and friendly.
        Make use of Mardown symbols to enchance the visibility of your answer, here are guidlines:
         '''
        - `#` → Main titles
        - `##` → Major section 
        - `###` → Sub-section 
        - `-` → Bulleted items or highlights
        - `**text**` → Important labels or keywords
        - `> ` → Optional notes or warnings
        - Emojis → Use to highlight important points, but sparingly
        '''
    """
)
#endregion

#region [Chains]
ForecastAnalysisChain = ForecastAnalysisPrompt | ForecastAnalysisModel
FutureAnalysisChain = FutureAnalysisPrompt | FutureAnalysisModel
FinalAnalysisChain  = FinalAnalysisPrompt | FinalAnalysisModel
#endregion

#region [Parallel Chains]
Processing_Chain = RunnableParallel({
    'Metrics': ForecastAnalysisChain,
    'Projections': FutureAnalysisChain,
})
#endregion

class ForecastAnalysisAgents:
    def __init__(self, memory):
        '''
            Initializes the ForecastAnalysisAgents.
        '''
        
        self.memory = memory
        self.processing_chain = Processing_Chain
        self.final_agent = FinalAnalysisChain
        self.explaining_agent = create_agent(
            model=ExplainingModel,
            tools=[],
            checkpointer=memory
        )

    def Process_Data(self,Evaluation_Data: list[dict], Future_Projections: list[dict]):
        '''
            Returns: Processessed evaluation data and future projections through parallel chains and returns structured summaries.
            Args:
                Evaluation_Data: A list of dictionaries containing forecast evaluation metrics for each province.
                Future_Projections: A list of dictionaries containing future employment projections for each province.
        '''
        
        method = inspect.currentframe().f_code.co_name
        try:

            logger.info(f'{method}()')

            results = self.processing_chain.invoke(
                input={
                    'Forecast_Meta_Data_Descriptions': Forecast_Meta_Data_Descriptions,
                    'Future_Meta_Data_Descriptions': Future_Meta_Data_Descriptions,
                    'Evaluation_Data': json.dumps(Evaluation_Data, indent=2, ensure_ascii=False),
                    'Future_Projections': json.dumps(Future_Projections, indent=2, ensure_ascii=False)
                }
            )

            Payload = {
                'Metric_Summaries': results['Metrics'].model_dump(by_alias=True),
                'Projection_Summaries': results['Projections'].model_dump(by_alias=True)
            }

            with open('test.json','w') as f:
                json.dump(Payload, f, indent=4)

            return Payload


        except Exception as e:
            logger.exception(e)
            return {
                'Metric_Summaries': "Not Available",
                'Projection_Summaries': "Not Available",
            }    

    def Ask_Agents(self, params):
        '''
            Returns: A 4 year structured analysis of the forecast data and future projections from the chatbot agent.
            Args:
                params:{
                    'session_id': str => A unique identifier for the session, used for memory management and context tracking.
                    'Evaluation_Data': list[dict] => A list of dictionaries containing forecast evaluation metrics for each province.
                    'Future_Projections': list[dict] => A list of dictionaries containing future employment projections for each province.
                    'NOC_Occupation_Group': str => The NOC occupation group for which to analyze forecasts.
                }.
        '''
        
        try:

            logger.info('Forecast Analysis Agents')

            session_id = params.get('session_id','default')

            Evaluation_Data = params.get('Evaluation_Data',[])
            Future_Projections = params.get('Future_Projections',[])
            
            Processed_Data_Result = self.Process_Data(Evaluation_Data=Evaluation_Data, Future_Projections=Future_Projections)
            
            Projection_Summaries = Processed_Data_Result.get('Projection_Summaries',['Unavailable'])
            Metric_Summaries = Processed_Data_Result['Metric_Summaries']
            
            NOC_Occupation_Group = params.get('NOC_Occupation_Group', 'Not Available')


            results = self.final_agent.invoke(
                input={
                    'Projection_Summaries': json.dumps(Projection_Summaries, indent=2),
                    'Metric_Summaries': json.dumps(Metric_Summaries, indent=2),
                    'NOC_Occupation_Group': NOC_Occupation_Group,
                }
            )

            result_converted = results.model_dump(by_alias=True)

            prompt = ExplainingModelPrompt.format(
                Formatted_Analysis=json.dumps(result_converted, indent=2, ensure_ascii=False),
            )



            config = {"configurable": {"thread_id": session_id}}

            response = self.explaining_agent.invoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )

            # The last message content
            content = response["messages"][-1].content

            return content

        except Exception as e:
            logger.exception(f"Ask_Agent() failed: {e}")
            return "Forecast Analysis failed due to an error."



