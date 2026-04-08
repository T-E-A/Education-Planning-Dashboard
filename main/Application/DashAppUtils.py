from DataProcessingRequests import DataProcessingRequester
from AIRequests import AIRequester
from DataVizHelpers import GraphUtils, DataTableUtils, OptionsTransformation
from DataVizHelpers import DataFramesCache as Cache
from concurrent.futures import ThreadPoolExecutor
import logging
import pandas as pd
import polars as pl
import numpy as np
import json
from datetime import datetime
import calendar
import inspect

logger = logging.getLogger(__name__)


fee_fields = [
    'Ancillary Fees',
    'Board only (on-campus meal plan)',
    'Books and Supplies',
    'Other Expenses',
    'Room and Board (on-campus)',
    'Room only (on-campus)',
    'Transportation (off-campus)',
    'Tuition Fees'
]



def Load_Options():
    # Service_Check = DataProcessingRequester.Service_Check()

    # if Service_Check['status'] == 200:
    #     All_Options = DataProcessingRequester.Get_Options_Dict()
    #     return All_Options
    # elif Service_Check['status'] == 503:
    #     return {}
    # elif Service_Check['status'] == 500:
    #     return {}
    return DataProcessingRequester.Get_Options_Dict()


All_Options = Load_Options()

print(f'Checking Options()\n{All_Options}')


#region [Dropdown Menu Loaders]
def Get_Pathways_Route_Options():
    return OptionsTransformation.Generate_Options(KeyDict=OptionsTransformation.Pathways_Routes)

def Get_Major_FOS_Options():
    return list(Cache.Major_Options.keys())

def Get_Career_Options():
    return list(Cache.Career_Options.keys())

def Get_Program_Options():
    return OptionsTransformation.Generate_Options(KeyDict=All_Options['Programs'])

def Get_NOC_Options():
    return OptionsTransformation.Generate_Options(KeyDict=All_Options['NOCGrouping'])

def Get_Province_Options():
    return OptionsTransformation.Generate_Options(KeyDict=All_Options['Provinces'])

def Get_Post_Grad_Employment_Rate_Measure_Options():

    return OptionsTransformation.Generate_Options(KeyDict=OptionsTransformation.Program_Post_Grad_Employment_Rate_Dict)

def Get_Student_Type_Options():
    return OptionsTransformation.Generate_Options(KeyDict=OptionsTransformation.Domestic_Or_International)
#endregion


#region [Skill Match Page]
def Send_Compentency_List(Metrics, session_id):
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
            "compentency_list": user_input,
            'session_id': session_id
        }


        response = AIRequester.Ask_Match_Maker_Agent(params=payload)


        answer = response.get("answer", "I'm sorry, I couldn't get an answer at this time.")
        return answer
    
    except Exception as e:
        print("Error with ")
        return "I could not provide any matches at this time."

#endregion

#endregio

#region ['Program Search' Functions]
def Ask_For_Universities_That_Match_Budget(params, frame):
    try:
        
        StudentTypeInt = int(params['StudentType'])

        StudentType = OptionsTransformation.Domestic_Or_International[StudentTypeInt]

        # print(StudentType)
        
        UniversityIDs = AIRequester.Ask_For_University_Budge_Match(params=params)

        # print(f"Number of Retrieved => {len(UniversityIDs)}")

        Sample = Cache.dp_Univeristy_Fees.filter((pl.col('UniversityID').is_in(UniversityIDs))).collect().to_pandas()
        Sample = Sample.sort_values(by=['UniversityID','Year'], ascending=[True,False])
        Sample = Sample.groupby(['UniversityID','University','Expense Type']).head(1)

        StudentDf = pd.DataFrame(frame)
        Merge = Sample.merge(StudentDf, on=['Expense Type'], how='left')
        Merge['Comparison'] = Merge['Input'] - Merge[StudentType]
        conditions = [
            Merge['Comparison'] < 0,
            Merge['Comparison'] > 0,
            Merge['Comparison'] == 0
        ]

        choices = ['Over Budget', 'Under Budget', 'Equal']

        Merge['Comparison_Label'] = np.select(conditions, choices, default='Unknown') 

        MergeReduced = Merge[['University','Expense Type','Input',StudentType,'Comparison','Comparison_Label']]



        MergeReduced = MergeReduced.rename(columns={StudentType:'Fee','Input':'User Budget'})

        result = (
            MergeReduced
                .groupby('University')
                .apply(
                lambda df: df
                .set_index('Expense Type')[['Fee','User Budget','Comparison','Comparison_Label']]
                .to_dict(orient='index')
            )
            .to_dict()
        )

        # print(result)

        Cache.Budget_Data_Cache = result


        MergeReduced.to_csv('Sample.csv',index=False)

        df_pivot = Sample.pivot(index='University', columns='Expense Type', values=StudentType)

        df_pivot['University'] = df_pivot.index
        df_pivot = df_pivot.reset_index(drop=True)

        print(df_pivot)


        Col_Dict = {str(col): str(col) for col in df_pivot.columns}

        return DataTableUtils.Generate_Dash_Table(
            data=df_pivot,
            Col_Dict=Col_Dict
        )

    
    except Exception as e:
        logger.exception(e)
        print(f"Error => {e}")
        return {'data': [], 'layout': {'title': f'Unable to generate Budget comparison due to system error => {e}'}}

