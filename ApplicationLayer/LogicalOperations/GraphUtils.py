#By: Abira Esther Demello
#Graphing the Data 

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import pandas as pd

def Graph_Program_University_Post_Grad_Employment_Rate_Map(Program, Measure, Data):
    try:
        scatter_map = px.scatter_map(
            title=f'{Program} - {Measure} Mapped by University',
            data_frame=Data,
            lat='Lat',
            lon='Lon',
            height=900,
            size=Measure, 
            color=Measure,
            color_continuous_scale=['#692618','#183B69','#186930'],
            text='University',
            hover_data=['ProgramID','Program','UniversityID','University']
        )

        scatter_map.update_layout(
            title_font=dict(size=16),  # Set the title font size
            font=dict(size=15),  # Set general font size for labels and axis titles
            hoverlabel=dict(
                font_size=20  # Set font size for hover data
            ),
            xaxis=dict(
                title_font=dict(size=18),  # Set x-axis title font size
                tickfont=dict(size=12)  # Set x-axis tick font size
            ),
            yaxis=dict(
                title_font=dict(size=18),  # Set y-axis title font size
                tickfont=dict(size=12)  # Set y-axis tick font size
            ),
            mapbox=dict(
                center=dict(lat=Data['Lat'].mean(), lon=Data['Lon'].mean()),  # Center the map on the data
                zoom=9,  # Set a zoom level that shows both primary and secondary points
  
            ),
            coloraxis_showscale=False
        )

        del Data

        return scatter_map


    except Exception as e:
         print(f"Graph_Program_University_Post_Grad_Employment_Rate_Map() => {e}")
         return {'data': [], 'layout': {'title': f'Post-Grad Employment Rate Data Unavailable for {Program} Map'}}

def Graph_Program_University_Post_Grad_Employment_Rate_Bar(Program, Measure, Data):
    try:

        # print(Measure)
        Data = Data.sort_values(by=Measure, ascending=False)
        bar = px.bar(
            title=f'{Program} - {Measure} Comparison by University',
            data_frame=Data,
            x='University',
            y=Measure,
            height=900,
            color=Measure,
            color_continuous_scale=['#692618','#183B69','#186930'],
            # text='University',
            hover_data=['ProgramID','Program','UniversityID','University'],
            template='ggplot2'
        )

        bar.update_layout(
            title_font=dict(size=16),  # Set the title font size
            font=dict(size=15),  # Set general font size for labels and axis titles
            hoverlabel=dict(
                font_size=20  # Set font size for hover data
            ),
            xaxis=dict(
                title_font=dict(size=18),  # Set x-axis title font size
                tickfont=dict(size=12)  # Set x-axis tick font size
            ),
            yaxis=dict(
                title_font=dict(size=18),  # Set y-axis title font size
                tickfont=dict(size=12)  # Set y-axis tick font size
            ),
            coloraxis_showscale=False
        )

        return bar

    

    except Exception as e:
        print(f"Graph_Program_University_Post_Grad_Employment_Rate_Bar() => {e}")
        return {'data': [], 'layout': {'title': f'Post-Grad Employment Rate Data Unavailable for {Program} Bar'}}

def Generate_Program_to_Occupation_Mapping(Data):
    try:

        Mappings = px.treemap(
            # title=f'Career Paths per Program',
            data_frame=Data,
            path=['Program','Broad Occupation Category','Sub-Major Group','Unit Group Occupation'],
            height=900,
            template='ggplot2',
            color_discrete_sequence=['white'],
            
            
            
        )
        Mappings.update_traces(
            marker=dict(
            line=dict(color="#1F5896", width=2),
            colorscale=None,
            cmin=None,
            cmax=None
                ),
        )

        Mappings.update_layout(
             font=dict(
        size=18,                
        ),
            title=dict(
        font=dict(size=28),
        x=0.5
        ),
         hoverlabel=dict(
                font_size=20 
            ),

        )

        del Data
        
        return Mappings
    
    

    except Exception as e:
        print(f"Generate_Program_to_Occupation_Mapping() => {e}")
        return {'data': [], 'layout': {'title': f'Program-Occupation Mappings Unavailable'}}
    

