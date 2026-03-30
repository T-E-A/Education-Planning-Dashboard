# Abira Demello

import chromadb
import logging
import inspect
import os
from pathlib import Path

# Connects to a local Vector Database and retrieves the most relevant NOC occupation documents based on the student's matched job titles 
BASE_DIR = Path(__file__).resolve().parent.parent

VectorDB_Path = Path(
    os.getenv(
        "Vector_DB",
        (BASE_DIR.parent / "Repository" / "VectorDatabase" / "chroma_db")
    )
).resolve()


print(f"Using DB Path: {VectorDB_Path}")


class Retriever:
    def __init__(self):
        # Setup the Retriever and connect to the vector DB

        method = inspect.currentframe().f_code.co_name
        try:
            self.className = self.__class__.__name__

            # Connect to the database and store the collection for later use
            self.collection = self.Initilize() 
            logging.getLogger(__name__).info(f"Vector Collection Initialized.")

        except Exception as e:
            logging.getLogger(__name__).exception(f'{method} => Error [{e}]')
    
    def Initilize(self):

        # Connect to the local Chroma DB database and return the NOC documents collection

        method = inspect.currentframe().f_code.co_name
        try:
            client = chromadb.PersistentClient(path=f"{VectorDB_Path}") # load the chromaDB stored
            return client.get_collection(name="Eduction_Planning_Documents")

        except Exception as e:
            logging.getLogger(__name__).exception(f'{method} => Error [{e}]')
    
    def Query(self, query, *, n_results: int = None, meta_filter=None):
        '''
            Returns: A list of the most relevant documents and their sources based on the inputed query and filter.
            Args:
                query: A string query to search the vector database with. In this case, its a string of matched job titles.
                n_results: An optional integer specifying how many results to return. Defaults to 5 if not provided.
                meta_filter: An optional dictionary specifying metadata filters to apply to the search. For example, {"content":"NOC"} would filter results to only include documents where the "content" metadata field contains "NOC".
        '''
        
        # Search the vector database for NOC documents relevant to the matched jobs

        method = inspect.currentframe().f_code.co_name
        try:

            # Join the matched job titles into one search string and query the database; 
            # n_results=10 returns the top 10 most relevant documents where={"content":"NOC"} filters to only return NOC-related documents
             
            results = self.collection.query(
            query_texts=[query],
            n_results=n_results or 5,
            where=meta_filter or None
        )
            # Extract the documents and their metadata from the nestedd result structure 

            # docs_nested = results.get('documents',[])
            # metas_nested = results.get('metadatas', [])

            docs = results.get('documents', [[]])[0]
            metas = results.get('metadatas', [[]])[0]

            # ChromaDB returns results in a nested list — grab the first (and only) inner list

            # docs = docs_nested[0] if docs_nested else []
            # metas = metas_nested[0] if metas_nested else []

            retireved = [
            {
                'document':doc, # The actual NOC Document text 
                'source': meta.get('source','Unknown Source') # Where the document came from 
            }
            for doc, meta in zip(docs, metas)
            ]
            
            return retireved

        except Exception as e:
            logging.getLogger(__name__).exception(f'{method} => Error [{e}]')
