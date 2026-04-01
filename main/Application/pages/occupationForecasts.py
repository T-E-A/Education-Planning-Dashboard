from dash import dcc, html, callback ,Input, Output, dash_table, State
import dash
import dash_bootstrap_components as dbc
from dash_chat import ChatComponent
import uuid
from dash import callback_context as ctx

from DashAppUtils import (
    Get_NOC_Options,
    Get_Province_Options,
    Generate_Forecast_Analysis,
    Ask_AI_For_Forecast_Analysis,
    Ask_Pathways_Agent_A_Question
)

dash.register_page(
    __name__,
    path="/occupationForecasts",
    name="Future Estimates"
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

# ---------- LAYOUT ----------

layout = dbc.Container(
[
    dcc.Store(id='fo-session-id', storage_type='session'),

    dbc.Row(
        dbc.Col(
            html.H2(
                "Future Outcomes",
                className="text-start mt-3 mb-4",
                style={"font-size": "35px","color":"white"}
            ),
            width=12
        )
    ),

    dbc.Card(
        dbc.CardBody(
        [

        # ---------- FILTER CARD ----------
        dbc.Card(
            dbc.CardBody(
                [
                    html.Label("Select Province", className="fw-bold mb-2", style={"font-size": "20px"}),
                    dcc.Dropdown(
                        id='Select_Province',
                        options=Get_Province_Options(),
                        multi=False,
                        className="mb-4"
                    ),

                    html.Label("Select NOC Occupation Group", className="fw-bold mb-2", style={"font-size": "20px"}),
                    dcc.Dropdown(
                        id='Select_NOC',
                        options=Get_NOC_Options(),
                        multi=False,
                        className="mb-3"
                    ),
                ]
            ),
            className="shadow-sm mb-4"
        ),

        # ---------- ANALYSIS SECTION ----------
        html.Div(
        id="forecast-analysis-section",
        style=HIDDEN,
        children=[

        dbc.Row(
        [

            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        dcc.Graph(
                            id='Graph_NOC_Prov_Forecast',
                            style={"height": "100%"}
                        )
                    ),
                    className="shadow-sm h-100"
                ),
                width=6,
                style={"height": "1000px"}
            ),

            dbc.Col(
                html.Div(
                [

                    dbc.Card(
                        dbc.CardBody(
                            dash_table.DataTable(
                                id='Tbl_Forecast',
                                sort_action='native',
                                sort_mode='multi',
                                style_cell={'textAlign': 'left'},
                                style_table={
                                    'height': '100%',
                                    'overflowY': 'auto'
                                },
                                column_selectable="multi",
                                selected_rows=[],
                                filter_action='native',
                                fixed_rows={'headers': True},
                                fixed_columns={'headers': True},
                            ),
                            className='dbc dbc-row-selectable'
                        ),
                        className="shadow-sm",
                        style={"flex": "0.45", "marginBottom": "10px"}
                    ),

                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id='Graph_Secondary',
                                style={"height": "100%"}
                            )
                        ),
                        className="shadow-sm",
                        style={"flex": "0.55"}
                    ),

                ],
                style={
                    "height": "1000px",
                    "display": "flex",
                    "flexDirection": "column"
                }
                ),
                width=6
            ),

        ],
        className="mb-4"
        ),

        ]
        ),

        # ---------- BUTTON ----------
        html.Div(
            dbc.Row(
                dbc.Col(
                    dbc.Button(
                        "Ask AI to Explain",
                        id='FO_Ask_AI_Button',
                        color="primary"
                    ),
                    width="auto"
                ),
                className="mb-3"
            ),
            id="forecast-ai-button",
            style=HIDDEN
        ),

        # ---------- CHAT ----------
        html.Div(
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        ChatComponent(
                            id="fo-chat-component",
                            messages=[],
                            container_style={
                                "height": "1000px",
                                "overflowY": "auto",
                            },
                            input_text_style={"fontSize": "20px"},
                            user_bubble_style={
                                "fontSize": "20px",
                                "padding": "12px",
                                "backgroundColor": "#092744"
                            },
                            assistant_bubble_style={
                                "fontSize": "20px",
                                "padding": "12px",
                            },
                        )
                    ),
                    className="shadow-sm"
                ),
                width=12
            )
        ),
        id="forecast-chat-section",
        style=HIDDEN
        ),

        ]
        ),
        style=PARENT_CARD_STYLE,
        className="shadow-lg mb-4"
    ),

],
fluid=True,
className="p-4",
style=PAGE_STYLE
)