def Ask_For_AI_Budget_Analysis():
    try:

        if Cache.Budget_Data_Cache:
        
            params = {
                'Data': Cache.Budget_Data_Cache
            }

            response = AIRequester.Ask_AI_Service_For_Budget_Analysis(params=params)

            answer = response.get('answer', 'Exception')

            print(f"Recieved =>\n{answer}")

            return answer
        else:
            return f"Please input budget variable and find matches first."

    except Exception as e:
        logger.exception(e)
        return f"I cannot answer this at the moment => {e}"
def Load_KPI_Frames():
    try:
        KPI_Data = DataProcessingRequester.Get_KPI_Data()

        Cache.Load_Both_KPI_Frames(latest_data=KPI_Data['Latest'], all_data=KPI_Data['All'])

    except Exception as e:
        logger.exception(e)
        print(e)

def Offload_KPI_Frames():
    try:
        
        Cache.Offload_Both_KPI_Frames()

    except Exception as e:
        logger.exception(e)
        print(e)

def Generate_KPI_Table(ProgramID, KPI):
    try:
        print(type(ProgramID))
        kpi_string = OptionsTransformation.Program_Post_Grad_Employment_Rate_Dict_All[KPI]

        df_All_Years = Cache.dp_All_KPI_Frame.filter(
            pl.col('ProgramID') == int(ProgramID)
        ).to_pandas()

        df = df_All_Years[['Year', 'University', kpi_string]].copy()

        df[kpi_string] = pd.to_numeric(df[kpi_string], errors='coerce')
        df[kpi_string] = round(df[kpi_string] * 100, 2)

        Years = [2017, 2018, 2019, 2020]
        df = df[df['Year'].isin(Years)]

        df_pivot = df.pivot(index='University', columns='Year', values=kpi_string)
        df_pivot['University'] = df_pivot.index
        df_pivot = df_pivot.reset_index(drop=True)
        df_pivot = df_pivot[['University'] + Years]

        Col_Dict = {str(col): str(col) for col in df_pivot.columns}

        return DataTableUtils.Generate_Dash_Table(
            data=df_pivot,
            Col_Dict=Col_Dict
        )
    except Exception as e:
        logger.exception(e)
        print(f"Generate_KPI_Table => [{e}]")

def Generate_KPI_Visuals(ProgramID, KPI):
    try:
        print(type(ProgramID))
        ProgramDict = All_Options['Programs']
        Program = ProgramDict[ProgramID]

        Measure = OptionsTransformation.Program_Post_Grad_Employment_Rate_Dict[KPI]

        df_Latest = Cache.dp_Latest_KPI_Frame.filter(
            pl.col('ProgramID') == int(ProgramID)
        ).to_pandas()

        df = df_Latest.copy()

        df['Program'] = df['ProgramID'].astype(str).map(ProgramDict)
        df[Measure] = df[Measure].astype(float)
        df = df[df[Measure] != 0]
        

        Map = GraphUtils.Graph_Program_University_Post_Grad_Employment_Rate_Map(
            Program=Program,
            Measure=Measure,
            Data=df
        )

        Bar = GraphUtils.Graph_Program_University_Post_Grad_Employment_Rate_Bar(
            Program=Program,
            Measure=Measure,
            Data=df
        )

        return Map, Bar
    except Exception as e:
        logger.exception(e)
        print(f"Generate_KPI_Visuals=>[{e}]")

