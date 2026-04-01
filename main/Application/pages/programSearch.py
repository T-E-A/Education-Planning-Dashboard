# from dash import dcc, html, callback ,Input, Output, State,dash_table, ALL
# import dash
# import dash_bootstrap_components as dbc
# # from DashAppUtilities import Generate_KPI_Comparison
# from DashAppUtils import (Get_Program_Options,
#                           Get_Post_Grad_Employment_Rate_Measure_Options,
#                           Generate_KPI_Comparison,
#                           Generate_YoY_Comparison,
#                           Get_Student_Type_Options,
#                           fee_fields,
#                           Ask_For_Universities_That_Match_Budget,
#                           Ask_For_AI_Budget_Analysis
#                           )
# def generate_fee_inputs(fields):
#     return [
#         dbc.Col(
#             dbc.Card(
#                 dbc.CardBody(
#                     [
#                         html.Label(field, className="fw-semibold mb-2"),

#                         dbc.InputGroup(
#                             [
#                                 dbc.InputGroupText("$"),
#                                 dbc.Input(
#                                      id={
#                                         "type": "fee-input",
#                                         "index": field
#                                     },
#                                     type="number",
#                                     placeholder="0.00",
#                                     min=0,
#                                     step=0.01,
#                                     className="text-end"
#                                 ),
#                             ],
#                             size="md"
#                         )
#                     ]
#                 ),
#                 className="h-100 border-0 shadow-sm"
#             ),
#             xs=12, sm=12, md=6, lg=6,  # responsive 2-column layout
#             className="mb-3"
#         )
#         for field in fields
#     ]



# dash.register_page(
#     __name__,
#     path="/programSearch",
#     name="Uni Comparison"
#     )


# layout = dbc.Container(
#     [




#         # ---------- PAGE TITLE ----------
#         dbc.Row(
#             dbc.Col(
#                 html.H2(
#                     "University Program KPI Stats",
#                     className="text-start mt-3 mb-4",
#                     style={"font-size": "35px"}
#                 ),
#                 width=12
#             )
#         ),

#         # ---------- PROGRAM + KPI SELECTORS ----------
#         dbc.Card(
#             dbc.CardBody(
#                 [
#                     html.Label(
#                         "Select Program",
#                         className="fw-bold mb-2",
#                         style={"font-size": "20px"}
#                     ),
#                     dcc.Dropdown(
#                         id='Select_Program',
#                         options=Get_Program_Options(),
#                         multi=False,
#                         className="mb-4"
#                     ),

#                     html.Label(
#                         "Select KPI",
#                         className="fw-bold mb-2",
#                         style={"font-size": "20px"}
#                     ),
#                     dcc.Dropdown(
#                         id='Select_KPI',
#                         options=Get_Post_Grad_Employment_Rate_Measure_Options(),
#                         multi=False,
#                         className="mb-3"
#                     )
#                 ]
#             ),
#             className="shadow-sm mb-4"
#         ),

#         # ---------- TWO KPI GRAPHS ----------
#         dbc.Row(
#             [
#                 dbc.Col(
#                     dbc.Card(
#                         dbc.CardBody(
#                             dcc.Graph(id='Graph_KPIMap')
#                         ),
#                         className="shadow-sm h-100"
#                     ),
#                     width=6
#                 ),

#                 dbc.Col(
#                     dbc.Card(
#                         dbc.CardBody(
#                             dcc.Graph(id='Graph_KPIBar')
#                         ),
#                         className="shadow-sm h-100"
#                     ),
#                     width=6
#                 ),

#                 dbc.Col(
#                     dbc.Card(
#                         dbc.CardBody(
#                              html.Div(

#                              dcc.Graph(id='Graph_KPIYOY')
#                              , className='dbc dbc-row-selectable'),
#                         ),
#                         className="shadow-sm h-100"
#                     ),
#                     width=12
#                 ),


#             ],
#             className="mb-5"
#         ),

#         dbc.Row(
#             dbc.Col(
#                 html.H2(
#                     "Budget Matching",
#                     className="text-start mt-3 mb-4",
#                     style={"font-size": "35px"}
#                 ),
#                 width=12
#             )
#         ),

