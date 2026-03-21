#By: Tejas Kumar
#Integrating Application Layer Utilities for usage. 

from ApplicationLayer.LogicalOperations import DataUtils, GraphUtils, OptionsUtils, DataTableUtils, ReportGenerator
import requests
import pandas as pd
from datetime import datetime
import calendar
import json

print(f"Importing Dash App Utilities 2")

#region Match Making Generator Functionalities
MATCH_MAKING_API_URI = "http://localhost:8002/query/"

def Send_Compentency_List(Metrics):
    try:

        user_input = [
            Metrics["Numeracy"],
            Metrics["Social Perceptiveness"],
            Metrics["Negotiating"],
            Metrics["Digital Literacy"],
            Metrics["Persuading"],
            Metrics["Evaluation"],
            Metrics["Writing"],
            Metrics["Instructing"],
            Metrics["Active Listening"],
            Metrics["Oral Expression"],
            Metrics["Reading Comprehension"]
        ]

        payload = {
            "compentency_list": user_input
        }

        response = requests.post(MATCH_MAKING_API_URI, json=payload)

        response.raise_for_status()

        data = response.json()
        answer = data.get("answer", "I'm sorry, I couldn't get an answer at this time.")
        return answer
    
    except Exception as e:
        return "I could not provide any matches at this time."


#endregion

#region RAG LLM Functionalities
RAG_API_URI = "http://localhost:8001/query/"
QAA_API_URI = "http://localhost:8001/ask_QAA/"

#Send Query to RAG API and get response
def Send_Query(uer_query: str) -> str:
    try:
        payload = {
            "user_query": uer_query
        }
        response = requests.post(RAG_API_URI, json=payload)
        response.raise_for_status()
        data = response.json()
        answer = data.get("answer", "I'm sorry, I couldn't get an answer at this time.")
        return answer
    except Exception as e:
        print(f"Error sending query to RAG API => {e}")
        return "Error processing the query."

#endregion

#An abstract function for Generating a key pair list for dropdown options in Dash.
def Generate_Options(KeyDict):
    Options = [{'label':val, 'value':choice} for choice,val in KeyDict.items()]

    return Options

#region Instantiating Main Selection Options 
def Get_All_Options_Dicts() -> tuple:
    try:
    
        ProgramDict = OptionsUtils.Get_Program_Options()
        NocOptionsDict = OptionsUtils.Get_NOC_GroupOptions()


        return ProgramDict, NocOptionsDict
    
    except Exception as e:
        print(f'Get_All_Options_Dicts() => {e}')
        return ()
    

ProgramDict, NocOptionsDict = Get_All_Options_Dicts()

print(ProgramDict)

Program_Post_Grad_Employment_Rate_Dict = {
    1: '2020 Employment Rate 6 Months after Graduation',
    2: '2020 Employment Rate 2 Years after Graduation',
    3: '2020 Graduation Rate',
}

Program_Post_Grad_Employment_Rate_Dict_All = {
    1: 'Employment Rate 6 Months after Graduation',
    2: 'Employment Rate 2 Years after Graduation',
    3: 'Graduation Rate',
}
#endregion
#  
#region Functions for Generating Dropdown Options.
def Get_Program_Options():

    return Generate_Options(KeyDict=ProgramDict)

def Get_NOC_Options():

    return Generate_Options(KeyDict=NocOptionsDict)

def Get_Province_Options():
    KeyDict = OptionsUtils.Get_Province_Options()
    return Generate_Options(KeyDict=KeyDict)

def Get_Post_Grad_Employment_Rate_Measure_Options():

    return Generate_Options(KeyDict=Program_Post_Grad_Employment_Rate_Dict)


#endregion

#region Functions for Program Search Page
def Generate_KPI_Comparison(ProgramID, KPI):
    try:
        
        #Data Utils Responsibility 
        df = DataUtils.Get_Program_University_Data(ProgramID=ProgramID)

        kpi_string = Program_Post_Grad_Employment_Rate_Dict_All[KPI]

        df_All_Years = DataUtils.Get_All_Year_KPIs_For_Program(ProgramID=ProgramID, KPI=kpi_string)

        Col_Dict = {str(col): str(col) for col in df_All_Years.columns}
        Tbl_Dict = DataTableUtils.Generate_Dash_Table(data=df_All_Years, Col_Dict=Col_Dict)

        Program = ProgramDict[ProgramID]
        Measure = Program_Post_Grad_Employment_Rate_Dict[KPI]
        df['Program'] = df['ProgramID'].map(ProgramDict)
        df = df.dropna(subset=[Measure])
        df[Measure] = df[Measure].astype(float)

        #Graph Utils Responsibility 

        Map = GraphUtils.Graph_Program_University_Post_Grad_Employment_Rate_Map(Program=Program, Measure=Measure, Data=df)
        Bar = GraphUtils.Graph_Program_University_Post_Grad_Employment_Rate_Bar(Program=Program, Measure=Measure, Data=df)

        return Map, Bar, Tbl_Dict


    except Exception as e:
         print(f'Generate_KPI_Map(Program={ProgramID}, KPI={KPI}) => {e}')
         return {'data': [], 'layout': {'title': f'Post-Grad Employment Rate Data Unavailable for {ProgramDict[ProgramID]}'}}, {'data': [], 'layout': {'title': f'Post-Grad Employment Rate Data Unavailable for {ProgramID[ProgramDict]} Bar'}}, {}

