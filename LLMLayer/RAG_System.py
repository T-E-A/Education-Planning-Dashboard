from typing import Optional, Dict, Any
import chromadb
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
import json
import Guard_Rails as Guard_Rails
from pydantic import BaseModel, Field


#region Declare LLM Output Structure
class Documents_and_Source(BaseModel):
    sources: list[str] = Field(description="A list of URLs of where the documents were retrieved.")
    answer: str = Field(description="The answer for the users query.")
#endregion 

#region Prompt Template 
prompt_template = PromptTemplate(
            input_variables=["context", "user_query"],
            template=(
                "You are Education Planning Assistant. Your task to is anwser the users query given your own knowledge and context that is provided to you.\n"
                "The context will be formatted as JSON object and will have the following keys:\n"
                "\tdocument: <The context chunk of information retireved for the you>\n"
                "\tsource: <A URL which denotes the source of the document>\n"

                "##Instructions##\n"
                "Utilize the retireved documents to generate at answer and consolidate the sources into a list. You output should have to things\n"
                "\t1. answer: <Your answer to the users query after consulting the contexts>\n"
                "\t2. sources: <A list of URLs for the documents you have specifically consulted to generated an answer>\n\n"

                "DO NOT Change or Alter any of the retrieved information.\n"
                "Return only a structured output. Always include the sources\n"

                "You will now be provided with the context and users query."

                "##Context##\n"
                "{context}\n"

                "##User Query##\n"
                "{user_query}\n"

                
            )
        )

#endregion 

#region Initialization of Vector DB and Model
#Load Vector Database
print('Loading Vector Database and Collections...')
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="Eduction_Planning_Documents")
print("Vector DB loaded")

#Initialize Model
def Initialize_Model():
    try:
        llm_model = 'phi4:14b'
        ChatModel = ChatOllama(
            model=llm_model,
            options={"num_thread": 4}
        ).with_structured_output(Documents_and_Source)

        ChatModelChain = prompt_template | ChatModel
        print(f"Model '{llm_model}' initialized")
        return ChatModelChain

    except Exception as e:
        print(f"Error initializing model => {e}")
        return None


ChatModelChain = Initialize_Model()
#endregion


#region Guard Rails Scans

def Scan_Input(Prompt: str) -> Dict[str, Any]:
    
    scan_result = Guard_Rails.Pre_RAG_Prompt_Check(Prompt)
    return scan_result

def Scan_Output(OriginalQuery: str, AugmentedPrompt: str, ResponseText: str) -> Dict[str, Any]:
    scan_result = Guard_Rails.Post_RAG_Prompt_Check(OriginalQuery, AugmentedPrompt, ResponseText)
    return scan_result

#endregion


#region RAG Retrieval and Textualizing

def Retrieve_Documents(usery_query: str, k: int) -> list:
    try:
        results = collection.query(
            query_texts=[usery_query],
            n_results=k
        )
        docs_nested = results.get('documents',[])
        metas_nested = results.get('metadatas', [])

        docs = docs_nested[0] if docs_nested else []
        metas = metas_nested[0] if metas_nested else []

        #Creating a list of dictionaries that pair documents to the source. 
        retireved = [
            {
                'document':doc,
                'source': meta['source']
            }
            for doc, meta in zip(docs, metas)
        ]
        return retireved
    except Exception as e:
        print(f"Error retrieving documents => {e}")
        return []

def Textual_Documents(retrieved: list) -> str:
    try:
        
        return json.dumps(retrieved, indent=2, ensure_ascii=False)

    except Exception as e:
        return ""

#endregion 


#region Response Generation with Ollama Model 

def Generate_Response(user_query: str, context: str) -> str:
    try:
        


        response = ChatModelChain.invoke({
            'context':context,
            'user_query':user_query
        })

        response_formatted = "\n**Answer**:\n"
        response_formatted += f"{response.answer}\n"
        response_formatted += f"**Sources**:\n"

        for url in response.sources:
            response_formatted += f"{url}\n"
        
        return response_formatted, user_query

    except Exception as e:
        print(f"Error generating response => {e}")
        return "I'm sorry, I couldn't generate a response at this time."
    

def RAG_Query(user_query: str) -> str:
    try:
        print("Input Scan")
        InputScanResult = Scan_Input(Prompt=user_query)

        if not InputScanResult['IsValid']:
            return InputScanResult['Prompt'], '', {}
        print("Retrieving Documents")
        retrieved_docs = Retrieve_Documents(user_query, k=7)

        print("Textualizing Documents")
        context = Textual_Documents(retrieved_docs)

        print("Generating Response")
        response, augmented_prompt = Generate_Response(user_query, context)

        print("Output Scan")
        FinalResult = Scan_Output(OriginalQuery=user_query, AugmentedPrompt=augmented_prompt, ResponseText=response)

        return FinalResult['Response']
    
    except Exception as e:
        print(f"Error in RAG Query => {e}")
        return "I'm sorry, I couldn't process your request at this time.", ""

#endregion