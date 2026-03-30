from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from langchain_core.prompts import PromptTemplate
import logging
import inspect
import json
from Agents.ModelCatalogue import ModelEnum, CreateModel
from datetime import datetime, timezone
import json



logger = logging.getLogger(__name__)


#region Declare LLM Output Structure
class Documents_and_Source(BaseModel):
    sources: list[str] = Field(description="A list of URLs of where the documents were retrieved.", alias='Sources')
    answer: str = Field(description="The answer for the users query.", alias='Answer' )
#endregion 


Chat_Assisstant_Model = CreateModel(ModelEnum.QWEN_14, schema=Documents_and_Source)

#region Prompt Template 
Chat_Assisstant_Prompt_Template = PromptTemplate(
    input_variables=["context", "user_query", "chat_history"],
    template=(
        "You are an Education Planning Assistant.\n\n"

        "## Conversation History ##\n"
        "{chat_history}\n\n"

        "## Context ##\n"
        "{context}\n\n"

        "## User Query ##\n"
        "{user_query}\n\n"

        "## Instructions ##\n"
        "- Use BOTH the conversation history and retrieved context to answer the user.\n"
        "- Maintain continuity with previous responses.\n"
        "- Do NOT contradict earlier answers unless the context clearly updates or corrects them.\n"
        "- Be concise but informative.\n\n"

        "## Output Requirements ##\n"
        "You must produce a response that includes the following fields:\n\n"

        "1. answer:\n"
        "- A clear and complete response to the user's query.\n"
        "- Should directly address the question using context and history.\n\n"

        "2. sources:\n"
        "- A list of URLs that support the answer.\n"
        "- Only include sources present in the provided context.\n"
        "- If no sources are available, return an empty list.\n"
        "- Do NOT fabricate or guess URLs.\n\n"

        "Ensure both fields are always present in your response."
    )
)
#endregion 


#region [Chain]

Chat_Assisstant_Chain = Chat_Assisstant_Prompt_Template | Chat_Assisstant_Model


class ChatAgent:
    def __init__(self):
        '''
            Initializes the ChatAgent.
        '''
        

        self.SESSION_STORE: Dict[str, list[Dict[str, str]]] = {}
        self.chain = Chat_Assisstant_Chain
    
    def Get_History(self ,session_id: str):
        try:
            return self.SESSION_STORE.get(session_id, [])
        except Exception as e:
            logger.exception(f'[{e}]')
            return []
    
    def Update_History(self, session_id: str, user_query: str, answer: str):
        '''
            Updates the conversation history for a given session.
            Args:
                session_id: The unique identifier for the user's session.
                user_query: The user's query to the chatbot.
                answer: The chatbot's response to the user's query.
        '''
        
        try:

            self.SESSION_STORE.setdefault(session_id, []).append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user": user_query,
                "assistant": answer
            })

            # print(self.SESSION_STORE)
            
        except Exception as e:
            logger.exception(f'[{e}]')
            raise
    def Format_History(self,history: list[Dict[str, str]]) -> str:
        '''
            Formats the conversation history into a string for use in the prompt.
            Args:
                history: A list of dictionaries representing the conversation history.
            Returns:
                A formatted string of the conversation history.
        '''
        
        try:
            return "\n".join(
                f"User: {h['user']}\nAssistant: {h['assistant']}"
                for h in history
            )
        except Exception as e:
            logger.exception(f'[{e}]')
            return "User: --\nAssistant: --"
        
    def Prepare_Content(self,params):
        '''
        Prepares the content for the chat assistant by formatting the conversation history.
        Args:
            'chat_history': The raw conversation history for the session.
        Returns:
            A dictionary with the extended parameters including the formatted chat history.
        '''
        
        try:

            session_id = params.get('session_id','')

            history = self.Get_History(session_id=session_id)
            formatted_history = self.Format_History(history=history)

            params_extended = {
                **params,
                'chat_history': formatted_history
            }
           

            return params_extended
        
        except Exception as e:
            logger.exception(f'[{e}]')
            return {}
    def Serialize_Sessions(self) -> dict:
        '''
        Serializes the conversation sessions.
        Returns:
            A dictionary containing all conversation sessions.
        '''
        
        try:
        
            return self.SESSION_STORE

        except Exception as e:
            logger.exception(f'[{e}]')
            raise

    def Ask_Chat_Agent(self,params):
        '''
        Asks the chat agent a question and returns the response.
        Args:
            params: A dictionary containing the input parameters.
        Returns:
            The response from the chat agent.
        '''
        
        try:

            params_extended = self.Prepare_Content(params=params)

            session_id = params_extended['session_id']
            
            user_query = params_extended['user_query']
            context = params_extended['context']
            chat_history = params_extended['chat_history']



            response = self.chain.invoke({
                "context": context,
                "user_query": user_query,
                "chat_history": chat_history
            })

            self.Update_History(session_id=session_id, user_query=user_query, answer=response.answer)

            return response

            

        except Exception as e:
            logger.exception(f'{[e]}')
            return f"I cannot answer that due to system error [{e}]"


