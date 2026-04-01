'''
This is the app module that serves as the entry point. It registers all pages and initializes the layout of the dash application
and the depedencies between the pages. 
'''



# from dash import Dash, dcc, html, Input, Output, State, callback, dash_table, dash
# from dash.dependencies import Input, Output
# from dash import callback_context
# import dash_bootstrap_components as dbc
# import dash
# import json
# import threading
# from DashAppUtils import Load_KPI_Frames, Offload_KPI_Frames


# #Function for generating the Dash App.
# def Generate_Dash_App():
#     dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
#     app = Dash(__name__, use_pages=True, 
#                external_stylesheets=[dbc.themes.FLATLY, dbc_css],
#                suppress_callback_exceptions=True
#                )


#     navbar = dbc.NavbarSimple(
#         brand="Education Planning Dashboard",
#         brand_href="/",
#         color="primary",
#         dark=True,
#         className="navbar me-auto",
#         children=[
#             dbc.Button(dbc.NavLink(page["name"], href=page["path"]), className='mainnav-button btn')
#             for page in dash.page_registry.values()
#         ]
#     )

#     app.layout = dbc.Container(
#         [   
#             dcc.Location(id="url", refresh=False), 
#             dcc.Store(id="previous-path"),    
#             navbar,
#             dbc.Card(
#                 [
#                     dbc.CardBody(
#                         [
#                             html.Div(dash.page_container)
#                         ]
#                     )
#                 ],
#                 className="shadow-sm p-3 mb-5 bg-white rounded"
#             )
#         ],
#         fluid=True,
#         className="p-4",
#     )

#     @callback(
#     Output("previous-path", "data"),
#     Input("url", "pathname"),
#     State("previous-path", "data"),
#     prevent_initial_call=True
#     )
#     def handle_navigation(current_path, previous_path):
    
#         #ENTERING /programSearch
#         if current_path == "/programSearch" and previous_path != "/programSearch":
#             print("Entering programSearch → Loading KPI Frames")
#             threading.Thread(target=Load_KPI_Frames).start()

#         #LEAVING /programSearch
#         if previous_path == "/programSearch" and current_path != "/programSearch":
#             print("Leaving programSearch → Offloading KPI Frames")
#             threading.Thread(target=Offload_KPI_Frames).start()
        

#         return current_path
    

#     return app
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import dash
import threading

from DashAppUtils import Load_KPI_Frames, Offload_KPI_Frames


# ---------- STYLES ----------

PAGE_STYLE = {
    # "backgroundColor": "#081F36",
    "minHeight": "100vh"
}

PARENT_CARD_STYLE = {
    # "backgroundColor": "#071A2E",
    "border": "1px solid #0F355A",
    "borderRadius": "16px",
    "padding": "10px"
}


# ---------- DASH APP ----------
def Generate_Dash_App():

    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

    app = Dash(
        __name__,
        use_pages=True,
        external_stylesheets=[dbc.themes.FLATLY, dbc_css],
        suppress_callback_exceptions=True
    )

    # ---------- NAVBAR ----------
    navbar = dbc.NavbarSimple(
        brand="Education Planning Dashboard",
        brand_href="/",
        color="primary",
        dark=True,
        className="navbar me-auto",
        children=[
            dbc.Button(
                dbc.NavLink(page["name"], href=page["path"]),
                className='mainnav-button btn'
            )
            for page in dash.page_registry.values()
        ]
    )

    # ---------- LAYOUT ----------
    app.layout = dbc.Container(

        [

            dcc.Location(id="url", refresh=False),
            dcc.Store(id="previous-path"),

            navbar,

            dbc.Card(

                dbc.CardBody(

                    html.Div(
                        dash.page_container
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

    # ---------- PAGE NAVIGATION ----------
    @callback(
        Output("previous-path", "data"),
        Input("url", "pathname"),
        State("previous-path", "data"),
        prevent_initial_call=True
    )
    def handle_navigation(current_path, previous_path):

        # ENTERING /programSearch
        if current_path == "/programSearch" and previous_path != "/programSearch":
            print("Entering programSearch → Loading KPI Frames")
            threading.Thread(target=Load_KPI_Frames).start()

        # LEAVING /programSearch
        if previous_path == "/programSearch" and current_path != "/programSearch":
            print("Leaving programSearch → Offloading KPI Frames")
            threading.Thread(target=Offload_KPI_Frames).start()

        return current_path

    return app