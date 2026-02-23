# Ed Wang - 2026-02-22
# API endpoint for the Match making system.

import Match_Making_System as MatchMaking 
from fastapi import FastAPI
from pydantic import BaseModel
import json


class Input_List(BaseModel):
    compentency_list : list[int] 


app = FastAPI(title="Matching Making Service")

@app.get("/")
def root():
    return {"message": "Education Planning Dashboard - Matching Maker API is running"}

@app.post("/query/")
def Query_Match_Making_System(request: Input_List):
    
    answer = MatchMaking.Get_All_Matches(
        user_input=request.compentency_list
    )
    
    return {"answer": answer}