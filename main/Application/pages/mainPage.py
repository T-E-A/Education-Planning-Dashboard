

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    path="/",
    name="Home"
)

# ---------- STYLES ----------

PAGE_STYLE = {
    "backgroundColor": "#081F36"
}

PARENT_CARD_STYLE = {
    "backgroundColor": "#071A2E",
    "border": "1px solid #0F355A",
    "borderRadius": "16px",
    "padding": "20px"
}

Pages_Dict = {
    1: {
        "Name": "Pathways",
        "href": "/careerPathways",
        "imgsrc": "/assets/icons/pathway.png",
        "desc": "Find your educational pathway here!"
    },
    2: {
        "Name": "Univeristy Comparisons",
        "href": "/programSearch",
        "imgsrc": "/assets/icons/comparison.png",
        "desc": "Compare different Universities based on your program of interest."
    },
    3: {
        "Name": "Trend Analysis",
        "href": "/trendAnalysis",
        "imgsrc": "/assets/icons/trend_analysis.png",
        "desc": "See which jobs may be hiring now based on trend analysis."
    },
    4: {
        "Name": "Future Estimates",
        "href": "/occupationForecasts",
        "imgsrc": "/assets/icons/forecast.png",
        "desc": "Find out what the future might look like for jobs you might want!"
    },
    5: {
        "Name": "Skill Matching",
        "href": "/compentencyMatching",
        "imgsrc": "/assets/icons/target.png",
        "desc": "Match your skills to potential career paths."
    },
    6: {
        "Name": "Educational Chat Assistant",
        "href": "/chatBot",
        "imgsrc": "/assets/icons/robot-assistant.png",
        "desc": "Chat with our Educational Chat Assistant"
    },
}


def build_page_links():

    links = []

    for page in Pages_Dict.values():

        links.append(

            dcc.Link(
                href=page["href"],
                className="circle-container",
                style={"textDecoration": "none", "color": "inherit"},

                children=[

                    html.Div(

                        [

                            html.Img(
                                src=page["imgsrc"],
                                style={
                                    "width": "100px",
                                    "height": "100px",
                                    "marginBottom": "10px"
                                }
                            ),

                            html.H4(
                                page["Name"],
                                className="main-header",
                                style={"fontSize": "22px"}
                            ),

                            html.P(
                                page["desc"],
                                style={
                                    "fontSize": "15px",
                                    "width": "85%",
                                    "textAlign": "center",
                                    "color": "#333"
                                }
                            )

                        ],

                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "padding": "20px",
                            "textAlign": "center"
                        }

                    )
                ]
            )
        )

    return links


layout = dbc.Container(

    [

        # Page Title
        dbc.Row(
            dbc.Col(
                html.H2(
                    "Welcome To the Education Planning Dashboard",
                    className="text-start mt-3 mb-2",
                    style={"fontSize": "35px", "color": "white"}
                ),
                width=12
            )
        ),

        # Description
        dbc.Row(
            dbc.Col(
                html.P(
                    "Use the tools below to explore career pathways, compare university programs, "
                    "analyze labour market trends, and discover future employment opportunities.",
                    style={
                        "fontSize": "18px",
                        "maxWidth": "900px",
                        "color": "#d0d6dc",
                        "lineHeight": "1.6"
                    }
                ),
                width=12
            )
        ),

        # ---------- DARK WRAPPER ----------
        dbc.Card(

            dbc.CardBody(

                dbc.Row(
                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                html.Div(
                                    build_page_links(),
                                    className="main_page_grid"
                                )

                            ),

                            style={
                                "borderRadius": "20px",
                                "boxShadow": "0 6px 15px rgba(0,0,0,0.15)",
                                "padding": "5px",
                                "backgroundColor": "#f8f9fb"
                            }

                        ),

                        width=12

                    )
                )

            ),

            style=PARENT_CARD_STYLE,
            className="shadow-lg mt-3"

        )

    ],

    fluid=True,
    className="p-4",
    style=PAGE_STYLE
)