def Generate_NOC_History(Data, NOC_Occupation):
    try:
        History_Graph = px.line(
            # title=f"'{NOC_Occupation}' Employment History in Ontario",
            height=1000,
            template='ggplot2',
        )

        History_Graph.add_trace(
            go.Scatter(
                x=Data['ds'],
                y=Data['Employment (Persons in Thousands)'],
                mode='lines',
                line=dict(color='#172B4A', width=4.5),
                name='Empoyment (Persons in Thousands)',
            )
        )

        History_Graph.add_trace(
            go.Scatter(
                x=Data['ds'],
                y=Data['3-Month Moving Average'],
                mode='lines',
                line=dict(color="#9D3D39", width=4.5, dash='dash'),
                name='Quarterly Moving Average'
            )
        )

        History_Graph.add_traces(
            go.Scatter(
            x=Data['ds'],
            y=Data['Upper Band'],
            mode='lines',
            line=dict(width=0),  
            showlegend=False,
            hoverinfo='skip'
            )
        )

        History_Graph.add_traces(
        go.Scatter(
            x=Data['ds'],
            y=Data['Lower Band'],
            mode='lines',
            line=dict(width=0), 
            fill='tonexty',      
            fillcolor='rgba(219, 118, 119, 0.2)', 
             hoverinfo='skip',
            name='Employment Volatility'
            )
            )



        History_Graph.update_layout(
            title_font=dict(size=24),  
            font=dict(size=15),  
            hoverlabel=dict(
                font_size=15 
            ),
            xaxis=dict(
                title='Date (Monthly)',
                title_font=dict(size=20),  
                tickfont=dict(size=18)  
            ),
            yaxis=dict(
                title='Employment (Persons in Thousands)',
                title_font=dict(size=20),  
                tickfont=dict(size=18)  
            ),
             legend=dict(
                orientation='h',       
                yanchor='bottom',     
                y=-0.3,               
                xanchor='center',      
                 x=0.5,                 
                font=dict(size=16)     
            ),
            hovermode='x unified',
        )

        return History_Graph
    

    except Exception as e:
        print(f"Generate_NOC_History() => {e}")
        return {'data': [], 'layout': {'title': f'NOC Employment History Unavailable'}}
    

def Generate_NOC_ER_Stat(Data, NOC_Occupation):
    try:
        Data = Data.sort_values(by='Monthly PCT', ascending=False)


        Color_Discrete_Map = {
            'Increase':'#186930',
            'No Change':'#183B69',
            'Decrease': '#692618'
        }

        Bar = px.bar(
            height=1000,
            template='ggplot2',
            data_frame=Data,
            y='Economic Region',
            x='Monthly PCT',
            text='Monthly PCT',
            color='Change',
            color_discrete_map=Color_Discrete_Map,
        )

        Bar.update_layout(
            title_font=dict(size=24),  
            font=dict(size=15),  
            hoverlabel=dict(
                font_size=20  
            ),
            xaxis=dict(
                title='Employment Change as %',
                title_font=dict(size=20),  
                tickfont=dict(size=18)  
            ),
            yaxis=dict(
                title='Economic Regions in Ontario',
                title_font=dict(size=20),  
                tickfont=dict(size=18)  
            ),
             legend=dict(
                orientation='h',      
                yanchor='bottom',      
                y=-0.3,                
                xanchor='center',      
                 x=0.5,                 
                font=dict(size=16)     
            )
        )

        return Bar

    except Exception as e:
        print(f"Generate_NOC_ER_Stat() => {e}")
        return {'data': [], 'layout': {'title': f'NOC Employment History for ERs Unavailable'}}
    


#region Forecast Graphs 

