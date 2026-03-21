#By: Ed Wang 
#Manipulating Data 

from DataTransportationLayer.DataServiceAPI import DataService
import pandas as pd 
import polars as pl
import numpy as np
import calendar


df_Decomp_Set = pd.DataFrame()
dp_Decomp_Set = pl.from_pandas(df_Decomp_Set)
dp_Filtered_Set = pl.DataFrame()

Latest_KPI_Rename_Dict = {
    'employment_rate_2_years_after_graduating_field': '2020 Employment Rate 2 Years after Graduation',
    'employment_rate_6_months_after_graduating_field': '2020 Employment Rate 6 Months after Graduation',
    'graduation_rate': '2020 Graduation Rate',
    'university':'University',
    'programcategoryid':'ProgramID',
    'universityid':'UniversityID',
    'lat':'Lat',
    'lon':'Lon',
    'year':'Year'
}

KPI_Rename_Dict = {
    'employment_rate_2_years_after_graduating_field': 'Employment Rate 2 Years after Graduation',
    'employment_rate_6_months_after_graduating_field': 'Employment Rate 6 Months after Graduation',
    'graduation_rate': 'Graduation Rate',
    'university':'University',
    'programcategoryid':'ProgramID',
    'universityid':'UniversityID',
    'lat':'Lat',
    'lon':'Lon',
    'year':'Year'
}


Program_Links_Rename_Dict = {
    'programid' : 'ProgramID',
    'program' : 'Program',
    'broad_occupation_category':'Broad Occupation Category',
    'sub_major_group': 'Sub-Major Group',
    'unit_group_occupation': 'Unit Group Occupation'
}

Province_Employment_History_Dict = {
    'datestamp': 'ds',
    'employment':'Employment (Persons in Thousands)',
    'employment_moving_average':'3-Month Moving Average',
    'employment_upper_band':'Upper Band',
    'employment_lower_band': 'Lower Band'
}

Economic_Region_Employment_Dict = {
    'economicregion':'Economic Region',
    'employment_pct_change': 'Monthly PCT',
}

def Get_Program_University_Data(ProgramID):
    try:
        df = DataService.RequestLatestKPIForProgram(ProgramID=ProgramID)

        #We need to rename the columns so that there more readable. 
        df = df.rename(columns=Latest_KPI_Rename_Dict)

        return df

    except Exception as e:
        print(f"Get_Program_University_Data(ProgramID={ProgramID})=>{e}")
        return pd.DataFrame()

def Get_Program_Occupation_Data(ProgramID):
    try:
        df = DataService.RequestProgramNOCLinks(ProgramID=ProgramID)

        df = df.rename(columns=Program_Links_Rename_Dict)
        
        return df
    except Exception as e:
        print(f"Get_Program_Occupation_Data(ProgramID={ProgramID})=>{e}")
        return pd.DataFrame()

def Get_NOC_Historical_Data(NOC_GroupingID,DGUID='2021A000235'):
    try:
        df = DataService.RequestNOCGroupLaborStatistics(NOC_GroupingID=NOC_GroupingID,DGUID=DGUID)
        
        df = df.rename(columns=Province_Employment_History_Dict)

        return df

    except Exception as e:
        print(f"Get_NOC_Historical_Data(NOC_GroupingId={NOC_GroupingID},DGUID={DGUID}) => {e}")
        return pd.DataFrame()
    
def Get_Latest_ER_NOC_PCT(NOC_GroupingID, provinceID=35):
    try:
        df = DataService.RequestEconomicRegionEmploymentEstimate(NOC_GroupingID=NOC_GroupingID, ProvinceID=provinceID)
        
        df['employment_pct_change'] = pd.to_numeric(df['employment_pct_change'], errors='coerce')
        conditions = [
            df['employment_pct_change'] > 0,
            df['employment_pct_change'] < 0,
            df['employment_pct_change'] == 0
        ]
        choices = ['Increase', 'Decrease', 'No Change']
        df['Change'] = np.select(conditions, choices, default='No Data').astype(str)
        
        df = df.rename(columns=Economic_Region_Employment_Dict)



        return df

    except Exception as e:
        print(f"Get_Latest_ER_NOC_PCT(NOC_GroupingId={NOC_GroupingID},provinceID={provinceID}) => {e}")
        return pd.DataFrame()


