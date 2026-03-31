import warnings
from pydantic import BaseModel, Field
from tqdm import tqdm
from langchain_core.prompts import PromptTemplate
import logging
import json
import time
from enum import Enum
from Agents.ModelCatalogue import ModelEnum, CreateModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent

logger = logging.getLogger(__name__)





#region [Meta Data Descriptions]
Meta_Data_Descriptions = {
    "MajorFieldOfStudy": "The major field of study or discipline that individuals in the dataset have pursued in their education.",
    "OccupationGroup": "The career group classification according to the National Occupational Classification (NOC) system, which individuals in the dataset belong to based on their occupation.",
    "HighestEducation": "The highest level of education attained by individuals in the dataset [Bachelor's degree, Master's degree, Earned doctorate]",
    "Age": "The age range of the individuals in the dataset.",
    "Gender":"The Gender of the Individuals in this subset.",
    "MaxAvgIncome": "The maximum average income for individuals in the dataset, measured in Canadian dollars (CAD).",
    "MinAvgIncome": "The minimum average income for individuals in the dataset, measured in Canadian dollars (CAD).",
    "25thPercentileAvgIncome": "The average income at the 25th percentile for individuals in the dataset, measured in Canadian dollars (CAD).",
    "MedianAvgIncome": "The median average income for individuals in the dataset, measured in Canadian dollars (CAD).",
    "75thPercentileAvgIncome": "The average income at the 75th percentile for individuals in the dataset, measured in Canadian dollars (CAD).",
    "StdDevAvgIncome": "The standard deviation of average income for individuals in the dataset, measured in Canadian dollars (CAD).",
    "SampleSize": "The number of individuals who fit this combination amongst MajorFieldOfStudy, OccupationGroup, HighestEducation, Age and Gender."
}
#endregion

#region [Model]
IncomeAnalysis_Model = CreateModel(ModelEnum.GRANITE)
#endregion


#region [Prompt]
IncomeAnalysis_Prompt_Template = PromptTemplate(
    input_variables=["metadata_descriptions", "data"],
    template="""
You are a data analyst. Your task is to generate a clear, structured, and data-driven analysis based on the provided dataset.

### Metadata Definitions:
{metadata_descriptions}

### Dataset:
{data}

---

### Analysis Requirements:

Your response MUST include the following 3 sections:

---

### 1.
-Identify the different combinations between MajorFieldOfStudy and OccupationGroups

### 2. Education and vs Income Insight
- Identify which **HighestEducationLevel** has the highest observed income
- Use specific metrics such as:
  - MaxAvgIncome
  - MedianAvgIncome
  - 75thPercentileAvgIncome
- Clearly explain how income changes across education levels

---

### 3. Value of Further Education
- Compare income levels between:
  - Bachelor's degree
  - Master's degree
  - Doctorate
- Determine whether pursuing education beyond a Bachelor's degree leads to meaningful financial benefit
- You MUST explicitly conclude one of the following:
  - "Further education is beneficial"
  - "Further education shows limited financial return"
- Support your conclusion with data

---

### 4. Additional Observations
Provide at least 2 meaningful insights, such as:
- Income variability (StdDevAvgIncome)
- Age-related income patterns
- Differences across MajorFieldOfStudy or CareerGroup
- Any notable anomalies or trends in the data

---

### Output Rules:
- Use clear section headers
- Be concise and analytical (avoid fluff)
- Every claim MUST reference the dataset
- Do NOT repeat metadata definitions
- Do NOT hedge (avoid "may", "might", "could")
- Be definitive in conclusions
- Use markdown formatting for clarity
    - `#` → Main title.
    - `##` → Major section 
    - `###` → Sub-section 
    - `-` → Bulleted items or highlights
    - `**text**` → Important labels or keywords
    - `> ` → Optional notes or warnings
    - Emojis → Use to highlight important points, but sparingly
"""
)


#region [Chain]
IncomeAnalysisChain = IncomeAnalysis_Prompt_Template | IncomeAnalysis_Model
#endregion

class IncomeAnalysisAgent:
    def __init__(self, memory):
        '''
            Initializes the IncomeAnalysisAgent.
        '''
        
        self.memory = memory
        self.agent = create_agent(
            model=IncomeAnalysis_Model,
            tools=[],
            checkpointer=memory
        )

    def Ask_Agent(self, Data, session_id="default"):
        '''
            Returns: A string object that contains the chatbot's response to the income distribution analysis
            Args:
                Data: A json dict of income stats.
                session_id: Session ID for Pathways page.
        '''
        try:
            logger.info('Asking Income Analysis Agent')
            prompt = IncomeAnalysis_Prompt_Template.format(
                data=json.dumps(Data, indent=2, ensure_ascii=False),
                metadata_descriptions=json.dumps(Meta_Data_Descriptions, indent=2)
            )

            config = {"configurable": {"thread_id": session_id}}

            response = self.agent.invoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )

            # The last message content
            content = response["messages"][-1].content

            return content

        except Exception as e:
            logger.exception(f"Ask_Agent() failed: {e}")
            return "Income analysis failed due to an error."



