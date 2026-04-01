# from dash import dcc, html, callback ,Input, Output, State
# import dash 
# import dash_bootstrap_components as dbc
# import uuid
# from dash_chat import ChatComponent
# from dash import callback_context as ctx
# from DashAppUtils import (Get_Pathways_Route_Options ,
#                           Get_Major_FOS_Options,
#                             Get_Career_Options,
#                           Generate_Pathways,
#                           Generate_Pathway_Aggregate,
#                           Ask_AI_For_Income_Analysis,
#                           Ask_Pathways_Agent_A_Question
#                           )

# dash.register_page(
#     __name__,
#     path="/careerPathways",
#     name="Pathways"
#     )

# layout = dbc.Container(
#     [

#         dcc.Store(id='cp-session-id', storage_type='session'),
#         # ---------- PAGE TITLE ----------
#         dbc.Row(
#             dbc.Col(
#                 html.H2(
#                     "Pathways",
#                     className="text-start mt-3 mb-4",
#                     style={"font-size": "35px"}
#                 ),
#                 width=12
#             )
#         ),

#         # ---------- PROGRAM DROPDOWN ----------
#         dbc.Card(
#             dbc.CardBody(
#                 [
#                     html.Label(
#                         "Select Direction",
#                         className="fw-bold mb-2",
#                         style={"font-size": "20px"}
#                     ),
#                     dcc.Dropdown(
#                         id='Select_Route',
#                         options=Get_Pathways_Route_Options(),
#                         multi=False,
#                         className="mb-3"
#                     ),
#                     html.Label(
#                         "Select Interest",
#                         className="fw-bold mb-2",
#                         style={"font-size": "20px"}
#                     ),
#                     dcc.Dropdown(
#                         id='Select_Focus',
#                         multi=False,
#                         className="mb-3"
#                     ),
#                     dcc.RadioItems(
#                         id='Select_Chart_Type',
#                         options=[
#                         {"label": "📊 Icicle", "value": "icicle"},
#                         {"label": "🌳 Treemap", "value": "treemap"}
#                     ],
#                     value="treemap",  # default
#                     inline=True, 
#                     inputClassName="btn-check",
#                     labelClassName="btn btn-outline-primary me-3",
#                     className="btn-group mb-3"    # makes it horizontal
#                     ),
#                     dcc.Graph(id='Graph_Pathway'),
#                      html.Label(
#                         "Select Sub-Interest",
#                         className="fw-bold mb-2",
#                         style={"font-size": "20px"}
#                     ),
#                     dcc.Dropdown(
#                         id='Select_Sub_Interest',
#                         multi=False,
#                         className="mb-3"
#                     ),

#                     dcc.Graph(id='Graph_SubFocus_Distribution'),
#                     dbc.Button("Ask AI For Summary", id='Ask_AI_Button', color="primary", className="mt-3"),
#                            ChatComponent(
#                     id="cp-chat-component",
#                     messages=[], 
#                       container_style={
#                     "height": "900px",
#                     "overflowY": "auto",
#                     },
#                        # 🔤 Input box font
#                     input_text_style={
#                             "fontSize": "20px",
#                     },

#                     # 👤 User messages
#                     user_bubble_style={
#                         "fontSize": "20px",
#                         "padding": "12px",
#                         "backgroundColor":"#0B2B4A"
#                     },

#                     # 🤖 Assistant messages
#                     assistant_bubble_style={
#                     "fontSize": "20px",
#                     "padding": "12px",
#                     },
#                     )
#                     ]
#                 ),
#                 className="shadow-sm mb-4"
#             ),

#         html.Div(id='Debug_Output')

#     ],
#     fluid=True,
#     className="p-4"
# )


# @callback(
#     Output('cp-session-id', 'data'),
#     Input('cp-session-id', 'data'),
#     prevent_initial_call=False
# )
# def initialize_session(existing_session):
#     if existing_session is None:
#         return str(uuid.uuid4())
#     print(existing_session) 
#     return existing_session


# @callback(
#     Output('Select_Focus','options'),
#     Input('Select_Route','value')
    
# )
# def Path_Route_Changed(pathway_route):
#     if pathway_route:
        
#         if pathway_route == 1:
#             options = Get_Major_FOS_Options()
#         elif pathway_route == 2:
#             options = Get_Career_Options()

#         return options
        
#     else:
#         return dash.no_update 

# @callback(
#     Output('Graph_Pathway','figure'),
#     Output('Select_Sub_Interest','options'),
#     State('Select_Route','value'),
#     Input('Select_Focus','value'),
#     Input('Select_Chart_Type','value')
# )
# def Pathway_Focus_Changed(pathway_route, pathway_focus, chart_type):
#     if pathway_route and pathway_focus and chart_type:
#         try:
            