def Generate_Forecast_Graph(Data):
    try:
        
        future_data = Data[Data['set'] == 'Future']
        test_data = Data[Data['set'].isin(['Validation','Test'])]

        line = px.line(
            title='Forecast (2024 - 2029)',
            height=1000,
            template='ggplot2',
        )

        line.add_trace(go.Scatter(
            x=test_data['datestamp'], 
            y=test_data['y'],
            name='Actual',
            line=dict(color='#172B4A', width=4.5),
            mode='lines'
        ))

        line.add_trace(go.Scatter(
            x=future_data['datestamp'], 
            y=future_data['yhat'],
            name='Forecast',
            line=dict(color="#5B160F", width=4.5, dash='dot'),
            mode='lines'
        ))

        line.add_traces(
            go.Scatter(
            x=future_data['datestamp'],
            y=future_data['yhat_upper'],
            mode='lines',
            line=dict(width=0),  
            showlegend=False,
            hoverinfo='skip'
            )
        )

        line.add_traces(
        go.Scatter(
            x=future_data['datestamp'],
            y=future_data['yhat_lower'],
            mode='lines',
            line=dict(width=0), 
            fill='tonexty',      
            fillcolor='rgba(117, 43, 58, 0.2)', 
             hoverinfo='skip',
            name='Forecast Uncertainty Interval'
            )
            )
        


        line.add_trace(go.Scatter(
            x=test_data['datestamp'], 
            y=test_data['yhat'],
            name='Predicted',
            line=dict(color="#2B7561", width=4.5, dash='dash')
        ))

        line.add_traces(
            go.Scatter(
            x=test_data['datestamp'],
            y=test_data['yhat_upper'],
            mode='lines',
            line=dict(width=0),  
            showlegend=False,
            hoverinfo='skip'
            )
        )

        line.add_traces(
        go.Scatter(
            x=test_data['datestamp'],
            y=test_data['yhat_lower'],
            mode='lines',
            line=dict(width=0), 
            fill='tonexty',      
            fillcolor='rgba(43, 117, 97, 0.2)', 
             hoverinfo='skip',
            name='Tested Uncertainty Interval'
            )
            )


        line.update_layout(
            title_font=dict(size=24),  
            font=dict(size=15),  
            hoverlabel=dict(
                font_size=15 
            ),
            xaxis=dict(
                title='Date (Monthly)',
                title_font=dict(size=20),  
                tickfont=dict(size=18)  
            ),
            yaxis=dict(
                title='Employment (Persons in Thousands)',
                title_font=dict(size=20),  
                tickfont=dict(size=18)  
            ),
             legend=dict(
                orientation='h',       
                yanchor='bottom',     
                y=-0.3,               
                xanchor='center',      
                 x=0.5,                 
                font=dict(size=16)     
            ),
            hovermode='x unified',
        )

        return line





    except Exception as e:
        print(f"Generate_Forecast_Graph() => {e}")
        return {'data': [], 'layout': {'title': f'NOC Employment Forecast Unavailable'}}


#endregion 


#region Trend Analysis Graphs 



def Generate_Cluster_Trend_Graphs(Data, monthlyColName, quarterlyColName):
    try:
        
        color_map = {
            'Increase': '#227A53',
            'Decrease': '#5E1722',
            'No Change': '#17355E'
        }

        Data = Data.sort_values(by=quarterlyColName, ascending=True)

        bar = px.bar(
            data_frame=Data,
            y='Cluster Name',
            x=quarterlyColName,
            template='ggplot2',
            color_discrete_map=color_map,
            color='Quarter Trend Segment'
        )

        bar.update_layout(
            title_font=dict(size=24),  
            font=dict(size=15),  
            hoverlabel=dict(
                font_size=15 
            ),
            yaxis=dict(
                title='Cluster',
                title_font=dict(size=20),  
                tickfont=dict(size=18)  
            ),
            xaxis=dict(
                title='Quarterly Trend (Past 3 Years)',
                title_font=dict(size=20),  
                tickfont=dict(size=18)  
            ),
             legend=dict(
                orientation='h',       
                yanchor='bottom',     
                y=-0.3,               
                xanchor='center',      
                 x=0.5,                 
                font=dict(size=16)     
            ),
            
        )



        return bar 

    except Exception as e:
        print(f'Graph_Cluster_Trend_Graphs')
        return {'data': [], 'layout': {'title': f'Trend Analysis Unavaiable due to system error => {e}'}}