def Generate_KPI_Comparison(ProgramID, KPI):
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            # future_table = executor.submit(Generate_KPI_Table, ProgramID, KPI)
            future_visuals = executor.submit(Generate_KPI_Visuals, ProgramID, KPI)

            # Tbl = future_table.result()
            Map, Bar = future_visuals.result()    

        return {
            'Map': Map,
            'Bar': Bar,
            # 'Tbl': Tbl
        }

    except Exception as e:
        logger.exception(e)
        print(f"[ERROR] {e}")
        return {}

def Generate_YoY_Comparison(ProgramID: int, KPI: str, UniversityIDs: list[int]):
    try:
        
        Measure = OptionsTransformation.Program_Post_Grad_Employment_Rate_Dict_All[KPI]
        ProgramDict = All_Options['Programs']
        Program = ProgramDict[str(ProgramID)]

        df = Cache.dp_All_KPI_Frame.filter((pl.col("UniversityID").is_in(UniversityIDs)) & (pl.col('ProgramID')==ProgramID)).to_pandas()
        
        df['ds'] = pd.to_datetime(df['Year'], format="%Y")
        

        df = df.sort_values(by=['UniversityID','ds'], ascending=[True, False])

        df = df.groupby('UniversityID').head(5)

        print(df[['University','ds',Measure]])



        df[Measure] = df[Measure].astype(float)

        df = df[df[Measure] != 0.0]

        df_Reduced = df[['UniversityID','University','ds',Measure]]

        payload = {
            'data': df_Reduced,
            'program':Program,
            'measure': Measure
        }

        return GraphUtils.Graph_YoY_KPI(params=payload)

    except Exception as e:
        logger.info(e)
        print(f"Error [{e}]")
        return None
#endregion 

#region ['Career Pathways' Functions] 
def Generate_Pathways(Route: int, Focus:str, tree: bool = True):
    try:

        if Route == 1:
            Data = Cache.dp_Career_Pathways.filter(
                pl.col(OptionsTransformation.Pathways_Agg_Operation[Route]) == Focus
            ).collect().to_pandas()

            Cache.dp_Career_Pathways_Sub_Select = pl.from_pandas(Data)

            Graph = GraphUtils.Generate_Pathways_FieldofStudy_Career_Graph(
                Data=Data,
                FieldOfStudy=Focus,
                tree=tree
            )

            SelectList = Data['UnitGroup'].unique().tolist()
        
        elif Route == 2:
            Data = Cache.dp_Career_Pathways.filter(
                (pl.col(OptionsTransformation.Pathways_Agg_Operation[Route]) == Focus)
                & (pl.col('MajorFieldOfStudyParentID') != 1)
            ).collect().to_pandas()

            Cache.dp_Career_Pathways_Sub_Select = pl.from_pandas(Data)

            Graph = GraphUtils.Generate_Pathways_Career_to_FieldOfStudy_Graph(
                Data=Data,
                Career=Focus,
                tree=tree
            )

            SelectList = Data['MajorFieldOfStudy'].unique().tolist()

        


        
        return {
            'Viz': Graph,
            'SelectList': SelectList
        }
    


    except Exception as e:
        logger.exception(e)
        return {
            'Viz': {'data': [], 'layout': {'title': f'Unable to generate Pathways => {e}'}},
            'SelectList': []
        }


def Generate_Pathway_Aggregate(Route: int, Focus: str ,SubFocus: str):
    try:
        if Cache.dp_Career_Pathways_Sub_Select is not None:
            if Route == 1:
                Data = Cache.dp_Career_Pathways_Sub_Select.filter(
                    pl.col('UnitGroup') == SubFocus
                ).to_pandas()

        

            elif Route == 2:
                Data = Cache.dp_Career_Pathways_Sub_Select.filter(
                    pl.col('MajorFieldOfStudy') == SubFocus
                ).to_pandas()

            
            Cache.dp_Career_Pathways_Second_Sub_Select = pl.from_pandas(Data)

            return GraphUtils.Generate_Distribution_Graph(
                    Data=Data,
                    Focus=Focus,
                    SubFocus=SubFocus
                )


        else:
            return {'data': [], 'layout': {'title': f'Unable to generate distribution Graph'}}
    
    except Exception as e:
        logger.exception(e)
        return {'data': [], 'layout': {'title': f'Unable to generate distribution Graph => {e}'}}


