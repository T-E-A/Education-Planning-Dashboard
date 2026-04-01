from dash import dcc, html, callback ,Input, Output, State
import dash 
import dash_bootstrap_components as dbc
import json
from datetime import datetime
import os
import uuid
from dash_chat import ChatComponent

from DashAppUtils import Ask_Chat_Agent

dash.register_page(
    __name__,
    path="/chatBot",
    name="Educational Chat Assistant"
    )

# Global dictionary to store chat history
chat_history = {
    "Message": []
}


layout = dbc.Container(
    [
        # ---------- PAGE TITLE ----------
        dcc.Store(id='cb-session-id', storage_type='session'),
        dbc.Row(
            dbc.Col(
                html.H2(
                    "Educational Chat Assistant",
                    className="text-start mt-3 mb-4",
                    style={"font-size": "35px"}
                ),
                width=12
            )
        ),

          # ---------- CHAT WINDOW ----------
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            "Conversation",
                            className="fw-semibold"
                        ),
                        dbc.CardBody(
                            [
                                
                                     ChatComponent(
                    id="cb-chat-component",
                    messages=[], 
                      container_style={
                    "height": "900px",
                    "overflowY": "auto",
                    },
                       # 🔤 Input box font
                    input_text_style={
                            "fontSize": "20px",
                    },

                    # 👤 User messages
                    user_bubble_style={
                        "fontSize": "20px",
                        "padding": "12px",
                        "backgroundColor":"#092744"
                    },

                    # 🤖 Assistant messages
                    assistant_bubble_style={
                    "fontSize": "20px",
                    "padding": "12px",
                    },
                    )
                            ],
                            style={"backgroundColor": "#fafafa"}
                        )
                    ],
                    className="shadow-sm"
                ),
                width=12
            )
        ),

        # ---------- ACTION BUTTONS ----------
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Save Chat",
                        id="btn-save-chat",
                        color="success",
                        className="w-100",
                        n_clicks=0
                    ),
                    width=3
                ),
            ],
            className="mt-3"
        ),

        # Hidden div to store chat history state
        dcc.Store(id="chat-history-store", data=[]),
        dcc.Download(id="download-report")

    ],
    fluid=True,
    className="p-4"
)

@callback(
    Output('cb-session-id', 'data'),
    Input('cb-session-id', 'data'),
    prevent_initial_call=False
)
def initialize_session(existing_session):
    if existing_session is None:
        return str(uuid.uuid4())
    print(existing_session) 
    return existing_session

@callback(
    Output('cb-chat-component', 'messages'),
    Input('cb-chat-component', 'new_message'),
    State('cb-chat-component', 'messages'),
    State('cb-session-id', 'data'),
    prevent_initial_call=True,
)
def new_message(query, messages, session_id):
    try:
        if not query:
            return messages

        if messages is None:
            messages = []

        # Append the full query dict (NOT just content)
        updated_messages = messages + [query]

        if query.get("role") == "user":
            user_text = query.get("content", "")

            params = {
                'user_query': user_text,
                'session_id': session_id
            }

            response = Ask_Chat_Agent(params=params)

            # Append assistant response as dict
            updated_messages.append({
                "role": "assistant",
                "content": response or "⚠️ Unable to answer query due to system error"
            })

        else:
            updated_messages.append({
                "role": "assistant",
                "content": "I cannot answer that at this time"
            })

        return updated_messages

    except Exception as e:

        if messages is None:
            messages = []

        messages.append({
            "role": "assistant",
            "content": f"⚠️ Unable to answer query due to system error [{e}]"
        })

        return messages