def Visualize_Cluster_Series(Data, Quarter):
    try:

        quarter_map = {
            1: (1, 3),
            2: (4, 6),
            3: (7, 9),
            4: (10, 12)
        }

        years = Data['Year'].unique()
        start_month, end_month = quarter_map[Quarter]

        shapes = []
        for year in years:
            start_date = pd.Timestamp(year=year, month=start_month, day=1)
            end_date = pd.Timestamp(year=year, month=end_month, day=1)

            shapes.append(
        dict(
            type="rect",
            xref="x",
            yref="paper",   
            x0=start_date,
            x1=end_date,
            y0=0,
            y1=1,
            fillcolor="#878894",
            opacity=0.4,
            layer="below",
            line_width=0
        )
    )
        
        Data['seasonal_3'] = Data['seasonal_3'] * 1000

        

        line = px.line(
            data_frame=Data,
            x='datestamp',
            y='seasonal_3',
            color='noc_grouping',
            template='ggplot2',
            height=900
        )

        line.update_layout(
            title_font=dict(size=24),  
            font=dict(size=15),  
            hoverlabel=dict(
                font_size=15 
            ),
            xaxis=dict(
                title='Date (Monthly)',
                title_font=dict(size=20),  
                tickfont=dict(size=18)  
            ),
            yaxis=dict(
                title='Quarterly Trend YoY',
                title_font=dict(size=20),  
                tickfont=dict(size=18)  
            ),
            hovermode='x unified',
            showlegend=False,
            shapes=shapes
        )

        return line


    except Exception as e:
        print(f'Visualize_Cluster_Series() => {e}')
        return {'data': [], 'layout': {'title': f'Cluster Set Unavailable due to system error => {e}'}}


def Graph_NOC_Decompose_Set(Data):
    try:
        

        fig = make_subplots(
            rows=6,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=[
            "Employment in Thousands",
            "Trend",
            "Annual Seasonality",
            "Semi-Annual Seasonality",
            "Quarterly Seasonality",
            "Residuals"
        
        ]
    )

        fig.add_trace(
            go.Scatter(
                x=Data['datestamp'],
                y=Data['observed'],
                mode="lines",
                name="Employment in Thousands",
                line=dict(color='#13256B', width=2.5)
            ),
            row=1,
            col=1
        )

        # Trend
        fig.add_trace(
            go.Scatter(
                x=Data['datestamp'],
                y=Data['trend'],
                mode="lines",
                name="Trend",
                line=dict(color='#13256B', width=2.5, dash='dash')
        ),
        row=2,
        col=1
        )

        # Seasonal
        fig.add_trace(
            go.Scatter(
                x=Data['datestamp'],
                y=Data['seasonal_12'],
                mode="lines",
                name="Annual Seasonality",
                line=dict(color='#064241', width=2.5)
        ),
        row=3,
        col=1
        )

        fig.add_trace(
            go.Scatter(
                x=Data['datestamp'],
                y=Data['seasonal_6'],
                mode="lines",
                name="Semi-Annual Seasonality",
                line=dict(color='#17615E', width=2.5)
            ),
        row=4,
        col=1
        )

        fig.add_trace(
            go.Scatter(
                x=Data['datestamp'],
                y=Data['seasonal_3'],
                mode="lines",
                name="Quarterly Seasonality",
                line=dict(color="#42B3AF", width=2.5)
            ),
        row=5,
        col=1
        )

        fig.add_trace(
            go.Scatter(
                x=Data['datestamp'],
                y=Data['resid'],
                mode="markers",
                name="Residuals",
                marker=dict(color="#580A0A", size=8)
            ),
            row=6,
            col=1
        )



        fig.update_layout(
            title="Seasonal Decomposition",
            showlegend=False
        )
        fig.update_layout(template='ggplot2')

        return fig

    except Exception as e:
        return {'data': [], 'layout': {'title': f'NOC Decompostion Unavailable due to system error => {e}'}}

