import warnings
from pydantic import BaseModel, Field
from tqdm import tqdm
from langchain_core.prompts import PromptTemplate
import logging
import json
import time
from enum import Enum
from Agents.ModelCatalogue import ModelEnum, CreateModel

logger = logging.getLogger(__name__)

#region [Action Enum]
class Strength(str, Enum):
    High = "High"
    Moderate = "Moderate"
    Low = "Low"
#endregion

#region [Structuring]
class EmploymentAnalysis(BaseModel):
    # Overall quarterly strength
    strength: Strength = Field(
        description="The quarterly employment strength of the NOC Grouping",
        alias='Strength'
    )
    
    # Summary of key insights
    summary: str = Field(
        description="A 3–4 sentence summary of the observed quarterly lifts, drops, and seasonal patterns in employment.",
        alias='Summary'
    )
    
    # Optional: suggested months for job applications or focus
    recommendation: str = Field(
        description="Actionable recommendation for job seekers based on seasonal employment trends.",
        alias='Recommendation'
    )
#endregion


Quarterly_Analysis_Model = CreateModel(ModelEnum.QWEN_14, schema=EmploymentAnalysis)


#region [Metadata]
Meta_Data_Descriptions = {
    "Year": "The calendar year of observation for employment data.",
    "Month_Name": "The name of the month for the observed data point.",
    "Quarter": "The fiscal quarter of the year (1 to 4) corresponding to the observation.",
    "seasonal_3": "Short-term quarterly fluctuations in employment (every 3 months). Positive values indicate an increase in persons employed, e.g., 24.5 ≈ 24 more employees; negative values indicate a decrease, e.g., -34.6 ≈ 35 fewer employees.",
    "seasonal_6": "Medium-term half-year seasonal patterns (every 6 months). Positive values indicate a moderate increase in employment over six months, negative values indicate a moderate decrease. This helps assess the stability of short-term trends.",
    "seasonal_12": "Long-term yearly seasonal patterns (every 12 months). Positive values indicate a net yearly increase in employment, negative values indicate a yearly decline. This reflects the overall annual trend and cyclical behavior."
}
#endregion

#region [Prompt Template]
Employment_Analysis_Prompt = PromptTemplate(
    input_variables=["Data", "Meta_Data_Descriptions"],
    template="""
You are an expert labor market analyst. You have data on monthly employment for various NOC groups, including three seasonal components:
- seasonal_3 → quarterly (short-term) employment fluctuations
- seasonal_6 → half-year (medium-term) seasonal patterns
- seasonal_12 → yearly (long-term) seasonal trends

Metadata Definitions:
{Meta_Data_Descriptions}

Data:
{Data}

---------------------
Instructions:
---------------------
1. Analyze the seasonal patterns to identify:
   - Meaningful spikes (positive) and drops (negative) in employment
   - Consistency or volatility across months/quarters
   - Alignment or conflict between short-, medium-, and long-term patterns

2. Based on seasonal_3 primarily (supported by seasonal_6 and seasonal_12):
   - Classify the overall quarterly employment strength:
       - High → mostly positive short-term changes, stable trends
       - Moderate → mixed or volatile short-term behavior
       - Low → mostly negative short-term changes

3. Write a **3–4 sentence analytical summary**:
   - Describe key quarterly trends
   - Highlight major increases and decreases
   - Reference medium- and long-term patterns where relevant
   - Note any cyclical or irregular behavior

4. Provide an actionable **recommendation** for students:
   - Suggest optimal months to apply for jobs
   - Highlight timing considerations based on seasonal patterns

---------------------
Output Format (STRICT JSON):
---------------------
Return ONLY a JSON object with the following keys:


  "Strength": "High" | "Moderate" | "Low",
  "Summary": "3–4 sentence analytical summary",
  "Recommendation": "Actionable advice for job seekers"


Rules:
- Use EXACT keys and casing
- Do NOT include extra keys or text
- Enum values must be exactly: High, Moderate, Low
- Do not include explanations outside JSON
"""
)
#endregion