# ---------- SESSION ----------
@callback(
    Output('fo-session-id', 'data'),
    Input('fo-session-id', 'data'),
    prevent_initial_call=False
)
def initialize_session(existing_session):
    if existing_session is None:
        return str(uuid.uuid4())
    return existing_session

# ---------- SHOW ANALYSIS ----------
@callback(
    Output("forecast-analysis-section","style"),
    Output("forecast-ai-button","style"),
    Input('Select_Province','value'),
    Input('Select_NOC','value')
)
def reveal_analysis(province,noc):

    if province and noc:
        return VISIBLE, VISIBLE

    return HIDDEN, HIDDEN

# ---------- SHOW CHAT ----------
@callback(
    Output("forecast-chat-section","style"),
    Input('FO_Ask_AI_Button','n_clicks'),
    prevent_initial_call=True
)
def reveal_chat(n):

    if n:
        return VISIBLE

    return HIDDEN

# ---------- UPDATE FORECAST ----------
@callback(
        Output('Graph_NOC_Prov_Forecast', 'figure'),
        Output('Tbl_Forecast','columns'),
        Output('Tbl_Forecast','style_cell'),
        Output('Tbl_Forecast','data'),
        Output('Tbl_Forecast','style_data_conditional'),
        Output('Graph_Secondary','figure'),
        Input('Select_Province','value'),
        Input('Select_NOC','value'),
)
def Update_Graph_Forecasts(provinceid, noc_groupingid):

    if provinceid and noc_groupingid:

        Result = Generate_Forecast_Analysis(
            provinceid=provinceid,
            noc_groupingid=noc_groupingid
        )

        if len(Result['Tbl']) == 0:
            return Result['Viz'], tuple([dash.no_update] * 4), Result['Viz_2']

        data = Result['Tbl']['Data']
        cols = Result['Tbl']['Cols']
        style = Result['Tbl']['Style']
        styleCond = Result['Tbl']['StyleCond']

        return Result['Viz'], cols, style, data, styleCond, Result['Viz_2']

    return tuple([dash.no_update] * 6)

# ---------- CHAT ----------
@callback(
    Output('fo-chat-component', 'messages'),
    Input('fo-chat-component', 'new_message'),
    Input('FO_Ask_AI_Button', 'n_clicks'),
    State('fo-session-id', 'data'),
    State('fo-chat-component', 'messages'),
    State('Select_NOC','value'),
    State('Select_Province','value'),
    prevent_initial_call=True,
)
def new_message(query, n_clicks, session_id, messages, noc, province):

    try:

        if messages is None:
            messages = []

        trigger = ctx.triggered_id

        if trigger == 'fo-chat-component':

            if not query:
                return messages

            updated_messages = messages + [query]

            if query.get("role") == "user":

                response = Ask_Pathways_Agent_A_Question(
                    user_query=query.get("content",""),
                    session_id=session_id
                )

                # response = "Msg"

                updated_messages.append({
                    "role": "assistant",
                    "content": response or "No relevant information found."
                })

            return updated_messages

        elif trigger == 'FO_Ask_AI_Button':

            if not noc or not province:

                messages.append({
                    "role": "assistant",
                    "content": "⚠️ Please select both a Province and NOC Occupation to get a summary."
                })

                return messages

            if session_id:

                response = Ask_AI_For_Forecast_Analysis(
                    session_id=session_id,
                    noc_groupingid=noc
                )

            else:

                response = "Could not retrieve session ID."

            # response = "Button Click"

            messages.append({
                "role": "assistant",
                "content": response or "No relevant information found."
            })

            return messages

        return messages

    except Exception as e:

        if messages is None:
            messages = []

        messages.append({
            "role": "assistant",
            "content": f"⚠️ Unable to answer query due to system error [{e}]"
        })

        return messages