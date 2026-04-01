from dash import dcc, html, callback ,Input, Output, State, ALL
import dash
import dash_bootstrap_components as dbc
import uuid
from dash import callback_context as ctx
from DashAppUtils import Send_Compentency_List, Ask_Pathways_Agent_A_Question
from dash_chat import ChatComponent


METRIC_NAMES = [
    "Numeracy",
    "Social Perceptiveness",
    "Negotiating",
    "Digital Literacy",
    "Persuading",
    "Evaluation",
    "Writing",
    "Instructing",
    "Active Listening",
    "Oral Expression",
    "Reading Comprehension"
]


dash.register_page(
    __name__,
    path="/compentencyMatching",
    name="Skill Matching"
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

CARD_STYLE = {
    "backgroundColor": "#B7CADF",
    "border": "1px solid #1E4A73",
    "borderRadius": "14px",
    "color": "white"
}

SLIDER_CONTAINER_STYLE = {
    "height": "550px",
    "overflowY": "auto",
    "paddingRight": "10px",
    "color":"#2A2B2C",
    "fontSize": "25px"
}

CHAT_CONTAINER_STYLE = {
    "height": "850px",
    "overflowY": "auto",
    # "backgroundColor": "#0F2F4F",
    "borderRadius": "12px",
    "padding": "12px"
}


# ---------- LAYOUT ----------

layout = dbc.Container(
    [

        dbc.Row(
            dbc.Col(
                html.H2(
                    "Skill Matching",
                    className="mt-3 mb-4 text-white"
                )
            )
        ),

        # ----------- DARK WRAPPER CARD -----------
        dbc.Card(
            dbc.CardBody(

                dbc.Row(
                    [

                        # ================= LEFT PANEL =================
                        dbc.Col(
                            dbc.Card(
                                [

                                    dbc.CardHeader(
                                        "Rate Your Skills (1–5)",
                                        className="fw-semibold"
                                    ),

                                    dbc.CardBody(

                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            html.Label(metric, className="fw-semibold"),

                                                            dcc.Slider(
                                                                id={"type": "metric-slider", "index": metric},
                                                                min=1,
                                                                max=5,
                                                                step=1,
                                                                value=3,
                                                                marks={i: str(i) for i in range(1, 6)},
                                                            ),
                                                        ],
                                                        className="mb-4",
                                                    ),

                                                    xs=12,
                                                    sm=6,
                                                    lg=4,

                                                )
                                                for metric in METRIC_NAMES
                                            ],
                                            className="g-3",
                                        ),

                                        style=SLIDER_CONTAINER_STYLE

                                    ),
                                ],
                                # style=CARD_STYLE,
                                className="shadow-lg h-100"
                            ),

                            lg=6,
                            md=12,

                        ),

                        # ================= RIGHT PANEL =================
                        dbc.Col(
                            dbc.Card(
                                [

                                    dbc.CardHeader(
                                        "Matched Career Insights",
                                        className="fw-semibold"
                                    ),

                                    dbc.CardBody(

                                        ChatComponent(
                                            id="mm-chat-component",
                                            messages=[],

                                            container_style=CHAT_CONTAINER_STYLE,

                                            input_text_style={
                                                "fontSize": "18px",
                                                "padding": "10px"
                                            },

                                            user_bubble_style={
                                                "fontSize": "18px",
                                                "padding": "14px",
                                                "backgroundColor": "#0B2B4A"
                                            },

                                            assistant_bubble_style={
                                                "fontSize": "18px",
                                                "padding": "14px"
                                            },
                                        )

                                    ),
                                ],

                                # style=CARD_STYLE,
                                className="shadow-lg h-100"
                            ),

                            lg=6,
                            md=12,
                        ),

                    ],
                    className="g-4"

                )

            ),

            style=PARENT_CARD_STYLE,
            className="shadow-lg mb-4"

        ),

        # ---------- BUTTON ----------
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "Find Matching Careers",
                    id="match-btn-send",
                    color="primary",
                    size="lg",
                    className="mt-3",
                    n_clicks=0
                ),
                width=4,
                className="mx-auto text-center"
            )
        ),

        # ---------- STORE ----------
        dcc.Store(id='mm-session-id', storage_type='session'),

    ],
    fluid=True,
    className="p-4",
    style=PAGE_STYLE
)


# ---------- SESSION ----------

@callback(
    Output('mm-session-id', 'data'),
    Input('mm-session-id', 'data'),
    prevent_initial_call=False
)
def initialize_session(existing_session):

    if existing_session is None:
        return str(uuid.uuid4())

    return existing_session


# ---------- CHAT + MATCH ----------

@callback(
    Output('mm-chat-component', 'messages'),
    Input('mm-chat-component', 'new_message'),
    Input('match-btn-send', 'n_clicks'),
    State('mm-session-id', 'data'),
    State('mm-chat-component', 'messages'),
    State({"type": "metric-slider", "index": ALL}, "value"),
    State({"type": "metric-slider", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def new_message(query, n_clicks, session_id, messages, values, ids):

    try:

        if messages is None:
            messages = []

        trigger = ctx.triggered_id

        # ---------- USER CHAT ----------
        if trigger == 'mm-chat-component':

            if not query:
                return messages

            updated_messages = messages + [query]

            if query.get("role") == "user":

                user_text = query.get("content", "")

                response = Ask_Pathways_Agent_A_Question(
                    user_query=user_text,
                    session_id=session_id
                )

                updated_messages.append({
                    "role": "assistant",
                    "content": response or "No relevant information found."
                })

            return updated_messages


        # ---------- MATCH BUTTON ----------
        elif trigger == 'match-btn-send':

            if n_clicks:

                try:

                    Metrics = {
                        slider_id["index"]: value
                        for slider_id, value in zip(ids, values)
                    }

                    response = Send_Compentency_List(
                        Metrics=Metrics,
                        session_id=session_id
                    )

                except:

                    response = "I am unable to get a list of matched careers."

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