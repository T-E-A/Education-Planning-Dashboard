from dash import dcc, html, callback ,Input, Output, State, ALL
import dash 
import dash_bootstrap_components as dbc
import json
from datetime import datetime
import os

from UILayer.DashAppUtilities import Send_Compentency_List

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
    name="Compentency Matching"
    )

# layout = dbc.Container(
#     [
#         # ---------- PAGE TITLE ----------
#         dbc.Row(
#             dbc.Col(
#                 html.H2(
#                     "Compentency-Occupation Match Making",
#                     className="text-start mt-3 mb-4",
#                     style={"font-size": "35px"}
#                 ),
#                 width=12
#             )
#         ),
#                 # ---------- USER INPUT ----------
#         dbc.Row(
#             dbc.Col(
#                 dbc.Card(
#                 [
#                     dbc.CardHeader("Skill Ratings (1–5)"),
#                     dbc.CardBody(
#                         [
#                             html.Div([
#                                 html.Label(metric),

#                                 dcc.Slider(
#                                     id={"type": "metric-slider", "index": metric},
#                                     min=1,
#                                     max=5,
#                                     step=1,
#                                     value=3,   # default value
#                                     marks={i: str(i) for i in range(1,6)}
#                                 )

#                             ], className="mb-4")

#                             for metric in METRIC_NAMES
#                         ]
#                     )
#                 ],
#                 className="shadow-sm"
#             ),
#             width=12
#         )
#         ),
#         dbc.Row(
#             [
#                 dbc.Col(
#                     dbc.Button(
#                         "Send",
#                         id="match-btn-send",
#                         color="primary",
#                         className="w-100 h-100",
#                         n_clicks=0
#                     ),
#                     width=2
#                 )
#             ],
#             className="mt-3"
#         ),

#           # ---------- CHAT WINDOW ----------
#         dbc.Row(
#             dbc.Col(
#                 dbc.Card(
#                     [
#                         dbc.CardHeader(
#                             "Matches",
#                             className="fw-semibold"
#                         ),
#                         dbc.CardBody(
#                             [
                                
#                                 dcc.Markdown(
#                                     id="match-chat-output",
#                                     children="",
#                                     style={
#                                         "height": "420px",
#                                         "overflowY": "auto",
#                                         "whiteSpace": "pre-wrap"
#                                     }
#                                 )
#                             ],
#                             style={"backgroundColor": "#fafafa"}
#                         )
#                     ],
#                     className="shadow-sm"
#                 ),
#                 width=12
#             )
#         ),





#     ],
#     fluid=True,
#     className="p-4"
# )

layout = dbc.Container(
    dbc.Row(
    [
        # ================= LEFT PANEL =================
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Skill Ratings (1–5)"),
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
                                    xs=12,   # mobile
                                    sm=6,    # tablet
                                    lg=4,    # desktop (3 per row)
                                )
                                for metric in METRIC_NAMES
                            ],
                            className="g-3",
                        ),
                        style={
                            "height": "500px",      # fixed height
                            "overflowY": "auto",    # internal scroll
                        },
                    ),
                ],
                className="shadow-sm h-100",
            ),
            lg=6,
            md=12,
        ),

        # ================= RIGHT PANEL =================
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Matches", className="fw-semibold"),
                    dbc.CardBody(
                        dcc.Markdown(
                            id="match-chat-output",
                            children="",
                            style={
                                "height": "500px",
                                "overflowY": "auto",
                                "whiteSpace": "pre-wrap",
                            },
                        ),
                        style={"backgroundColor": "#fafafa"},
                    ),
                ],
                className="shadow-sm h-100",
            ),
            lg=6,
            md=12,
        ),
    dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Send",
                        id="match-btn-send",
                        color="primary",
                        className="w-100 h-100",
                        n_clicks=0
                    ),
                    width=2
                )
            ],
            className="mt-3"
        ),
    ],
    className="mt-3 g-4",
)
)


@callback(
    Output("match-chat-output", "children"),   # change if needed
    Input("match-btn-send", "n_clicks"),
    State({"type": "metric-slider", "index": ALL}, "value"),
    State({"type": "metric-slider", "index": ALL}, "id"),
    prevent_initial_call=True
)
def collect_metrics(n_clicks, values, ids):

    # Build Metrics dictionary dynamically
    if n_clicks:
        Metrics = {
            slider_id["index"]: value
            for slider_id, value in zip(ids, values)
        }

        return Send_Compentency_List(Metrics=Metrics)