#endregion 

#region Functions for Career Pathway Page 
def Generate_Program_Pathways(Program):
    try:
        df = DataUtils.Get_Program_Occupation_Data(ProgramID=Program)

        Mappings = GraphUtils.Generate_Program_to_Occupation_Mapping(Data=df)

        return Mappings
    
    except Exception as e:
        print(f"Generate_Program_Pathways(Program={Program}) => {e}")
        return {'data': [], 'layout': {'title': f'Program-Occupation Mappings Unavailable for {Program} Bar'}}



def Generate_NOC_History_In_Ontario(NOC_GroupingID):

    try:
        NOC_Occupation = NocOptionsDict[NOC_GroupingID]
        df = DataUtils.Get_NOC_Historical_Data(NOC_GroupingID=NOC_GroupingID)

        History_Graphs = GraphUtils.Generate_NOC_History(Data=df, NOC_Occupation=NOC_Occupation)

        return History_Graphs

    except Exception as e:
        print(f"Generate_NOC_History_In_Ontario(NOC_Code={NOC_GroupingID}) => {e}")
        return {'data': [], 'layout': {'title': f'NOC Employment History Unavailable'}}

def Generate_NOC_Latest_ER_PCT(NOC_GroupingID):
    try:
        df = DataUtils.Get_Latest_ER_NOC_PCT(NOC_GroupingID=NOC_GroupingID)

        NOC_Occupation = NocOptionsDict[NOC_GroupingID]

        ER_Bar = GraphUtils.Generate_NOC_ER_Stat(Data=df, NOC_Occupation=NOC_Occupation)

        return ER_Bar

    except Exception as e:
        print(f"Generate_NOC_Latest_ER_PCT(NOC_Code={NOC_GroupingID}) => {e}")
        return {'data': [], 'layout': {'title': f'NOC Employment History for ERs Unavailable'}}

#endregion


#region Functions for Future Outcomes Page

def Generate_Forecast_Analysis(provinceid: int, noc_groupingid : int):

    df = DataUtils.Get_Provincial_NOC_Forecast(provinceid=provinceid, noc_groupingid=noc_groupingid)

    df_All = DataUtils.Get_NOC_Forecast_All_Provinces(noc_groupingid=noc_groupingid)

    print(f"All Province Data =>\{df_All}")

    Col_Dict = {str(col): str(col) for col in df_All.columns}
    Tbl_Dict = DataTableUtils.Generate_Dash_Table(data=df_All, Col_Dict=Col_Dict)

    


    

    graph = GraphUtils.Generate_Forecast_Graph(Data=df)

    return graph, Tbl_Dict


#endregion 

#region Trend Analysis Functions

def Generate_Provincial_Cluster_Analysis(provinceid: int):
    try:
        today = datetime.today()
        
        month = today.month
        quarter = (today.month - 1) // 3 + 1

        monthlyColName = f'Average Trend for {calendar.month_name[month]}'
        quarterlyColName = f'Average Trend for Q{quarter}'

        df_Combined_Analysis, corCols, ClusterID_ClusterName_Dict =DataUtils.Generate_Processed_Data_Sets(provinceid=provinceid, quarter=quarter, month=month)

        df_Combined_Analysis_Reduced = df_Combined_Analysis[corCols]
        Col_Dict = {str(col): str(col) for col in df_Combined_Analysis_Reduced.columns}

        Tbl_Dict = DataTableUtils.Generate_Dash_Table(data=df_Combined_Analysis_Reduced, Col_Dict=Col_Dict)

        ClusterOptions = Generate_Options(KeyDict=ClusterID_ClusterName_Dict)
        MonthlyTrendGraph = GraphUtils.Generate_Cluster_Trend_Graphs(Data=df_Combined_Analysis, 
                                                                                     monthlyColName=monthlyColName, 
                                                                                     quarterlyColName=quarterlyColName)

        Payload = {
            'Tbl':Tbl_Dict,
            'BarGraph': MonthlyTrendGraph,
            'ClusterOptions':ClusterOptions
        }

        return Payload
        

    except Exception as e:
        print(f"Generate_Provincial_Cluster_Analysis(provinceid={provinceid}) => {e}")
        return {}
    