def Ask_AI_For_Income_Analysis(session_id: str):
    try:
        if Cache.dp_Career_Pathways_Second_Sub_Select is not None:
            Data = Cache.dp_Career_Pathways_Second_Sub_Select.group_by(['MajorFieldOfStudy','UnitGroup',
                                                                       'HighestEducation',
                                                                       'Age',
                                                                       'Gender',
                                                                       ]).agg(
                pl.col('AvgIncome').max().alias('MaxAvgIncome'),
                pl.col('AvgIncome').min().alias('MinAvgIncome'),
                pl.col('AvgIncome').quantile(0.25).alias('25thPercentileAvgIncome'),
                pl.col('AvgIncome').median().alias('MeanAvgIncome'),
                pl.col('AvgIncome').quantile(0.75).alias('75thPercentileAvgIncome'),
                pl.col('AvgIncome').std().alias('StdDevAvgIncome'),
                pl.len().alias('SampleSize')

                
                ).to_pandas()

            Data = Data.dropna()
            
            Data = Data.rename(columns={'UnitGroup':'OccupationGroup'})

            DataNested = Data.to_dict(orient='records')

            params = {
                'data': DataNested,
                'session_id': session_id
            }

            response = AIRequester.Ask_AI_Service_For_Income_Distribution_Analysis(params=params)

            return response.get('answer', 'I cannot provide an income distribution analysis at this time.')
    except Exception as e:
            return f"I cannot provide an income distribution analysis at this time => {e}"

def Ask_Pathways_Agent_A_Question(user_query, session_id):
    try:
        
        params = {
            'user_query':user_query,
            'session_id':session_id
        }

        response = AIRequester.Ask_Pathways_Agent(params=params)

        answer = response.get('answer','AI Service ran into an error.')

        return answer

    except Exception as e:
        logger.exception(e)
        return f"I am sorry I cannot answer this due to application error => {e}"

def Generate_Program_Pathways(ProgramID):
    try:
        ProgramID = int(ProgramID)
        Data = DataProcessingRequester.Get_Program_To_NOC_Data(ProgramID=ProgramID)

        df = Cache.Create_Frame(Data=Data).to_pandas()

        Mappings = GraphUtils.Generate_Program_to_Occupation_Mapping(Data=df)

        Payload = {
            'Mappings': Mappings
        }

        return Payload

    except Exception as e:
        return {
            'Mappings': None
        }
    
def Generate_NOC_Provincial_Analysis_Graph(df, NOC_Occupation):
    try:
        
        History_Graphs = GraphUtils.Generate_NOC_History(Data=df, NOC_Occupation=NOC_Occupation)
        return History_Graphs

    except Exception as e:
        print(e)
        return {'data': [], 'layout': {'title': f'NOC Employment History Unavailable'}}

def Generate_Latest_ER_PCT(df, NOC_Occupation):
    try:
        
        ER_Bar = GraphUtils.Generate_NOC_ER_Stat(Data=df, NOC_Occupation=NOC_Occupation)
        return ER_Bar

    except Exception as e:
        print(f'Generate_Latest_ER_PCT=>{e}')
        return {'data': [], 'layout': {'title': f'NOC Employment History for ERs Unavailable'}}
    
def Generate_NOC_History(NOC_GroupingID, provinceID='35'):
    try:
        NOC_Occupation = All_Options['NOCGrouping'][NOC_GroupingID]
        DGUID = All_Options['Provinces_DGUID'][provinceID]

        provinceID = int(provinceID)
        NOC_GroupingID = int(NOC_GroupingID)       

        DataNested = DataProcessingRequester.Get_NOC_Historical(NOC_GroupingID=NOC_GroupingID, 
                                                                provinceid=provinceID,
                                                                DGUID=DGUID
                                                                )
        df_Prov = Cache.Create_Frame(Data=DataNested['PROV']).to_pandas()
        df_ER = Cache.Create_Frame(Data=DataNested['ER']).to_pandas()

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_prov = executor.submit(Generate_NOC_Provincial_Analysis_Graph, df_Prov, NOC_Occupation)
            future_er = executor.submit(Generate_Latest_ER_PCT, df_ER, NOC_Occupation)

            ProvGraph = future_prov.result()
            ERGraph = future_er.result()

        return {
            'PROV': ProvGraph,
            'ER': ERGraph
        }
    
    except Exception as e:
        print(f'Generate_NOC_History() => {e}')
        return {
            'PROV': {'data': [], 'layout': {'title': f'NOC Employment History Unavailable'}},
            'ER': {'data': [], 'layout': {'title': f'NOC Employment History for ERs Unavailable'}}
        }
