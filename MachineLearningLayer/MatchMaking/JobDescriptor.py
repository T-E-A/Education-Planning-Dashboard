# Abira Demello

from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import logging
import inspect
import json

# Data models: Pydantic models that define the exact structure of the data that will be returned by the model. it enforces type safety and prvents malformed outputs 
class Summary_Object(BaseModel):
    noc_occupation: str = Field(description="The title of the NOC Occupation", alias="Occupation Title") # title of the NOC jo
    description: str = Field(description="2 to 3 sentence description of the NOC Occupation", alias="Description") # 2-3 sentence description of the NOC occupation
    education: str = Field(description="Any required education or credentials needed by someone who decides to purse this role.", alias='Education/Credentials Required') # education or credentials required for the role
#endregion

#region [Summaries Structured Output]
class Summaries(BaseModel):
    summaries : list[Summary_Object] = Field(description="A list of Summaries", alias="Matches")
#endregion

# Model Setup: Initializes the local LLM via Ollama; with_structured_output() forces the model to return data matching the Summaries schema
modelName = 'qwen2.5:14b'
Job_Descriptor_Model = ChatOllama(
    model=modelName,
    options={"num_threads": 4}
).with_structured_output(Summaries)



# Prompt Template: Defines the instructions sent to the AI. 
# Uses 2 dynamic placeholders: {Context}: NOC job documents from the database; and {MatchedList}: Jobs the student was matched to
Match_Prompt_Template = PromptTemplate(
    input_variables=['Context','MatchedList'],
    template=(
        "You are a Job Matching Assistant.\n"
        "Your role is to summarize the documents retrieved from the database that have been pulled based on matched jobs.\n"
        "You will be provided with 2 things.\n"
        "\tNOC Occupation Descriptions: A set of documents describing various NOC Occupations.\n"
        "\tNOC Match List: A list of NOC Occupations the student matched to and for which the documents were retrieved\n"

        "##Instructions##\n"
        "\t1. Per Occupation in the NOC Match List you are to generate a summary that contains 3 things."
        "\t-noc_occupation: The title of the NOC Occupation\n"
        "\t-description: 2 to 3 sentence description of the NOC Occupation\n"
        "\t-education: Any required education or credentials needed by someone who decides to purse this role."
        "\tIf the documents do not contain any information for a NOC Occupation in the NOC Match List, you can skip that NOC."
        "\t2. After generating the summaries, consolidate them into a list.\n"

        "DO NOT Alter the information provided in the documentation.\n"
        "Return only a structure output.\n"

        "You will now be provided with the NOC Occupation Descriptions and NOC Match List\n"

        "##NOC Occupations Descriptions##\n"
        "{Context}\n\n"

        "##NOC Match List##\n"
        "{MatchedList}\n\n"


    )
)
#endregion

# Chain: Connects the prompt template to the model using Langchain's pipe operator | 
# Data flows: prompt --> model --> structured output for the student which is easy to read summaries for each job

Job_Descriptor_Chain = Match_Prompt_Template | Job_Descriptor_Model
#endregion

class Descriptor:
    def __init__(self):
        method = inspect.currentframe().f_code.co_name
        try:
            self.className = self.__class__.__name__
            self.chain = Job_Descriptor_Chain

        except Exception as e:
            logging.getLogger(__name__).exception(f'{method} => Error [{e}]')

    def Describe(self, MatchedList, Context):
        method = inspect.currentframe().f_code.co_name
        try:
            response = self.chain.invoke({
                'Context':json.dumps(Context, indent=2, ensure_ascii=False),
                'MatchedList': json.dumps(MatchedList, ensure_ascii=False)
            })

            return response.model_dump(by_alias=True)
        

        except Exception as e:
            logging.getLogger(__name__).exception(f'{self.className} - {method} => Error [{e}]')
