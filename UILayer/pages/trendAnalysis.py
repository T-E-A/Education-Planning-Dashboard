from dash import dcc, html, callback ,Input, State, Output, dash_table
import dash 
import dash_bootstrap_components as dbc

from UILayer.DashAppUtilities import (Get_Province_Options, Generate_Provincial_Cluster_Analysis, Generate_Cluster_Set_Analysis, Get_NOC_Occupation_Seasonal_Decomp_Analysis)


dash.register_page(
    __name__,
    path="/trendAnalysis",
    name="Trend Analysis"
    )

layout = dbc.Container(
    [

        # ---------- PAGE TITLE ----------
        dbc.Row(
            dbc.Col(
                html.H2(
                    "Trend Analysis",
                    className="text-start mt-3 mb-4",
                    style={"font-size": "35px"}
                ),
                width=12
            )
        ),

        # ---------- PROVINCE SELECTORS ----------
        dbc.Card(
            dbc.CardBody(
                [
                    html.Label(
                        "Select a Province to start:",
                        className="fw-bold mb-2",
                        style={"font-size": "20px"}
                    ),
                    dcc.Dropdown(
                        id='Select_Province',
                        options=Get_Province_Options(),
                        multi=False,
                        className="mb-4"
                    ),

                ]
            ),
            className="shadow-sm mb-4"
        ),

        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                             html.Div(
                                 
                             
                             dash_table.DataTable(
                                 id='Tbl_Cluster_Trends',
                                sort_action='native',
                                sort_mode='multi',
                                style_cell={'textAlign': 'left'},  
                                style_table={'height': '500px', 'overflowY': 'auto'},
                                column_selectable="multi",
                                selected_rows=[],
                                filter_action='native',
                                fixed_rows={'headers': True},
                                fixed_columns={'headers': True}
            
                            ), className='dbc dbc-row-selectable dash-header'),
                        ),
                        className="shadow-sm h-100"
                    ),
                    width=6
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(id='Graph_Monthly_Trend')
                        ),
                        className="shadow-sm h-100"
                    ),
                    width=6
                ),
                
               
            ],
            className="mb-5"
        ),

        dbc.Row(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Label(
                            "Select a Cluster for Analysis:",
                            className="fw-bold mb-2",
                            style={"font-size": "20px"}
                        ),
                        dcc.Dropdown(
                            id='Select_Cluster',
                            multi=False,
                            className="mb-4"
                        ),
                    ]
                ),
                className="shadow-sm mb-4"
            ),
        ]
    ),

    dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        dcc.Graph(id='Graph_Cluster_Series', style={"height": "900px"})
                    ),
                    className="shadow-sm h-100"
                ),
                width=6
            ),

            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        dcc.Markdown(
                            id="Chat_Quarterly_Analysis",
                            children="",
                            style={
                                "height": "900px",
                                "overflowY": "auto",
                                "whiteSpace": "pre-wrap",
                            },
                        ),
                    ),
                    className="shadow-sm h-100"
                ),
                width=6
            ),
        ],
        className="shadow-sm mb-4"
    ),

    dbc.Row(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Label(
                            "Select a NOC Grouping for Analysis:",
                            className="fw-bold mb-2",
                            style={"font-size": "20px"}
                        ),
                        dcc.Dropdown(
                            id='Select_NOC',
                            multi=False,
                            className="mb-4"
                        ),
                    ]
                ),
                className="shadow-sm mb-4"
            ),

            dbc.Row(
            [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        dcc.Graph(id='Graph_Decomposition', style={"height": "1200px"})
                    ),
                    className="shadow-sm h-100"
                ),
                width=7
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        children=[
                        dcc.Graph(id='Graph_Yearly_Comparison', style={"height":"400px"}),
                        dcc.Graph(id='Graph_Monthly_Comparison', style={"height":"400px"}),
                        dcc.Graph(id='Graph_Quarterly_Comparison', style={"height":"400px"})]
                    ),
                    className="shadow-sm h-100"
                ),
                width=5
            )

        ],
        className="shadow-sm mb-4"
    ),
        ]
    ),

        


        html.Div(id='Output_Sample', children='Check')

    ],
    fluid=True,
    className="p-4"
)


@callback(
        Output('Tbl_Cluster_Trends','columns'),
        Output('Tbl_Cluster_Trends','style_cell'),
        Output('Tbl_Cluster_Trends','data'),
        Output('Tbl_Cluster_Trends','style_data_conditional'),
        Output('Graph_Monthly_Trend', 'figure'),
        Output('Select_Cluster','options'),
        Input('Select_Province','value'),
    )
def Update_Cluster_Comparison(provinceid):
    if provinceid:
        Payload = Generate_Provincial_Cluster_Analysis(provinceid=provinceid)

        Tbl_Dict = Payload['Tbl']
        Bar_Graph = Payload['BarGraph']
        ClusterOptions = Payload['ClusterOptions']
        
        
        if len(Tbl_Dict) == 0:
            return tuple([dash.no_update] * 4), Bar_Graph, ClusterOptions
        
        if len(Tbl_Dict) > 0:
            data = Tbl_Dict['Data']
            cols = Tbl_Dict['Cols']
            style = Tbl_Dict['Style']
            styleCond = Tbl_Dict['StyleCond']
            return cols, style, data, styleCond, Bar_Graph, ClusterOptions

    else:
        return tuple([dash.no_update] * 6)

@callback(
    Output('Graph_Cluster_Series','figure'),
    Output("Chat_Quarterly_Analysis", "children"),
    Output('Select_NOC','options'),
    Input('Select_Cluster','value')
)
def Update_Cluster_Series(cluster):
    if cluster:
        Payload = Generate_Cluster_Set_Analysis(cluster=cluster)

        Cluster_Viz = Payload['Viz']
        Cluster_Summary = Payload['Analysis']
        Cluster_NOC_Options = Payload['NOC_Options']
        
        return Cluster_Viz, Cluster_Summary, Cluster_NOC_Options
    else:
        return tuple([dash.no_update] * 3)

@callback(
    Output('Graph_Decomposition','figure'),
    Output('Graph_Yearly_Comparison','figure'),
    Output('Graph_Monthly_Comparison','figure'),
    Output('Graph_Quarterly_Comparison','figure'),
    State('Select_Province','value'),
    Input('Select_NOC','value'),

)

def Update_Decomp_Series(provinceid, noc_groupingid):
    if provinceid and noc_groupingid:

        Payload =  Get_NOC_Occupation_Seasonal_Decomp_Analysis(provinceid=provinceid, noc_groupingid=noc_groupingid)

        # DecompPayload = {
        #    'Set': DecompData,
        #    'Annual':AnnualViz,
        #    'Monthly':MonthlyViz,
        #    'Quart': QuarterlyViz 
        # }


        Decomp = Payload['Set']
        Annual = Payload['Annual']
        Monthly = Payload['Monthly']
        Quart = Payload['Quart']

        return Decomp, Annual, Monthly, Quart
    else:
       return tuple([dash.no_update] * 4)