#endregion


#region ['Future Outcomes' Functions]

def Generate_Provincial_Forecast_Viz(df, noc_group, province):
    try:
    
        graph = GraphUtils.Generate_Forecast_Graph(Data=df, noc_group=noc_group, province=province)
        return graph

    except Exception as e:
        return {'data': [], 'layout': {'title': f'NOC Employment Forecast Unavailable Due to systme error [{e}]'}}
    
def Generate_All_Province_Outlook(df):
    try:
        
        Col_Dict = {str(col): str(col) for col in df.columns}
        Tbl_Dict = DataTableUtils.Generate_Dash_Table(data=df, Col_Dict=Col_Dict)

        return Tbl_Dict

    except Exception as e:
        return None

def Ask_AI_For_Forecast_Analysis(session_id, noc_groupingid: str):
    try:
    
        NOC_Occupation_Grouping = All_Options['NOCGrouping'][str(noc_groupingid)]

        Evaluation_Data = Cache.dp_Forecast_Evals.filter(
            pl.col('noc_groupingid')==int(noc_groupingid)
        ).select(['r2','euclidean distance','mae','rmse','mse','Average Actual',
                  'CV RMSE','CV MAE','MAPE','Coverage','province_shorthand']).collect().to_pandas().to_dict(orient='records')
        
        Future_Projections = Cache.dp_YoY_Forecast_Cache.to_pandas().to_dict(orient='records')

        params = {
            'session_id':session_id,
            'Evaluation_Data': Evaluation_Data,
            'Future_Projections': Future_Projections,
            'NOC_Occupation_Group': NOC_Occupation_Grouping
        }

        for key in params:
            print(f"{key} => {type(params[key])}\n")

        try:
            answer = AIRequester.Ask_For_Forecast_Analysis(params=params)

            return answer.get('answer','Unable to get answer.')
        except Exception as e:
            return "I cannot answer this at this time."

    except Exception as e:
        return f"Unable to generate analysis because of {e}"

def Generate_Forecast_Analysis(provinceid: int, noc_groupingid: int):
    try:
        provinceid = int(provinceid)
        noc_groupingid = int(noc_groupingid)
        
        DataNested = DataProcessingRequester.Get_NOC_Forecast(provinceid=provinceid, NOC_GroupingID=noc_groupingid)

        noc_occupation = All_Options['NOCGrouping'][str(noc_groupingid)]
        province = All_Options['Provinces'][str(provinceid)]

        df_Forecast = Cache.Create_Frame(Data=DataNested['PROV']).to_pandas()
        Cache.dp_Forecast_Cache = pl.from_pandas(df_Forecast)


        df_All = Cache.Create_Frame(Data=DataNested['ALL']).to_pandas()

        try:

            
            
            df_Long = df_All.melt(
                id_vars=['Province'],
                value_vars=['2026','2027','2028','2029'],
                var_name='Year',
                value_name='Estimate'
            )
            
            df_Long = df_Long.dropna(subset=['Year'])
            df_Long['Year'] = df_Long['Year'].astype(int)
            df_Long = df_Long.sort_values(by=['Province','Year'], ascending=True)


        except Exception as e:
            print(f"Cannt do it => {e}")

        Cache.dp_YoY_Forecast_Cache = pl.from_pandas(df_All)

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_prov_forecast = executor.submit(Generate_Provincial_Forecast_Viz, df_Forecast, noc_occupation, province)
            future_outlook = executor.submit(Generate_All_Province_Outlook, df_All)
            future_estimates = executor.submit(GraphUtils.Generate_Estimate_Graph, df_Long, noc_occupation)

            Viz = future_prov_forecast.result()
            Viz_2 = future_estimates.result()
            Tbl = future_outlook.result()

        return {
            'Tbl':Tbl,
            'Viz': Viz,
            'Viz_2':Viz_2
        }

    except Exception as e:

        return {
            'Tbl': {},
            'Viz': {'data': [], 'layout': {'title': f'NOC Employment Forecast Unavailable Due to systme error [{e}]'}},
            'Viz_2': {'data': [], 'layout': {'title': f'Unable to do estimate graph'}},
        }