#             if chart_type == 'treemap':
#                 tree = True
#             else:
#                 tree = False


#             response = Generate_Pathways(Route=pathway_route, Focus=pathway_focus, tree=tree)

#             if response:
#                 return response['Viz'], response['SelectList']
#             else:
#                 return {'data': [], 'layout': {'title': f'No data available for selected pathway'}}, ['No options']

#         except Exception as e:
#             print(f"Pathway_Focus_Changed() => {e}")
#             return {'data': [], 'layout': {'title': f'Unable to generate Pathways graph for {pathway_focus} due to system error => {e}'}}, ['No options']
#     else:
#         return dash.no_update


# @callback(
#     Output('Graph_SubFocus_Distribution','figure'),
#     State('Select_Route','value'),
#     State('Select_Focus','value'),
#     Input('Select_Sub_Interest','value')
# )
# def SubFocus_Changed(pathway_route, pathway_focus, sub_focus):
#     if pathway_route and pathway_focus and sub_focus:
#         try:

#             response = Generate_Pathway_Aggregate(Route=pathway_route, Focus=pathway_focus, SubFocus=sub_focus)

#             return response

#         except Exception as e:
#             print(f"SubFocus_Changed() => {e}")
#             return {'data': [], 'layout': {'title': f'Unable to generate Sub-Focus Distribution graph for {sub_focus} due to system error => {e}'}}
#     else:
#         return dash.no_update


# @callback(
#     Output('cp-chat-component', 'messages'),
#     Input('cp-chat-component', 'new_message'),
#     Input('Ask_AI_Button', 'n_clicks'),
#     State('cp-session-id', 'data'),
#     State('cp-chat-component', 'messages'),
#     State('Select_Focus','value'),
#     State('Select_Sub_Interest', 'value'),
#     prevent_initial_call=True,
# )
# def new_message(query, n_clicks, session_id, messages, focus, sub_interest):
#     try:
#         if messages is None:
#             messages = []

#         # 🔍 Identify what triggered the callback
#         trigger = ctx.triggered_id

#         # -----------------------------
#         # 🟢 CASE 1: User typed a message
#         # -----------------------------
#         if trigger == 'cp-chat-component':
#             if not query:
#                 return messages

#             updated_messages = messages + [query]

#             if query.get("role") == "user":
#                 user_text = query.get("content", "")

#                 params = {
#                     'query': user_text,
#                     'focus': focus,
#                     'sub_interest': sub_interest
#                 }

#                 response = Ask_Pathways_Agent_A_Question(user_query=user_text, session_id=session_id)

#                 updated_messages.append({
#                     "role": "assistant",
#                     "content": response or "No relevant information found."
#                 })

#             return updated_messages

#         # -----------------------------
#         # 🔵 CASE 2: Button clicked
#         # -----------------------------
#         elif trigger == 'Ask_AI_Button':

#             print(f"Button clicked! Focus: {focus}, Sub-Interest: {sub_interest}, Session ID: {session_id}")
#             # if not messages:
#             #     return messages
            
#             if not focus or not sub_interest:
#                 messages.append({
#                     "role": "assistant",
#                     "content": "⚠️ Please select both a a Interest and Sub-Interest to get a summary."
#                 })
#                 return messages

#             # Get last user message
#             # last_user_msg = next(
#             #     (m for m in reversed(messages) if m.get("role") == "user"),
#             #     None
#             # )

#             # if not last_user_msg:
#             #     return messages

#             # user_text = last_user_msg.get("content", "")

#             # params = {
#             #     'query': user_text,
#             #     'focus': focus,
#             #     'sub_interest': sub_interest
#             # }

#             if session_id:
#                 response = Ask_AI_For_Income_Analysis(session_id=session_id)
#             else:
#                 response = "Could not retrieve session ID. Please refresh the page and try again."

#             # response = helper.ask_query(params=params)

#             messages.append({
#                 "role": "assistant",
#                 "content": response or "No relevant information found."
#             })

#             return messages

#         return messages

#     except Exception as e:
#         # logger.exception(e)

#         if messages is None:
#             messages = []

#         messages.append({
#             "role": "assistant",
#             "content": f"⚠️ Unable to answer query due to system error [{e}]"
#         })

#         return messages
from dash import dcc, html, callback, Input, Output, State
import dash
import dash_bootstrap_components as dbc
import uuid
from dash_chat import ChatComponent
from dash import callback_context as ctx

from DashAppUtils import (
    Get_Pathways_Route_Options,
    Get_Major_FOS_Options,
    Get_Career_Options,
    Generate_Pathways,
    Generate_Pathway_Aggregate,
    Ask_AI_For_Income_Analysis,
    Ask_Pathways_Agent_A_Question
)

