import RAG_System as RAG
from fastapi import FastAPI
from pydantic import BaseModel
import Quarterly_Analysis_Agent as QAA

class QueryRequest(BaseModel):
    user_query: str

class QuarterlyAnalysisRequest(BaseModel):
    AllSamples: dict
    Cluster: int

app = FastAPI(title="Educational Assistant Service")


@app.get("/")
def root():
    return {"message": "RAG Education Assisstant API is running"}

@app.post("/query/")
def Query_Rag_System(request: QueryRequest):
    
    answer = RAG.RAG_Query(
        user_query=request.user_query
    )
    
    return {
        "answer": answer,
    }


@app.post("/ask_QAA/")
def Ask_QAA(request: QuarterlyAnalysisRequest):
    answer = QAA.Ask_Agent(AllSamples=request.AllSamples, Cluster=request.Cluster)

    return {
        "answer":answer
    }