#endregion


#region [ChatBot]
def Ask_Chat_Agent(params):
    try:
        
        answer = AIRequester.Ask_ChatBot(params=params)

        return answer.get('answer', "No Response due to Application error.")

    except Exception as e:
        logger.exception(e)



#endregion



#region [Trend Analysis Page]
def Get_Cluster_Quarterly_Trend_Graph(df_Cluster_Comp_Table, quarterlyColName):
    try:
        print(f"dutils calling graph")
        return GraphUtils.Generate_Cluster_Quarterly_Trend_Graphs(Data=df_Cluster_Comp_Table,
                                                                  quarterlyColName=quarterlyColName
                                                                  )

    except Exception as e:
        print(f'dutil exception {e}')
        logger.exception(e)
        return {'data': [], 'layout': {'title': f'Trend Analysis Unavaiable due to system error => {e}'}}

def Generate_Cluster_Comparison_Table(df_Cluster_Comp_Table, quarterlyColName):
    try:
        
        df_Table_Reduce = df_Cluster_Comp_Table[['Cluster','Number of NOC Groupings',quarterlyColName,'Quarter Trend Segment']].sort_values(by=quarterlyColName, ascending=False)
        Col_Dict = {str(col): str(col) for col in df_Table_Reduce.columns}
        return DataTableUtils.Generate_Dash_Table(Col_Dict=Col_Dict, data=df_Table_Reduce)
    
    except Exception as e:
        return DataTableUtils.Generate_Dash_Table(Col_Dict=None, data=None, errorMessage=e)

def Generate_Cluster_Options(Cluster_Dict_Options):
    try:
        
        return OptionsTransformation.Generate_Options(KeyDict=Cluster_Dict_Options)

    except Exception as e:
        return OptionsTransformation.Generate_Options(KeyDict=None, errorMessage=e)

def Get_Cluster_Analysis_Set_For_Province(provinceid: str):
    try:
        
        today = datetime.today()
        
        month = today.month
        quarter = (today.month - 1) // 3 + 1

        Cluster_Analysis_Dict = DataProcessingRequester.Get_Province_Clustered_Series(
            provinceid=int(provinceid),
            month=month,
            quarter=quarter
        )

        Cache.dp_All_Clusters_Seasonal_Decomp = pl.DataFrame(Cluster_Analysis_Dict.get('FullSet',[]))
        Cache.Cluster_Dict_Options = Cluster_Analysis_Dict.get('ClusterDict',{})
        df_Cluster_Comp_Table = pd.DataFrame(Cluster_Analysis_Dict.get('AnalysisSet',[]))

        quarterlyColName = f'Average Trend for Q{quarter}'

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_viz = executor.submit(Get_Cluster_Quarterly_Trend_Graph, df_Cluster_Comp_Table, quarterlyColName)
            future_tbl = executor.submit(Generate_Cluster_Comparison_Table, df_Cluster_Comp_Table, quarterlyColName)
            future_options = executor.submit(Generate_Cluster_Options, Cache.Cluster_Dict_Options)

            BarGraph = future_viz.result()
            Tbl = future_tbl.result()
            ClusterOptions = future_options.result()

        return {
            'Tbl': Tbl,
            'BarGraph': BarGraph,
            'ClusterOptions':ClusterOptions
        }

    except Exception as e:
        logger.exception(e)
        Payload = {
            'Tbl': None,
            'BarGraph':None,
            'ClusterOptions': None,
        }

        return Payload


def Ask_AI_TS_Cluster_Analysis(cluster: int, Cluster_Sample_Dict: dict, errorMessage=None):
    try:
        
        params= {
            'AllSamples':Cluster_Sample_Dict,
            'Cluster':int(cluster)
        }

        print(f"Samples: {type(params['AllSamples'])}\nCluster: {type(cluster)}")

        answer = AIRequester.Ask_For_Cluster_Quarterly_Analysis(params=params)

        return answer.get('answer','Could not generate analysis at this time.')

    except Exception as e:
        return f"I cannot generate cluster analysis because of {e}"

def Generate_TS_Cluster_Viz(Cluster_Sample: pd.DataFrame, Quarter: int, errorMessage=None):
    try:
    
        return GraphUtils.Visualize_Cluster_Series(Data=Cluster_Sample, Quarter=Quarter, errorMessage=errorMessage)

    except Exception as e:
        logger.exception(e)
        return GraphUtils.Visualize_Cluster_Series(Data=None, Quarter=None, errorMessage=e)