#         dbc.Card(
#             dbc.CardBody(
#                 [
#                     html.Label(
#                         "Domestic/International",
#                         className="fw-bold mb-2",
#                         style={"font-size": "20px"}
#                     ),
#                     dcc.Dropdown(
#                         id='Select_StudentType',
#                         options=Get_Student_Type_Options(),
#                         multi=False,
#                         className="mb-4"
#                     ),
#                     dbc.Row([
#                         *generate_fee_inputs(fee_fields),
#                          dbc.Button(
#                             "Find Universities that Match Budget Criteria",
#                             id="btn-getMatches",
#                             color="primary",
#                             className="w-100 h-100",
#                         ),
#                          html.Div(


#                              dash_table.DataTable(
#                                  id='Tbl_UniBudgets',
#                                 sort_action='native',
#                                 sort_mode='multi',
#                                 style_cell={'textAlign': 'left'},
#                                 style_table={'height': '500px', 'overflowY': 'auto'},
#                                 column_selectable="multi",
#                                 selected_rows=[],
#                                 filter_action='native',
#                                 fixed_rows={'headers': True},
#                                 fixed_columns={'headers': True}

#                             ), className='dbc dbc-row-selectable')

#                         ]

#                     ),
#                     dbc.Button(
#                             "Get Budget Analysis",
#                             id="btn-getbudgetAnalysis",
#                             color="primary",
#                             className="w-100 h-100",
#                         ),
#                 ]
#             ),
#             className="shadow-sm mb-4"
#         ),

#         dbc.Row(
#             dbc.Col(
#                 dbc.Card(
#                     [

#                         dbc.CardBody(
#                             [

#                                 dcc.Markdown(
#                                     id="chat-budget-analysis",
#                                     children="Click Get Budget Analysis for quick summary!",
#                                     style={
#                                         "height": "420px",
#                                         "overflowY": "auto",
#                                         "whiteSpace": "pre-wrap"
#                                     }
#                                 )
#                             ],
#                             style={"backgroundColor": "#fafafa"}
#                         ),
#                     ],
#                     className="shadow-sm"
#                 ),
#                 width=12
#             )
#         ),

#         html.Div(id='test')
#     ],
#     fluid=True,
#     className="p-4"


# )




# @callback(
#         Output('Graph_KPIMap', 'figure'),
#         Output('Graph_KPIBar', 'figure'),
#         Input('Select_Program','value'),
#         Input('Select_KPI','value'),
#     )
# def Update_KPI_Map(Program, KPI):
#     if Program and KPI:
#         print(f"Map/Bar Call Back Called")
#         Payload = Generate_KPI_Comparison(ProgramID=Program, KPI=KPI)

#         Map = Payload['Map']
#         Bar = Payload['Bar']

#         return Map, Bar

#     else:
#         return tuple([dash.no_update] * 2)

# @callback(
#     Output('Graph_KPIYOY','figure'),
#     State('Select_KPI','value'),
#     State('Select_Program','value'),
#     Input('Graph_KPIMap','selectedData')
# )
# def Get_YOY_Comparison(kpi, programid ,selectedData):
#     try:
#         if not selectedData:
#             return dash.no_update

#         if kpi and programid:

#             univeristy_ids = [
#                 point['customdata'][0]
#                 for point in selectedData['points']
#             ]

#             string_test = [
#                 str(point['customdata'][0])
#                 for point in selectedData['points']
#             ]

#         print(univeristy_ids)
#         print(f"ProgramID: {programid}")
#         print(f"KPI ID => {kpi}")



#         result = Generate_YoY_Comparison(ProgramID=int(programid), KPI= int(kpi), UniversityIDs=univeristy_ids)

#         if result:
#             return result


#         return string_test
#     except Exception as e:
#         return dash.no_update


# @callback(
#     Output('Tbl_UniBudgets','columns'),
#     Output('Tbl_UniBudgets','style_cell'),
#     Output('Tbl_UniBudgets','data'),
#     Output('Tbl_UniBudgets','style_data_conditional'),
#     Input('btn-getMatches','n_clicks'),
#     State('Select_StudentType','value'),
#     State({"type": "fee-input", "index": ALL}, "value"),
#     State({"type": "fee-input", "index": ALL}, "id"),
#     prevent_initial_call=True

# )
# def Get_Optimized_Choices(clicked, studentType, values, ids):
#     try:
#         if not clicked:
#             tuple([dash.no_update] * 4)

#         if not studentType:
#             tuple([dash.no_update] * 4)

#         print("Student Type:", studentType)
#         print("IDs:", ids)
#         print("Values:", values)

#         data = {
#             id_["index"]: (float(value) if value is not None else 0)
#             for id_, value in zip(ids, values)
#         }

#         print("Processed Data:", data)

#         frame = [
#             {'Expense Type': k, 'Input': v} for k, v in data.items()
#         ]