#region [Chain]
Quarterly_Chain = Employment_Analysis_Prompt | Quarterly_Analysis_Model
#endregion


class QuarterlyAnalyzer:
    def __init__(self):
        '''
            Initializes the QuarterlyAnalyzer.
        '''
        try:
            self.className = self.__class__.__name__
            self.chain = Quarterly_Chain

        except Exception as e:
            logger.exception(f'[{e}]')

    def Process_Data(self, Sample, NOC_Grouping):
        '''
        Processes the employment data for a specific NOC grouping and generates an analysis.
        Args:
            Sample: A dictionary containing the employment data for the NOC grouping.
            NOC_Grouping: The name of the NOC grouping being analyzed.
        Returns:
            A dictionary containing the analysis results, including strength, summary, and recommendation.
        '''
        
        try:
        
            response = Quarterly_Chain.invoke({
            'Data': json.dumps(Sample, indent=2, ensure_ascii=False),
            'Meta_Data_Descriptions': json.dumps(Meta_Data_Descriptions, indent=2, ensure_ascii=False)
            })

            response_converted = response.model_dump(by_alias=True)
            response_converted['NOC_Grouping'] = NOC_Grouping

            return response_converted
        
        except Exception as e:
            logger.exception(f"Process_Data(NOC_Grouping={NOC_Grouping}) => {e}")
            return {}

    def Process_All(self, params):
        '''
        Processes the employment data for all NOC groupings and generates analyses for each.
        Args:
            params: A dictionary containing the input parameters, including 'AllSamples' which is a dictionary of employment data for all NOC groupings.
        Returns:
            A list of dictionaries containing the analysis results for each NOC grouping.
        '''
        try:

            AllSamples = params.get('AllSamples',[])

            All_Responses = []
            Keys = list(AllSamples.keys())

            for noc_grouping in tqdm(Keys, desc='Processing NOC Grouping', unit='NOC Grouping'):
                Sample = AllSamples[noc_grouping]
                All_Responses.append(self.Process_Data(Sample=Sample, NOC_Grouping=noc_grouping))

            return All_Responses
        except Exception as e:
            logger.exception(f"Process_All() => {e}")
            return []
    
    def Process_Answers(self, All_Responses, Cluster):
        '''
        Processes the analysis results for all NOC groupings and generates a consolidated answer for the specified cluster.
        Args:
            All_Responses: A list of dictionaries containing the analysis results for each NOC grouping.
            Cluster: The specific cluster number for which the user wants to obtain analysis and insights.
        Returns:
            A string containing the consolidated analysis for the specified cluster.
        '''
        
        try:
        
            Refined_Answer = f"## Cluster {Cluster} Analysis\n"

            for response in All_Responses:
                strength_value = response['Strength'].value if isinstance(response['Strength'], Enum) else response['Strength']

                Refined_Answer += (
                    f"\n---\n"
                    f"### {response['NOC_Grouping']}\n\n"
                    f"**Analysis:**\n{response['Summary']}\n\n"
                    f"**Employment Seasonality:** {strength_value}\n\n"
                    f"**Recommendation:**\n{response.get('Recommendation', 'No recommendation provided.')}\n"
                )

            return Refined_Answer
        except Exception as e:
            logger.exception(f"Process_Answers() => {e}")
            return f"Unable to perform Analysis on Cluster [{Cluster}]"
    
    def Ask_Agent(self, params):
        '''
        Asks the quarterly analysis agent to process the employment data and generate insights for the specified cluster.
        Args:
            params: A dictionary containing the input parameters, including 'AllSamples' which is a dictionary of employment data for all NOC groupings, and 'Cluster' which is the specific cluster number for analysis.
        Returns:
            A string containing the consolidated analysis for the specified cluster.
        '''
        
        All_Responses = self.Process_All(params=params)
        Cluster = params['Cluster']
        return self.Process_Answers(All_Responses=All_Responses, Cluster=Cluster)