def Graph_Annual_Growth(Data):
    try:
        color_map = {
            'Increase': '#227A53',
            'Decrease': '#5E1722',
            'No Change': '#17355E'
        }

        bar = px.bar(
            data_frame=Data,
            x='Year',
            y='Growth',
            template='ggplot2',
            color='Growth Segment',
            color_discrete_map=color_map

        )

        bar.update_layout(
            title_font=dict(size=24),  
            font=dict(size=15),  
            hoverlabel=dict(
                font_size=9 
            ),
            xaxis=dict(
                title='Year',
                title_font=dict(size=14),  
                tickfont=dict(size=12)  
            ),
            yaxis=dict(
                title='YoY Annual Growth',
                title_font=dict(size=14),  
                tickfont=dict(size=12)  
            ),
            showlegend=False,
            )
        
        return bar


    except Exception as e:
        return {'data': [], 'layout': {'title': f'NOC Yearly Growth Unavailable due to system error => {e}'}}

def Graph_Monthly_Growth(Data):
    try:
        color_map = {
            'Increase': '#227A53',
            'Decrease': '#5E1722',
            'No Change': '#17355E'
        }

        
        Data = Data.sort_values(by='Month_Num', ascending=True)

        
        Data['Month_Name'] = pd.Categorical(
            Data['Month_Name'],
            categories=Data.sort_values('Month_Num')['Month_Name'].tolist(),
            ordered=True
        )

        month_order = Data.sort_values('Month_Num')['Month_Name'].tolist()

        bar = px.bar(
            data_frame=Data,
            x='Month_Name',
            y='Growth',
            template='ggplot2',
            color='Growth Segment',
            color_discrete_map=color_map,
            category_orders={"Month_Name": month_order}

        )

        bar.update_layout(
            title_font=dict(size=24),  
            font=dict(size=15),  
            hoverlabel=dict(
                font_size=9 
            ),
            xaxis=dict(
                title='Month',
                title_font=dict(size=14),  
                tickfont=dict(size=12)  
            ),
            yaxis=dict(
                title='YoY Monthly Growth',
                title_font=dict(size=14),  
                tickfont=dict(size=12)  
            ),
            showlegend=False,
            )
        
        return bar


    except Exception as e:
        return {'data': [], 'layout': {'title': f'NOC Monthly Growth Unavailable due to system error => {e}'}}

def Graph_Quarterly_Growth(Data):
    try:
        color_map = {
            'Increase': '#227A53',
            'Decrease': '#5E1722',
            'No Change': '#17355E'
        }

        Data = Data.sort_values(by='Quarter', ascending=True)

        Data['Quarter_Name'] = pd.Categorical(
            Data['Quarter_Name'], 
            categories=Data['Quarter_Name'].unique(), 
            ordered=True
        )

        q_order = Data.sort_values('Quarter')['Quarter_Name'].tolist()
        bar = px.bar(
            data_frame=Data,
            x='Quarter_Name',
            y='Growth',
            template='ggplot2',
            color='Growth Segment',
            color_discrete_map=color_map,
            category_orders={"Quarter_Name": q_order}

        )

        bar.update_layout(
            title_font=dict(size=24),  
            font=dict(size=15),  
            hoverlabel=dict(
                font_size=9 
            ),
            xaxis=dict(
                title='Quarter',
                title_font=dict(size=14),  
                tickfont=dict(size=12)  
            ),
            yaxis=dict(
                title='YoY Quarterly Growth',
                title_font=dict(size=14),  
                tickfont=dict(size=12)  
            ),
            showlegend=False,
            )
        
        return bar


    except Exception as e:
        return {'data': [], 'layout': {'title': f'NOC Quarterly Growth Unavailable due to system error => {e}'}}
#endregion