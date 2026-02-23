# Abira Demello

import chromadb
import logging
import inspect

# Connects to a local Vector Database and retrieves the most relevant NOC occupation documents based on the student's matched job titles 


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
            client = chromadb.PersistentClient(path="./chroma_db") # load the chromaDB stored
            return client.get_collection(name="Eduction_Planning_Documents")

        except Exception as e:
            logging.getLogger(__name__).exception(f'{method} => Error [{e}]')
    
    def Query(self, MatchedList):
        # Search the vector database for NOC documents relevant to the matched jobs

        method = inspect.currentframe().f_code.co_name
        try:

            # Join the matched job titles into one search string and query the database; 
            # n_results=10 returns the top 10 most relevant documents where={"content":"NOC"} filters to only return NOC-related documents
             
            results = self.collection.query(
            query_texts=[", ".join(MatchedList)],
            n_results=10,
            where={"content":"NOC"}
        )
            # Extract the documents and their metadata from the nestedd result structure 

            docs_nested = results.get('documents',[])
            metas_nested = results.get('metadatas', [])

            # ChromaDB returns results in a nested list — grab the first (and only) inner list

            docs = docs_nested[0] if docs_nested else []
            metas = metas_nested[0] if metas_nested else []

            retireved = [
            {
                'document':doc, # The actual NOC Document text 
                'source': meta['source'] # Where the document came from 
            }
            for doc, meta in zip(docs, metas)
            ]
            
            return retireved

        except Exception as e:
            logging.getLogger(__name__).exception(f'{method} => Error [{e}]')