def Get_All_Year_KPIs_For_Program(ProgramID, KPI):
    try:
        df = DataService.RequestKPIForProgram(ProgramID=ProgramID)

        df = df.rename(columns=KPI_Rename_Dict)

        df_Reduced = df[['Year','University', KPI]].sort_values(by=['Year','University'], ascending=[False,True])
        df_Reduced[KPI] = pd.to_numeric(df_Reduced[KPI], errors='coerce')
        df_Reduced[KPI] = round(df_Reduced[KPI] * 100, 2)
        Years = [2017,2018,2019,2020]
        df_Reduced = df_Reduced[df_Reduced['Year'].isin(Years)]
        df_pivot = df_Reduced.pivot(index='University', columns='Year', values=KPI)

        
       
        df_pivot['University'] = df_pivot.index
        df_pivot = df_pivot.reset_index(drop=True)
        
        
        df_pivot = df_pivot[['University'] + Years]

        print(df_pivot)
        print(df_pivot.columns)

        return df_pivot

    except Exception as e:
        print(f"Get_All_Year_KPIs_For_Program(ProgramID={ProgramID}) => {e}")
        return pd.DataFrame()
    


#region Forecasting Analysis Data Getters 

def Get_Provincial_NOC_Forecast(provinceid : int, noc_groupingid : int) -> pd.DataFrame:
    try:
        df = DataService.Request_Provincial_NOC_Forecast(provinceID=provinceid, noc_groupingid=noc_groupingid)

        df['yhat'] = df['yhat'].round(2)
        df['yhat_lower'] = df['yhat_lower'].round(2)
        df['yhat_upper'] = df['yhat_upper'].round(2)
        return df

    except Exception as e:
        print(f"Get_Provincial_NOC_Forecast(provinceid : {provinceid}, noc_groupingid : {noc_groupingid}) => {e}")
        return pd.DataFrame()


def Get_NOC_Forecast_All_Provinces(noc_groupingid : int) -> pd.DataFrame:
    try:
        df = DataService.Request_All_Province_NOC_Forecast(noc_groupingid=noc_groupingid)

        df = df.rename(columns={'province_shorthand':'Province','year':'Year'})

        df = df[df['Year']>=2026]

        # print(df)
        

        Years = sorted(df['Year'].unique())

        # print(f"Years =>\n{Years}")

        df = df.sort_values(by=['provinceid','Year'], ascending=[True,True])

        df_pivot = df.pivot(index='Province', columns='Year', values='Employment Forecast')

        df_pivot['Province'] = df_pivot.index
        df_pivot = df_pivot.reset_index(drop=True)

        df_pivot = df_pivot[['Province'] + Years]

        
        return df_pivot
    

    except Exception as e:
        print(f"Get_NOC_Forecast_All_Provinces(noc_groupingid : {noc_groupingid}) => {e}")
        return pd.DataFrame()
#endregion 


#region Trend Analysis Pre-Processing 
def Transform_Set(Data: pd.DataFrame):
    try:
        
        Data['datestamp'] = pd.to_datetime(Data['datestamp'])
        Data['Year'] = Data['datestamp'].dt.year
        Data['Month_Num'] = Data['datestamp'].dt.month
        Data['Month_Name'] = Data['datestamp'].dt.month_name()
        Data['Quarter'] = Data['datestamp'].dt.quarter


        return Data

    except Exception as e:
        print(f"Transform_Set() => {e}")
        return Data

def Set_Decomp_Set(provinceid):
    try:
        
        global df_Decomp_Set
        global dp_Decomp_Set

        df_Decomp_Set = DataService.RequestionSeasonalDecomp(provinceid=provinceid)
        df_Decomp_Set = Transform_Set(Data=df_Decomp_Set)
        dp_Decomp_Set = pl.from_pandas(df_Decomp_Set)

    except Exception as e:
        print(f"Set_Decomp_Set(provinceid={provinceid}) => {e}")
        return

def Filter_Set():
    try:
        
        global dp_Filtered_Set

        dp_Filtered_Set = dp_Decomp_Set.filter((pl.col('Year')>= 2022) & (pl.col('Year')<= 2024))

        

    except Exception as e:
        print(f"Filter_Set() => {e}")
        return pl.DataFrame()

def Generate_Cluster_Monthly_Comparison(month):
    try:


        
        df_Comp = dp_Filtered_Set.filter(pl.col('Month_Num')==month).group_by('trend_cluster').agg(
            pl.col('noc_groupingid').n_unique().alias('Number of NOC Groupings'),
            (pl.col('seasonal_12').mean()*1000).round(3).alias(f'Average Trend for {calendar.month_name[month]}')
        ).to_pandas().sort_values(by=f'Average Trend for {calendar.month_name[month]}', ascending=False).reset_index(drop=True)

        df_Comp = df_Comp.rename(columns={'trend_cluster':'Cluster'})

        coreCols = df_Comp.columns.tolist()
        
        conditions = [
            df_Comp[f'Average Trend for {calendar.month_name[month]}'] > 0,
            df_Comp[f'Average Trend for {calendar.month_name[month]}'] < 0,
            df_Comp[f'Average Trend for {calendar.month_name[month]}'] == 0
        ]
        choices = ['Increase', 'Decrease', 'No Change']
        df_Comp['Month Trend Segment'] = np.select(conditions, choices, default='No Data').astype(str)

        



        return df_Comp, coreCols

    except Exception as e:
        print(f"Generate_Cluster_Monthly_Comparison(month={month}) => {e}")
        return pd.DataFrame(), []

