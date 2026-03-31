import warnings
from pydantic import BaseModel, Field
from tqdm import tqdm
from langchain_core.prompts import PromptTemplate
import logging
import json
from enum import Enum
from Agents.ModelCatalogue import ModelEnum, CreateModel
from typing import List

logger = logging.getLogger(__name__)

#region [Action Enum]
class MatchQuality(str, Enum):
    Good = "Good"
    Okay = "Okay"
    Bad = "Bad"
#endregion

#region [Structuring]
class UniversityAnalysis(BaseModel):

    university: str = Field(
        description="Name of the university being analyzed",
        alias="University"
    )

    match_quality: MatchQuality = Field(
        description="Overall affordability match based on total comparison across all expense categories",
        alias="Match_Quality"
    )

    summary: str = Field(
        description="2-3 sentence explanation of why the university is a good, okay, or bad match based on budget differences",
        alias="Summary"
    )

class BudgetAnalysisResponse(BaseModel):

    analyses: list[UniversityAnalysis] = Field(
        description="List of per-university analyses",
        alias="Analyses"
    )

    recommendation: str = Field(
        description="Final recommendation identifying the best university option based on affordability",
        alias="Recommendation"
    )

#endregion


Budget_Analysis_Model = CreateModel(ModelEnum.QWEN_14, schema=BudgetAnalysisResponse)


#region [Metadata]
Meta_Data_Descriptions = {
    "Structure": {
        "Level_1": "University Name (string) - Top-level key representing each institution.",
        "Level_2": "Expense Type (string) - Categories of student-related expenses.",
        "Level_3": "Metrics (dict) - Financial comparison data."
    },

    "Metrics_Definition": {
        "Fee": "Cost charged by the university",
        "User Budget": "Amount student is willing to pay",
        "Comparison": "User Budget - Fee",
        "Comparison_Label": "Over Budget, Under Budget, Equal"
    },

    "Semantic_Meaning": {
        "Positive_Comparison": "Affordable (under budget)",
        "Negative_Comparison": "Not affordable (over budget)",
        "Zero_Comparison": "Exact match"
    }
}
#endregion


#region [Prompt Template]
Budget_Analysis_Prompt = PromptTemplate(
    input_variables=["Data", "Meta_Data_Descriptions"],
    template="""
You are a financial advisor helping students choose the most affordable university.

Metadata Definitions:
{Meta_Data_Descriptions}

Data:
{Data}

---------------------
Instructions:
---------------------

1. For EACH university:
   - Calculate overall affordability by summing all "Comparison" values
   - Identify key cost drivers (largest negative values)
   - Assess affordability:
        Good → mostly under budget or small deficit
        Okay → mixed affordability, moderate deficits
        Bad → significantly over budget

2. Generate a short summary (2–3 sentences):
   - Explain affordability
   - Mention key expensive categories (e.g., Tuition, Housing)

3. Recommend the BEST option based on:
   - Highest total affordability
   - Fewest major budget overruns

---------------------
Output Format:
---------------------

Return your answer in a clean structured format like:

University: <name>
Match Quality: Good / Okay / Bad
Summary: <2–3 sentence explanation>

(repeat for each university)

Then at the end:

Recommendation: <best university and reasoning>

---------------------
Rules:
- Be consistent in formatting
- Do NOT include JSON
- Do NOT include extra commentary
- Use only the provided data
"""
)
#endregion


#region [Chain]
Budget_Chain = Budget_Analysis_Prompt | Budget_Analysis_Model
#endregion


class BudgetAnalyzer:
    def __init__(self):
        '''
        Initializes the BudgetAnalyzer.
        '''
        try:
            self.className = self.__class__.__name__
            self.chain = Budget_Chain
        except Exception as e:
            logger.exception(f'[{e}]')

    def Process_Data(self, Data):
        '''
            Returns: Processed budget analysis based on the input data and metadata descriptions.
            Args:
                Data: A nested dictionary of budget-related data for each university and expense category.
        '''
        try:

            logger.info(f"INcoming Data => {json.dumps(Data, indent=2, ensure_ascii=False)}")

            response = self.chain.invoke({
                'Data': json.dumps(Data, indent=2, ensure_ascii=False),
                'Meta_Data_Descriptions': json.dumps(Meta_Data_Descriptions, indent=2, ensure_ascii=False)
            })

            return response.model_dump(by_alias=True)

        except Exception as e:
            logger.exception(f"Process_Data() => {e}")
            return {}

    def Process_Answers(self, Response):
        '''
            Returns: A refined string analysis based on the structured response from the model.
            Args:
                Response: The structured output from the budget analysis model containing university analyses and recommendation.
        '''
        try:
            refined = "## ✅ Recommendation\n\n"
            refined += f"{Response.get('Recommendation', 'No recommendation provided.')}\n\n"

            refined += "## 🎓 University Budget Analysis\n"

            logger.info("Processing structured response")
            for uni in Response.get("Analyses", []):
                match = uni["Match_Quality"].value if isinstance(uni["Match_Quality"], Enum) else uni["Match_Quality"]

                refined += (
                    f"\n---\n"
                    f"### {uni['University']}\n\n"
                    f"**Match Quality:** {match}\n\n"
                    f"**Analysis:**\n{uni['Summary']}\n"
                )


            logger.info(f'Done Processing => Sending')

            return refined

        except Exception as e:
            logger.exception(f"Process_Answers() => {e}")
            return "Unable to generate analysis."

    def Ask_Agent(self, params):
        response = self.Process_Data(Data=params["Data"])
        return self.Process_Answers(Response=response)