def Summarize(Cluster, AllSamples):
    try:
        payload = {
            "AllSamples": AllSamples,
            "Cluster":Cluster
        }
        response = requests.post(QAA_API_URI, json=payload)
        response.raise_for_status()
        data = response.json()
        answer = data.get("answer", "I'm sorry, I couldn't get an answer at this time.")
        return answer

    except Exception as e:
        print(f"Summarizes() => {e}")
        return f"Unable to perform Analysis on Cluster [{Cluster}]"

def Generate_Cluster_Set_Analysis(cluster: int):
    try:
        today = datetime.today()
        
        month = today.month
        quarter = (today.month - 1) // 3 + 1

        Cluster_Sample = DataUtils.Get_Cluster_Set(cluster=cluster)

        Cluster_Sample_Copy = Cluster_Sample.copy()
        Cluster_Sample_Copy['seasonal_3'] = round(Cluster_Sample_Copy['seasonal_3'] * 1000, 2)
        Cluster_Sample_Copy['seasonal_6'] = round(Cluster_Sample_Copy['seasonal_6'] * 1000, 2)
        Cluster_Sample_Copy['seasonal_12'] = round(Cluster_Sample_Copy['seasonal_12'] * 1000, 2)

        Cluster_Sample_Json = Cluster_Sample[
            Cluster_Sample['Quarter'] == quarter
                ].set_index('noc_grouping')[[
                    'Year',
                    'Month_Name',
                    'Quarter',
                    'seasonal_3',
                    'seasonal_6',
                    'seasonal_12'
        ]]

        # Convert to dict with noc_grouping as keys
        cluster_dict = (
            Cluster_Sample_Json
                .reset_index()
                .groupby('noc_grouping')
                .apply(lambda x: x.drop(columns='noc_grouping').to_dict(orient='records'))
                .to_dict()
        )

        with open('Sample.json','w') as f:
            json.dump(cluster_dict, f, indent=4)

        Cluster_Summary = Summarize(Cluster=cluster, AllSamples=cluster_dict)

        print(Cluster_Summary)

        Cluster_Viz = GraphUtils.Visualize_Cluster_Series(Data=Cluster_Sample, Quarter=quarter)

        NOC_GroupingID_NOC_Dict = Cluster_Sample.set_index('noc_groupingid')['noc_grouping'].to_dict()

        NOC_Selection_Options = Generate_Options(KeyDict=NOC_GroupingID_NOC_Dict)

        Payload = {
            'Viz':Cluster_Viz,
            'Analysis': Cluster_Summary,
            'NOC_Options': NOC_Selection_Options
        }

        return Payload

    except Exception as e:
        print(f"Generate_Cluster_Set_Analysis(cluster={cluster}) => {e}")
        return {}

def Get_NOC_Occupation_Seasonal_Decomp_Analysis(provinceid, noc_groupingid):
    try:
        
        Payload = DataUtils.Get_NOC_Set(provinceid=provinceid, noc_groupingid=noc_groupingid)

        DecompData = GraphUtils.Graph_NOC_Decompose_Set(Data=Payload['Set'])
        AnnualViz = GraphUtils.Graph_Annual_Growth(Data=Payload['Annual'])
        MonthlyViz = GraphUtils.Graph_Monthly_Growth(Data=Payload['Monthly'])
        QuarterlyViz = GraphUtils.Graph_Quarterly_Growth(Data=Payload['Quart'])

        # Payload = {
        #     'Set': Set,
        #     'Annual':AnnualGrowth,
        #     'Monthly':MonthlyGrowth,
        #     'Quart': QuarterlyGrowth
        # }

        DecompPayload = {
           'Set': DecompData,
           'Annual':AnnualViz,
           'Monthly':MonthlyViz,
           'Quart': QuarterlyViz 
        }


        return DecompPayload

    except Exception as e:
        return {}

#endregion


#region Functions for sending saved json chat history to the report generation module for analysis and insights extraction.

def Send_Chat_To_Report_Generator(Chat_History_Json: dict, reportName: str):

    try:
        
        response = ReportGenerator.generate_report(chat_history_json=Chat_History_Json, reportName=reportName)
        return response
        
    except Exception as e:
        print(f"Error sending chat history to Report Generator => {e}")
        return None

#endregion