dash.register_page(
    __name__,
    path="/careerPathways",
    name="Pathways"
)

# ---------- STYLING ----------
CARD_STYLE = {
    "backgroundColor": "#102F4F",
    "border": "1px solid #1E4A73",
    "borderRadius": "14px",
    "color": "white"
}

GRAPH_CONTAINER_STYLE = {
    "backgroundColor": "#0B2B4A",
    "borderRadius": "12px",
    "padding": "10px"
}

# ---------- LAYOUT ----------
layout = dbc.Container(
    [

        dcc.Store(id='cp-session-id', storage_type='session'),

        # ---------- PAGE TITLE ----------
        dbc.Row(
            dbc.Col(
                html.H2(
                    "Career Pathways",
                    className="text-start mt-3 mb-4 text-white",
                    style={"font-size": "35px"}
                ),
                width=12
            )
        ),

        # ---------- STEP 1 ----------
        dbc.Card(
            [
                dbc.CardHeader("Step 1 — Choose Direction"),
                dbc.CardBody(
                    dbc.Row(
                        dbc.Col(
                            [

                                html.Label("Select Direction", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id='Select_Route',
                                    options=Get_Pathways_Route_Options(),
                                    multi=False,
                                    className="mb-3",
                                     style={
                                        "color": "black"
                                    }
                                ),

                                html.Label("Select Interest", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id='Select_Focus',
                                    multi=False,
                                    className="mb-3",
                                    style={
                                        "color": "black"
                                    }
                                ),

                                dcc.RadioItems(
                                    id='Select_Chart_Type',
                                    options=[
                                        {"label": "📊 Icicle", "value": "icicle"},
                                        {"label": "🌳 Treemap", "value": "treemap"}
                                    ],
                                    value="treemap",
                                    inline=True,
                                    inputClassName="btn-check",
                                    labelClassName="btn btn-outline-light me-3",
                                    className="btn-group"
                                ),
                            ],
                            width=6
                        ),
                        justify="center"
                    )
                )
            ],
            style=CARD_STYLE,
            className="shadow-lg mb-4"
        ),

        # ---------- STEP 2 GRAPH ----------
        html.Div(
            dbc.Card(
                [
                    dbc.CardHeader("Step 2 — Pathway Visualization"),
                    dbc.CardBody(
                        dcc.Loading(
                            html.Div(
                                dcc.Graph(id='Graph_Pathway'),
                                style=GRAPH_CONTAINER_STYLE
                            ),
                            type="circle"
                        )
                    )
                ],
                style=CARD_STYLE,
                className="shadow-lg mb-4"
            ),
            id="pathway-card",
            style={"display": "none"}
        ),

        # ---------- STEP 3 SUB INTEREST ----------
        html.Div(
            dbc.Card(
                [
                    dbc.CardHeader("Step 3 — Select Sub-Interest"),
                    dbc.CardBody(
                        dbc.Row(
                            dbc.Col(
                                [
                                    dcc.Dropdown(
                                        id='Select_Sub_Interest',
                                        multi=False,
                                        className="mb-3",
                                        style={
                                        "color": "black"
                                        }
                                    )
                                ],
                                width=6
                            ),
                            justify="center"
                        )
                    )
                ],
                style=CARD_STYLE,
                className="shadow-lg mb-4"
            ),
            id="sub-interest-card",
            style={"display": "none"}
        ),

        # ---------- STEP 4 DISTRIBUTION GRAPH ----------
        html.Div(
            dbc.Card(
                [
                    dbc.CardHeader("Step 4 — Distribution Insights"),
                    dbc.CardBody(
                        dcc.Loading(
                            html.Div(
                                dcc.Graph(id='Graph_SubFocus_Distribution'),
                                style=GRAPH_CONTAINER_STYLE
                            ),
                            type="circle"
                        )
                    )
                ],
                style=CARD_STYLE,
                className="shadow-lg mb-4"
            ),
            id="distribution-card",
            style={"display": "none"}
        ),

        # ---------- STEP 5 AI INSIGHTS ----------
        html.Div(
            dbc.Card(
                [
                    dbc.CardHeader("AI Pathway Income Insights"),
                    dbc.CardBody(
                        [

                            dbc.Button(
                                "Ask AI For Summary",
                                id='Ask_AI_Button',
                                color="primary",
                                className="mb-3"
                            ),

                            ChatComponent(
                                id="cp-chat-component",
                                messages=[],
                                container_style={
                                    "height": "900px",
                                    "overflowY": "auto",
                                    # "backgroundColor": "#FFFFFF",
                                    "borderRadius": "12px",
                                    "padding": "10px",
                                },

                                input_text_style={"fontSize": "18px"},

                                user_bubble_style={
                                    "fontSize": "18px",
                                    "padding": "12px",
                                    "backgroundColor": "#0B2B4A"
                                },

                                assistant_bubble_style={
                                    "fontSize": "18px",
                                    "padding": "12px",

                                },
                            )
                        ]
                    )
                ],
                style=CARD_STYLE,
                className="shadow-lg mb-4"
            ),
            id="chat-card",
            style={"display": "none", "height": "600px"}
        ),

        html.Div(id='Debug_Output')

    ],
    fluid=True,
    className="p-4",
    style={"backgroundColor": "#081F36"}
)