def Generate_NOC_Selection_Options(NOC_Selection_Options: dict, errorMessage=None):
    try:
        
        return OptionsTransformation.Generate_Options(KeyDict=NOC_Selection_Options, errorMessage=errorMessage)

    except Exception as e:
        return OptionsTransformation.Generate_Options(KeyDict=None, errorMessage=str(e))

def Generate_Cluster_Analysis_Set(cluster: int):
    method = inspect.currentframe().f_code.co_name
    try:

        logger.info(f"{method}() Called")
        
        today = datetime.today()

        quarter = (today.month - 1) // 3 + 1

        logger.info(f'{method}=> getting Cluster Sample')
        Cluster_Sample = Cache.dp_All_Clusters_Seasonal_Decomp.filter((pl.col('trend_cluster')==int(cluster))
                                                                      & (pl.col('Year') <= 2024)
                                                                      & (pl.col('Year') >= 2022)
                                                                      ).to_pandas().sort_values(by=['noc_groupingid','datestamp'], ascending=True)
        
        logger.info(f"{method} =>\n{Cluster_Sample.head()}")
        logger.info(f"{method} => transforming seasonal")

        Cluster_Sample_Copy = Cluster_Sample.copy()
        Cluster_Sample_Copy['seasonal_3'] = round(Cluster_Sample_Copy['seasonal_3'] * 1000, 2)
        Cluster_Sample_Copy['seasonal_6'] = round(Cluster_Sample_Copy['seasonal_6'] * 1000, 2)
        Cluster_Sample_Copy['seasonal_12'] = round(Cluster_Sample_Copy['seasonal_12'] * 1000, 2)

        Cluster_Sample_Json = Cluster_Sample_Copy[Cluster_Sample_Copy['Quarter']==quarter].set_index('noc_grouping')[[
            'Year',
            'Month_Name',
            'Quarter',
            'seasonal_3',
            'seasonal_6',
            'seasonal_12'
        ]]
        
        logger.info(f'{method} =>\n{Cluster_Sample_Copy.columns}')
        logger.critical(f'{method} => Test point of failure')
        # Cluster_Sample_Dict = (
        #     Cluster_Sample_Copy.reset_index()
        #         .groupby('noc_grouping')
        #         .apply(lambda x: x.drop(columns='noc_grouping').to_dict(orient='records'))
        #         .to_dict()
        # )

        Cluster_Sample_Dict = (
            Cluster_Sample_Copy.groupby('noc_grouping')[['Year',
            'Month_Name',
            'Quarter',
            'seasonal_3',
            'seasonal_6',
            'seasonal_12']].apply(lambda x: x.to_dict(orient='records')).to_dict()
        )

        logger.critical(f"{method} Cluster_Sample_Dict:\n{Cluster_Sample_Dict}")

        NOC_GroupingID_NOC_Dict = Cluster_Sample.set_index('noc_groupingid')['noc_grouping'].to_dict()

        with ThreadPoolExecutor(max_workers=3) as executor:

            future_viz = executor.submit(Generate_TS_Cluster_Viz, Cluster_Sample, quarter)
            future_analysis = executor.submit(Ask_AI_TS_Cluster_Analysis, cluster, Cluster_Sample_Dict)
            future_options = executor.submit(Generate_NOC_Selection_Options, NOC_GroupingID_NOC_Dict)
        
            Viz = future_viz.result()
            Analysis = future_analysis.result()
            NOC_Options = future_options.result()

        return {
            'Viz': Viz,
            'Analysis': Analysis,
            'NOC_Options': NOC_Options
        }


        

    except Exception as e:
        logger.exception(e)
        return {
            'Viz': Generate_TS_Cluster_Viz(Cluster_Sample=None, Quarter=None, errorMessage=str(e)),
            'Analysis': Ask_AI_TS_Cluster_Analysis(cluster=None, Cluster_Sample_Dict=None, errorMessage=str(e)),
            'NOC_Options': Generate_NOC_Selection_Options(NOC_Selection_Options=None, errorMessage=str(e))
        }

