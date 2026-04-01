from dash import dcc, html, callback ,Input, State, Output, dash_table
import dash 
import dash_bootstrap_components as dbc

from DashAppUtils import (
    Get_Province_Options,
    Get_Cluster_Analysis_Set_For_Province,
    Generate_Cluster_Analysis_Set,
    Generate_NOC_Seasonal_Decomp_Analysis
)

dash.register_page(
    __name__,
    path="/trendAnalysis",
    name="Trend Analysis"
)

# ---------- VISIBILITY ----------
HIDDEN = {"display":"none"}
VISIBLE = {"display":"block"}

LABEL_STYLE = {
    "fontSize": "20px",
    "color": "white"
}

layout = dbc.Container([

    # ---------- TITLE ----------
    dbc.Row(
        dbc.Col(
            html.H2(
                "Trend Analysis",
                className="text-start mt-3 mb-4",
                style={"fontSize": "35px","color":"white"}
            ),
            width=12
        )
    ),

    # ---------- PROVINCE SELECT ----------
    dbc.Card(
        dbc.CardBody([
            html.Label(
                "Select a Province to start:",
                className="fw-bold mb-2",
                style=LABEL_STYLE
            ),
            dcc.Dropdown(
                id='Select_Province',
                options=Get_Province_Options(),
                multi=False,
                className="mb-4"
            ),
        ]),
        className="shadow-sm mb-4"
    ),

    # ---------- CLUSTER OVERVIEW ----------
    html.Div(
        id="cluster-overview-section",
        style=HIDDEN,
        children=[

            dbc.Row([

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Loading(
                                type="circle",
                                children=html.Div(
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
                                    ),
                                    className='dbc dbc-row-selectable dash-header'
                                )
                            )
                        ),
                        className="shadow-sm h-100"
                    ),
                    width=6
                ),

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Loading(
                                type="circle",
                                children=dcc.Graph(id='Graph_Monthly_Trend')
                            )
                        ),
                        className="shadow-sm h-100"
                    ),
                    width=6
                ),

            ], className="mb-5"),

        ]
    ),

    # ---------- CLUSTER SELECT ----------
    html.Div(
        id="cluster-select-section",
        style=HIDDEN,
        children=[

            dbc.Card(
                dbc.CardBody([
                    html.Label(
                        "Select a Cluster for Analysis:",
                        className="fw-bold mb-2",
                        style=LABEL_STYLE
                    ),
                    dcc.Dropdown(
                        id='Select_Cluster',
                        multi=False,
                        className="mb-4"
                    ),
                ]),
                className="shadow-sm mb-4"
            )

        ]
    ),

    # ---------- CLUSTER ANALYSIS ----------
    html.Div(
        id="cluster-analysis-section",
        style=HIDDEN,
        children=[

            dbc.Row([

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Loading(
                                type="circle",
                                children=dcc.Graph(
                                    id='Graph_Cluster_Series',
                                    style={"height": "900px"}
                                )
                            )
                        ),
                        className="shadow-sm h-100"
                    ),
                    width=6
                ),

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Loading(
                                type="circle",
                                children=dcc.Markdown(
                                    id="Chat_Quarterly_Analysis",
                                    children="",
                                    style={
                                        "height": "900px",
                                        "overflowY": "auto",
                                        "whiteSpace": "pre-wrap",
                                    }
                                )
                            )
                        ),
                        className="shadow-sm h-100"
                    ),
                    width=6
                ),

            ], className="mb-4")

        ]
    ),

    # ---------- NOC SELECT ----------
    html.Div(
        id="noc-select-section",
        style=HIDDEN,
        children=[

            dbc.Card(
                dbc.CardBody([
                    html.Label(
                        "Select a NOC Grouping for Analysis:",
                        className="fw-bold mb-2",
                        style=LABEL_STYLE
                    ),
                    dcc.Dropdown(
                        id='Select_NOC',
                        multi=False,
                        className="mb-4"
                    ),
                ]),
                className="shadow-sm mb-4"
            )

        ]
    ),

    # ---------- DECOMPOSITION ----------
    html.Div(
        id="decomp-section",
        style=HIDDEN,
        children=[

            dbc.Row([

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Loading(
                                type="circle",
                                children=dcc.Graph(
                                    id='Graph_Decomposition',
                                    style={"height": "1200px"}
                                )
                            )
                        ),
                        className="shadow-sm h-100"
                    ),
                    width=7
                ),

                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Loading(
                                type="circle",
                                children=[
                                    dcc.Graph(id='Graph_Yearly_Comparison', style={"height":"400px"}),
                                    dcc.Graph(id='Graph_Monthly_Comparison', style={"height":"400px"}),
                                    dcc.Graph(id='Graph_Quarterly_Comparison', style={"height":"400px"})
                                ]
                            )
                        ),
                        className="shadow-sm h-100"
                    ),
                    width=5
                )

            ], className="mb-4")

        ]
    ),

], fluid=True, className="p-4")

# ---------- SHOW CLUSTER OVERVIEW ----------
@callback(
    Output("cluster-overview-section","style"),
    Output("cluster-select-section","style"),
    Input("Select_Province","value")
)
def show_cluster_section(province):
    if province:
        return VISIBLE, VISIBLE
    return HIDDEN, HIDDEN


# ---------- SHOW CLUSTER ANALYSIS ----------
@callback(
    Output("cluster-analysis-section","style"),
    Output("noc-select-section","style"),
    Input("Select_Cluster","value")
)
def show_cluster_analysis(cluster):
    if cluster:
        return VISIBLE, VISIBLE
    return HIDDEN, HIDDEN


# ---------- SHOW DECOMPOSITION ----------
@callback(
    Output("decomp-section","style"),
    Input("Select_NOC","value")
)
def show_decomp(noc):
    if noc:
        return VISIBLE
    return HIDDEN


# ---------- ORIGINAL CALLBACKS ----------

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
        Payload = Get_Cluster_Analysis_Set_For_Province(provinceid=provinceid)

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
        Payload = Generate_Cluster_Analysis_Set(cluster=cluster)

        return (
            Payload['Viz'],
            Payload['Analysis'],
            Payload['NOC_Options']
        )
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

        Payload = Generate_NOC_Seasonal_Decomp_Analysis(
            provinceid=provinceid,
            noc_groupingid=noc_groupingid
        )

        return (
            Payload['Set'],
            Payload['Annual'],
            Payload['Monthly'],
            Payload['Quart']
        )

    else:
        return tuple([dash.no_update] * 4)