# ---------- SESSION ----------
@callback(
    Output('cp-session-id', 'data'),
    Input('cp-session-id', 'data'),
    prevent_initial_call=False
)
def initialize_session(existing_session):
    if existing_session is None:
        return str(uuid.uuid4())
    return existing_session


# ---------- ROUTE CHANGE ----------
@callback(
    Output('Select_Focus', 'options'),
    Input('Select_Route', 'value')
)
def Path_Route_Changed(pathway_route):

    if pathway_route:

        if pathway_route == 1:
            return Get_Major_FOS_Options()

        elif pathway_route == 2:
            return Get_Career_Options()

    return dash.no_update


# ---------- PATHWAY GRAPH ----------
@callback(
    Output('Graph_Pathway', 'figure'),
    Output('Select_Sub_Interest', 'options'),
    Output("pathway-card", "style"),
    Output("sub-interest-card", "style"),
    State('Select_Route', 'value'),
    Input('Select_Focus', 'value'),
    Input('Select_Chart_Type', 'value')
)
def Pathway_Focus_Changed(pathway_route, pathway_focus, chart_type):

    if pathway_route and pathway_focus and chart_type:

        try:

            tree = chart_type == "treemap"

            response = Generate_Pathways(
                Route=pathway_route,
                Focus=pathway_focus,
                tree=tree
            )

            if response:
                return (
                    response['Viz'],
                    response['SelectList'],
                    {"display": "block"},
                    {"display": "block"}
                )

        except Exception as e:
            print(f"Pathway_Focus_Changed() => {e}")

    return dash.no_update


# ---------- SUBFOCUS GRAPH ----------
@callback(
    Output('Graph_SubFocus_Distribution', 'figure'),
    Output("distribution-card", "style"),
    Output("chat-card", "style"),
    State('Select_Route', 'value'),
    State('Select_Focus', 'value'),
    Input('Select_Sub_Interest', 'value')
)
def SubFocus_Changed(pathway_route, pathway_focus, sub_focus):

    if pathway_route and pathway_focus and sub_focus:

        try:

            response = Generate_Pathway_Aggregate(
                Route=pathway_route,
                Focus=pathway_focus,
                SubFocus=sub_focus
            )

            return response, {"display": "block"}, {"display": "block"}

        except Exception as e:

            print(f"SubFocus_Changed() => {e}")

    return dash.no_update


# ---------- CHAT ----------
@callback(
    Output('cp-chat-component', 'messages'),
    Input('cp-chat-component', 'new_message'),
    Input('Ask_AI_Button', 'n_clicks'),
    State('cp-session-id', 'data'),
    State('cp-chat-component', 'messages'),
    State('Select_Focus', 'value'),
    State('Select_Sub_Interest', 'value'),
    prevent_initial_call=True
)
def new_message(query, n_clicks, session_id, messages, focus, sub_interest):

    try:

        if messages is None:
            messages = []

        trigger = ctx.triggered_id

        # ---------- USER MESSAGE ----------
        if trigger == 'cp-chat-component':

            if not query:
                return messages

            updated_messages = messages + [query]

            if query.get("role") == "user":

                user_text = query.get("content", "")

                response = Ask_Pathways_Agent_A_Question(
                    user_query=user_text,
                    session_id=session_id
                )

                # response = "Hello"

                updated_messages.append({
                    "role": "assistant",
                    "content": response or "No relevant information found."
                })

            return updated_messages

        # ---------- AI SUMMARY ----------
        elif trigger == 'Ask_AI_Button':

            if not focus or not sub_interest:

                messages.append({
                    "role": "assistant",
                    "content": "⚠️ Please select both an Interest and Sub-Interest."
                })

                return messages

            if session_id:
                response = Ask_AI_For_Income_Analysis(session_id=session_id)
            else:
                response = "Could not retrieve session ID."

            messages.append({
                "role": "assistant",
                "content": response or "No relevant information found."
            })

            return messages

        return messages

    except Exception as e:

        messages.append({
            "role": "assistant",
            "content": f"⚠️ System error [{e}]"
        })

        return messages