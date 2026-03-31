import logging
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  
from Agents.ModelCatalogue import ModelEnum, CreateModel
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
import json
import logging 

logger = logging.getLogger(__name__)

Pathways_Assisstant_Model = CreateModel(ModelEnum.QWEN_14)



Pathways_Prompt_Template = PromptTemplate(
    input_variables=["Query", "Context"],
    template=(
        "You are a Career Pathways Assistant. Your role is to help users explore and understand potential career pathways based on their interests.\n"
        "Your task is to answer the user's query **using the Context provided or your memory**\n."
        "You will be provided with a Query and relevant Context based on the user's interest.\n"
        "Note: Sometimes Context will be empty, if so you can ignore it and use your memory to answer the question."

        "Context:\n"
        "{Context}\n\n"

        "User Query:\n"
        "{Query}\n\n"

        "Instructions:\n"
        "1. Use the combination of your memory and context provided to formulate your answer."
        "2. Summarize and synthesize the information clearly and concisely.\n"
        "3. Do not hallucinate; if the documents do not contain the answer, respond that the information is not available.\n"
        "4. Be precise and professional in your response.\n\n"
        "5. Use easy to interpret language and avoid high level jargon\n\n"
        "6. If the Summaries and Context list was empty, rely on your memory to generate an answer."
        "7. Use markdown symbols effectively, here are the guidelines:"
        '''
        - `#` → Main titles
        - `##` → Major section 
        - `###` → Sub-section 
        - `-` → Bulleted items or highlights
        - `**text**` → Important labels or keywords
        - `> ` → Optional notes or warnings
        - Emojis → Use to highlight important points, but sparingly
        '''

        "Generate your answer:"

    )
)


class CareerPathwaysAgent:
    def __init__(self, memory):
        '''
        Initializes the CareerPathwaysAgent.
        '''
        self.memory = memory
        self.agent = create_agent(
            model=Pathways_Assisstant_Model,
            tools=[],
            checkpointer=memory
        )

    def Ask_Agent(self, docs, query, session_id="default"):
        '''
            Returns: The generated answer from the agent based on the provided documents and user query for career pathways.
            Args:
                docs: A list of relevant documents or summaries that can be used as context for answering the user's query.
                query: The user's input query for career pathways.
                session_id: Session ID for Pathways page.
        '''
        try:
            if not docs:
                docs = []

            logger.info('Asking Pathways Agents')
            prompt = Pathways_Prompt_Template.format(
                Context=json.dumps(docs, indent=2),
                Query=query
            )

            config = {"configurable": {"thread_id": session_id}}

            response = self.agent.invoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )

            messages = response['messages']

            msglist =  [
                {
                    "type": msg.__class__.__name__,
                    "content": msg.content
                    }
                    for msg in messages
                ],
            
            try:
                with open('Pathways_Sample.json','w') as f:
                    json.dump(msglist, f, indent=4)
            except:
                print(msglist)

            return response["messages"][-1].content

        except Exception as e:
            logger.error(f"generate_answer failed: {e}")
            return "Error generating answer."