def Generate_Cluster_Quarterly_Comparison(quarter, corCols):
    try:
        
        df_Comp = dp_Filtered_Set.filter(pl.col('Quarter')==quarter).group_by('trend_cluster').agg(
            (pl.col('seasonal_3').mean()*1000).round(3).alias(f'Average Trend for Q{quarter}')
        ).to_pandas().sort_values(by=f'Average Trend for Q{quarter}', ascending=False).reset_index(drop=True)
        
        corCols.append(f'Average Trend for Q{quarter}')
        df_Comp = df_Comp.rename(columns={'trend_cluster':'Cluster'})

        conditions = [
            df_Comp[f'Average Trend for Q{quarter}'] > 0,
            df_Comp[f'Average Trend for Q{quarter}'] < 0,
            df_Comp[f'Average Trend for Q{quarter}'] == 0
        ]
        choices = ['Increase', 'Decrease', 'No Change']
        df_Comp['Quarter Trend Segment'] = np.select(conditions, choices, default='No Data').astype(str)

        return df_Comp



    except Exception as e:
        print(f"Generate_Cluster_Quarterly_Comparison(quarter={quarter}) => {e}")
        return pd.DataFrame()

def Generate_Processed_Data_Sets(provinceid, quarter, month):
    try:
        
        Set_Decomp_Set(provinceid=provinceid)
        Filter_Set()

        df_Montly_Comp, corCols = Generate_Cluster_Monthly_Comparison(month=month)
        df_Quarterly_Comp = Generate_Cluster_Quarterly_Comparison(quarter=quarter, corCols=corCols)

        # print(f"Monthly Comp =>\n{df_Montly_Comp}")
        # print(f"Quarterly Comp =>\n{df_Quarterly_Comp}")

        df_Combined_Analysis = df_Montly_Comp.merge(df_Quarterly_Comp, on=['Cluster'], how='inner')
        df_Combined_Analysis['Cluster Name'] = df_Combined_Analysis['Cluster'].apply(lambda x: f"Cluster [{x}]")

        df_Combined_Analysis = df_Combined_Analysis.sort_values(by=[f'Average Trend for Q{quarter}'], ascending=False)

        # print(f"Combined =>\n{df_Combined_Analysis}")

        ClusterID_ClusterName_Dict = df_Combined_Analysis.set_index('Cluster')['Cluster Name'].to_dict()

        return df_Combined_Analysis, corCols, ClusterID_ClusterName_Dict

    except Exception as e:
        print(f"Generate_Processed_Data_Sets(provinceid={provinceid}, quarter={quarter}, month={month}) => {e}"), corCols, {}

def Get_Cluster_Set(cluster):
    try:
        
        Cluster_Sample = dp_Decomp_Set.filter((pl.col('trend_cluster')==cluster)
                                              & (pl.col('Year') <= 2024)
                                              & (pl.col('Year') >= 2022)
                                              ).to_pandas().sort_values(by=['noc_groupingid','datestamp'], ascending=True)

        print(Cluster_Sample)
        return Cluster_Sample

    except Exception as e:
        print(f"Get_Cluster_Set(cluster={cluster})=> {e}")
        return pd.DataFrame()

def Get_NOC_Set(provinceid, noc_groupingid):
    try:
        df_Filtered = dp_Decomp_Set.filter((pl.col('provinceid')==provinceid) 
                                   & (pl.col('noc_groupingid')==noc_groupingid)
                                   & (pl.col('Year') <= 2024)
                                   )
        Set = df_Filtered.to_pandas().sort_values(by='datestamp', ascending=True)
        
        AnnualGrowth = df_Filtered.filter(pl.col('Year')>=2020).group_by(['Year']).agg(
            (pl.col('seasonal_12').mean() * 1000).round(2).alias('Growth')
        ).to_pandas().sort_values(by='Year', ascending=True)

        MonthlyGrowth = df_Filtered.filter(pl.col('Year')>=2020).group_by(['Month_Num','Month_Name']).agg(
            (pl.col('seasonal_12').mean() * 1000).round(2).alias('Growth')
        ).to_pandas().sort_values(by='Month_Num', ascending=True)

        QuarterlyGrowth = df_Filtered.filter(pl.col('Year')>=2020).group_by(['Quarter']).agg(
            (pl.col('seasonal_12').mean() * 1000).round(2).alias('Growth')
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
        print(f"Get_NOC_Set(provinceid={provinceid}, noc_groupingid={noc_groupingid})")
        return pd.DataFrame()
#endregion 