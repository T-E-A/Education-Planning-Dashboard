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