def Aggregate_NOC_Seasonal_Decomp_Analysis_Set(df_Filtered: pd.DataFrame):
    try:
        
        Set = df_Filtered.to_pandas().sort_values(by='datestamp', ascending=True)

        AnnualGrowth = df_Filtered.filter(pl.col('Year')>=2020).group_by(['Year']).agg(
            (pl.col('seasonal_12').sum()).round(2).alias('Growth')
        ).to_pandas().sort_values(by='Year', ascending=True)

        MonthlyGrowth = df_Filtered.filter(pl.col('Year')>=2020).group_by(['Month_Num','Month_Name']).agg(
            (pl.col('seasonal_12').sum()).round(2).alias('Growth')
        ).to_pandas().sort_values(by='Month_Num', ascending=True)

        QuarterlyGrowth = df_Filtered.filter(pl.col('Year')>=2020).group_by(['Quarter']).agg(
            (pl.col('seasonal_12').sum()).round(2).alias('Growth')
        ).to_pandas().sort_values(by='Quarter', ascending=True)

        QuarterlyGrowth['Quarter_Name'] = QuarterlyGrowth['Quarter'].apply(lambda x: f"Q{x}")

        choices = ['Increase', 'Decrease', 'No Change']
        conditions_annual = [
            AnnualGrowth['Growth'] > 0,
            AnnualGrowth['Growth'] < 0,
            AnnualGrowth['Growth'] == 0
        ]

        conditions_monthly = [
             MonthlyGrowth['Growth'] > 0,
             MonthlyGrowth['Growth'] < 0,
             MonthlyGrowth['Growth'] == 0
        ]

        conditions_quarterly = [
             QuarterlyGrowth['Growth'] > 0,
             QuarterlyGrowth['Growth'] < 0,
             QuarterlyGrowth['Growth'] == 0
        ]

        AnnualGrowth['Growth Segment'] = np.select(conditions_annual, choices, default='No Data').astype(str)
        MonthlyGrowth['Growth Segment'] = np.select(conditions_monthly, choices, default='No Data').astype(str)
        QuarterlyGrowth['Growth Segment'] = np.select(conditions_quarterly, choices, default='No Data').astype(str)

        Payload = {
            'Set': Set,
            'Annual':AnnualGrowth,
            'Monthly':MonthlyGrowth,
            'Quart': QuarterlyGrowth
        }

        return Payload

    except Exception as e:
        logger.exception(e)
        return {}

def Generate_NOC_Seasonal_Decomp_Analysis(provinceid: str, noc_groupingid: str):
    try:

        df_Filtered = Cache.dp_All_Clusters_Seasonal_Decomp.filter((pl.col('noc_groupingid')==int(noc_groupingid))
                                                                   & (pl.col('provinceid')==int(provinceid))
                                                                   & (pl.col('Year')>=2020)
                                                                   & (pl.col('Year')<2025)
                                                                   )

        Aggregates = Aggregate_NOC_Seasonal_Decomp_Analysis_Set(df_Filtered=df_Filtered)

        DecompData = Aggregates.get('Set',pd.DataFrame())
        AnnualData = Aggregates.get('Annual',pd.DataFrame())
        MonthlyData = Aggregates.get('Monthly',pd.DataFrame())
        QuarterlyData = Aggregates.get('Quart',pd.DataFrame())

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_set = executor.submit(GraphUtils.Graph_NOC_Decompose_Set, DecompData)
            future_annual = executor.submit(GraphUtils.Graph_Annual_Growth, AnnualData)
            future_monthly = executor.submit(GraphUtils.Graph_Monthly_Growth, MonthlyData)
            future_quarterly = executor.submit(GraphUtils.Graph_Quarterly_Growth, QuarterlyData)

            Set = future_set.result()
            Annual = future_annual.result()
            Monthly = future_monthly.result()
            Quart = future_quarterly.result()
        
        return {
            'Set': Set,
            'Annual': Annual,
            'Monthly': Monthly,
            'Quart': Quart
        }

    except Exception as e:

        return {
            'Set': GraphUtils.Graph_NOC_Decompose_Set(Data=None, errorMessage=str(e)),
            'Annual': GraphUtils.Graph_Annual_Growth(Data=None, errorMessage=str(e)),
            'Monthly': GraphUtils.Graph_Monthly_Growth(Data=None, errorMessage=str(e)),
            'Quart': GraphUtils.Graph_Quarterly_Growth(Data=None, errorMessage=str(e))
        }

#endregion