#         Vector = [float(data[f]) for f in fee_fields]

#         print(f"Vector => {Vector}")

#         params = {
#             'StudentType': studentType,
#             'Vector':Vector
#         }

#         Tbl =Ask_For_Universities_That_Match_Budget(params=params, frame=frame)

#         if len(Tbl) > 0:
#             data = Tbl['Data']
#             cols = Tbl['Cols']
#             style = Tbl['Style']
#             styleCond =Tbl['StyleCond']

#         return cols, style, data,styleCond


#     except Exception as e:
#         return tuple([dash.no_update] * 4)


# @callback(
#     Output("chat-budget-analysis", "children"),
#     Input("btn-getbudgetAnalysis", "n_clicks"),
#     prevent_initial_call=True
# )
# def update_chat(n_clicks):
#     try:

#         if n_clicks:

#             response = Ask_For_AI_Budget_Analysis()


#             return response

#     except Exception as e:
#         return f"I cannot provide a budget analysis at this time. Sorry => {e}"

from dash import dcc, html, callback ,Input, Output, State, dash_table, ALL
import dash
import dash_bootstrap_components as dbc

from DashAppUtils import (
    Get_Program_Options,
    Get_Post_Grad_Employment_Rate_Measure_Options,
    Generate_KPI_Comparison,
    Generate_YoY_Comparison,
    Get_Student_Type_Options,
    fee_fields,
    Ask_For_Universities_That_Match_Budget,
    Ask_For_AI_Budget_Analysis
)

# ---------- STYLES ----------
PAGE_STYLE = {
    # "backgroundColor": "#081F36"
    }

PARENT_CARD_STYLE = {
    "backgroundColor": "#071A2E",
    "border": "1px solid #0F355A",
    "borderRadius": "16px",
    "padding": "20px"
}

HIDDEN = {"display": "none"}
VISIBLE = {"display": "block"}

# ---------- HELPERS ----------
def generate_fee_inputs(fields):
    return [
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Label(field, className="fw-semibold mb-2"),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("$"),
                                dbc.Input(
                                    id={"type": "fee-input", "index": field},
                                    type="number",
                                    placeholder="0.00",
                                    min=0,
                                    step=0.01,
                                    className="text-end"
                                ),
                            ]
                        )
                    ]
                ),
                className="h-100 border-0 shadow-sm"
            ),
            xs=12, sm=12, md=6, lg=6,
            className="mb-3"
        )
        for field in fields
    ]

dash.register_page(__name__, path="/programSearch", name="Uni Comparison")

# ---------- LAYOUT ----------
layout = dbc.Container([

    dbc.Row(
        dbc.Col(
            html.H2("University Program KPI Stats",
                className="mt-3 mb-4",
                style={"fontSize": "35px", "color":"white"}
            )
        )
    ),

    dbc.Card(
        dbc.CardBody([

        # ---------- FILTER ----------
        dbc.Card(
            dbc.CardBody([
                html.Label("Select Program", className="fw-bold"),
                dcc.Dropdown(id='Select_Program', options=Get_Program_Options(), className="mb-4"),

                html.Label("Select KPI", className="fw-bold"),
                dcc.Dropdown(id='Select_KPI', options=Get_Post_Grad_Employment_Rate_Measure_Options())
            ]),
            className="shadow-sm mb-4"
        ),

        # ---------- KPI SECTION ----------
        html.Div(id="kpi-section", style=HIDDEN, children=[

            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='Graph_KPIMap')), className="shadow-sm"), width=6),
                dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='Graph_KPIBar')), className="shadow-sm"), width=6),
            ]),

            html.Div(id="yoy-section", style=HIDDEN, children=[
                dbc.Card(
                    dbc.CardBody(dcc.Graph(id='Graph_KPIYOY')),
                    className="shadow-sm mt-3"
                )
            ])
        ]),

        # ---------- BUDGET ----------
        dbc.Row(
            dbc.Col(
                html.H2("Budget Matching",
                    className="mt-4 mb-4",
                    style={"color":"white"}
                )
            )
        ),

        dbc.Card(
            dbc.CardBody([
                html.Label("Domestic/International", className="fw-bold"),
                dcc.Dropdown(id='Select_StudentType', options=Get_Student_Type_Options(), className="mb-4"),

                dbc.Row(generate_fee_inputs(fee_fields)),

                dbc.Button("Find Universities that Match Budget Criteria",
                    id="btn-getMatches",
                    color="primary",
                    className="w-100 mb-3"
                ),

                html.Div(
                    dash_table.DataTable(
                        id='Tbl_UniBudgets',
                        sort_action='native',
                        style_table={'height': '500px', 'overflowY': 'auto'},
                    ),
                    id="budget-table-section",
                    style=HIDDEN
                ),

                dbc.Button("Get Budget Analysis",
                    id="btn-getbudgetAnalysis",
                    color="primary",
                    className="w-100 mt-3"
                ),

                html.Div(
                    dcc.Markdown(
                        id="chat-budget-analysis",
                        children="",
                        style={"height": "420px","overflowY": "auto"}
                    ),
                    id="budget-analysis-section",
                    style=HIDDEN
                )
            ]),
            className="shadow-sm mb-4"
        ),

        ]),
        style=PARENT_CARD_STYLE,
        className="shadow-lg"
    )

], fluid=True, className="p-4", style=PAGE_STYLE)

