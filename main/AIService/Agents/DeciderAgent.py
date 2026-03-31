from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from enum import Enum
import logging

# ---------------------------
# Logging
# ---------------------------
logger = logging.getLogger(__name__)

# ---------------------------
# Enum for Decision Category
# ---------------------------
class RetrievalCategory(str, Enum):
    NO_RETRIEVAL = "NO_RETRIEVAL"
    RETRIEVAL_REQUIRED = "RETRIEVAL_REQUIRED"
    RETRIEVAL_OPTIONAL = "RETRIEVAL_OPTIONAL"

# ---------------------------
# Pydantic Model
# ---------------------------
class RetrievalDecision(BaseModel):
    needs_retrieval: bool = Field(alias="Needs Retrieval")
    confidence: float = Field(alias="Confidence")
    category: RetrievalCategory = Field(alias="Category")
    reasoning: str = Field(alias="Reasoning")

# ---------------------------
# Model
# ---------------------------
decision_model = ChatOllama(
    model='qwen2.5:14b-instruct-q4_K_M',
    options={"num_threads": 4}
)

# ---------------------------
# Prompt Template
# ---------------------------
decision_prompt = PromptTemplate(
    input_variables=["query"],
    template="""
You are an assistant that determines whether a user query requires retrieving documents
from a private knowledge base.

Your task:
1. Analyze the query.
2. Decide if retrieval is needed.

Decision Guidelines:
- RETRIEVAL_REQUIRED:
    Queries about specific NOC Occupations or Major field of studies like: 
        <ex. Data Scientists, or Computer Science Majors, Humanities, Education Majors>, 
        <asking for specific information about Unviersities or Provincies>
- RETRIEVAL_OPTIONAL:
    Queries that could benefit from additional context like 'What do I need for this <> roles?' or 'What are the pathways for <>?'
- NO_RETRIEVAL:
    General knowledge, definitions, coding help, or the query does NOT introduce a new noun/entity that requires external data
        “Which has the highest avg income?”
        “Which one is lower?”
        “What do they do again?”
        “Why is this one higher?”
        “How does this compare?”
        “What’s happening here?”

Rules:
- Bias toward RETRIEVAL_REQUIRED if uncertain
- Confidence must be between 0 and 1

The result should be in this structure:

  "Needs Retrieval": <true or false>,
  "Confidence": <float between 0 and 1>,
  "Category": "<NO_RETRIEVAL | RETRIEVAL_REQUIRED | RETRIEVAL_OPTIONAL>",
  "Reasoning": "<short explanation>"


User Query:
{query}
"""
)

# ---------------------------
# Main Function
# ---------------------------
def decide_retrieval(query: str) -> dict:
    '''
        Returns: A dictionary with the following structure:
        {
            "Needs Retrieval": <true or false>,
            "Confidence": <float between 0 and 1>,
            "Category": "<NO_RETRIEVAL | RETRIEVAL_REQUIRED | RETRIEVAL_OPTIONAL>",
            "Reasoning": "<short explanation>"
        }
        Args:
            'query': str => The user's input query that needs to be analyzed for retrieval necessity.
    '''
    
    try:
        logger.info("Deciding if retrieval is needed...")

        prompt = decision_prompt.format(query=query)

        response = decision_model.with_structured_output(RetrievalDecision).invoke(
            [HumanMessage(content=prompt)]
        )

        decision = response.model_dump(by_alias=True)

        logger.info(f"Decision: {decision}")
        return decision

    except Exception as e:
        logger.error(f"Decision agent failed: {e}")

        # Safe fallback → default to retrieval
        return {
            "Needs Retrieval": True,
            "Confidence": 0.5,
            "Category": "RETRIEVAL_REQUIRED",
            "Reasoning": "Fallback due to error"
        }