# ---------- SHOW KPI ----------
@callback(
    Output("kpi-section","style"),
    Input('Select_Program','value'),
    Input('Select_KPI','value')
)
def show_kpi(p,k):
    return VISIBLE if p and k else HIDDEN

# ---------- SHOW YOY ----------
@callback(
    Output("yoy-section","style"),
    Input('Graph_KPIMap','selectedData')
)
def show_yoy(data):
    return VISIBLE if data else HIDDEN

# ---------- SHOW TABLE ----------
@callback(
    Output("budget-table-section","style"),
    Input("btn-getMatches","n_clicks"),
    prevent_initial_call=True
)
def show_table(n):
    return VISIBLE if n else HIDDEN

# ---------- SHOW ANALYSIS ----------
@callback(
    Output("budget-analysis-section","style"),
    Input("btn-getbudgetAnalysis","n_clicks"),
    prevent_initial_call=True
)
def show_analysis(n):
    return VISIBLE if n else HIDDEN


# ---------- YOUR ORIGINAL CALLBACKS (UNCHANGED) ----------
@callback(
    Output('Graph_KPIMap', 'figure'),
    Output('Graph_KPIBar', 'figure'),
    Input('Select_Program','value'),
    Input('Select_KPI','value'),
)
def Update_KPI_Map(Program, KPI):
    if Program and KPI:
        Payload = Generate_KPI_Comparison(ProgramID=Program, KPI=KPI)
        return Payload['Map'], Payload['Bar']
    return tuple([dash.no_update] * 2)


@callback(
    Output('Graph_KPIYOY','figure'),
    State('Select_KPI','value'),
    State('Select_Program','value'),
    Input('Graph_KPIMap','selectedData')
)
def Get_YOY_Comparison(kpi, programid ,selectedData):
    try:
        if not selectedData:
            return dash.no_update

        univeristy_ids = [p['customdata'][0] for p in selectedData['points']]
        result = Generate_YoY_Comparison(
            ProgramID=int(programid),
            KPI=int(kpi),
            UniversityIDs=univeristy_ids
        )
        return result if result else dash.no_update
    except:
        return dash.no_update


@callback(
    Output('Tbl_UniBudgets','columns'),
    Output('Tbl_UniBudgets','style_cell'),
    Output('Tbl_UniBudgets','data'),
    Output('Tbl_UniBudgets','style_data_conditional'),
    Input('btn-getMatches','n_clicks'),
    State('Select_StudentType','value'),
    State({"type": "fee-input", "index": ALL}, "value"),
    State({"type": "fee-input", "index": ALL}, "id"),
    prevent_initial_call=True
)
def Get_Optimized_Choices(clicked, studentType, values, ids):
    try:
        data = {id_["index"]: (float(v) if v else 0) for id_, v in zip(ids, values)}
        Vector = [float(data[f]) for f in fee_fields]

        Tbl = Ask_For_Universities_That_Match_Budget(
            params={'StudentType': studentType, 'Vector': Vector},
            frame=[{'Expense Type': k, 'Input': v} for k, v in data.items()]
        )

        if len(Tbl) > 0:
            return Tbl['Cols'], Tbl['Style'], Tbl['Data'], Tbl['StyleCond']

    except:
        return tuple([dash.no_update] * 4)


@callback(
    Output("chat-budget-analysis", "children"),
    Input("btn-getbudgetAnalysis", "n_clicks"),
    prevent_initial_call=True
)
def update_chat(n_clicks):
    try:
        if n_clicks:
            return Ask_For_AI_Budget_Analysis()
    except Exception as e:
        return f"Error: {e}"