from dash import dcc, html, callback ,Input, Output, State
import dash 
import dash_bootstrap_components as dbc
import json
from datetime import datetime
import os

from UILayer.DashAppUtilities import Send_Query, Send_Chat_To_Report_Generator

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
                                
                                dcc.Markdown(
                                    id="chat-output",
                                    children="*Ask a question to begin the conversation.*",
                                    style={
                                        "height": "420px",
                                        "overflowY": "auto",
                                        "whiteSpace": "pre-wrap"
                                    }
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

        # ---------- USER INPUT ----------
        dbc.Row(
            [
                dbc.Col(
                    dcc.Textarea(
                        id="chat-input",
                        placeholder="Type your question here...",
                        style={
                            "width": "100%",
                            "height": "90px",
                            "resize": "none"
                        }
                    ),
                    width=10
                ),
                dbc.Col(
                    dbc.Button(
                        "Send",
                        id="btn-send",
                        color="primary",
                        className="w-100 h-100",
                        n_clicks=0
                    ),
                    width=2
                )
            ],
            className="mt-3"
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

                dbc.Col(
                    dbc.Button(
                        "Clear Chat",
                        id="btn-clear-chat",
                        color="warning",
                        className="w-100",
                        n_clicks=0
                    ),
                    width=3
                ),
                dbc.Col(
                    html.Div(id="save-status", className="text-center mt-2"),
                    width=6
                )
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
    [Output("chat-output", "children"),
     Output("chat-input", "value"),
     Output("chat-history-store", "data")],
    Input("btn-send", "n_clicks"),
    [State("chat-input", "value"),
     State("chat-history-store", "data")],
    prevent_initial_call=True
)
def update_chat(n_clicks, user_input, stored_history):
    global chat_history
    
    if n_clicks > 0 and user_input:
        # Get answer from the chatbot
        answer = Send_Query(user_input)
        
        # Create message object
        message_obj = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_input": user_input,
            "assistant_response": answer
        }
        
        # Append to global chat history
        chat_history['Message'].append({'Query': user_input, 'Answer': answer})
        
        # Also update stored history for persistence
        if stored_history is None:
            stored_history = []
        stored_history.append(message_obj)
        
        # Build display text
        display_text = ""
        for msg in stored_history:
            display_text += f"**[{msg['timestamp']}]**\n\n"
            display_text += f"**User:** {msg['user_input']}\n\n"
            display_text += f"**Assistant:** {msg['assistant_response']}\n\n"
            display_text += "---\n\n"
        
        # Clear input field and return updated chat
        return display_text, "", stored_history
    
    return dash.no_update, dash.no_update, dash.no_update


@callback(
    Output("save-status", "children"),
    Output("download-report", "data"),
    Input("btn-save-chat", "n_clicks"),
    State("chat-history-store", "data"),
    prevent_initial_call=True
)
def save_chat_to_json(n_clicks, stored_history):
    if n_clicks > 0:
        if not stored_history or len(stored_history) == 0:
            return dbc.Alert("No chat history to save!", color="warning", duration=3000)
        
        # Create saved_chats directory if it doesn't exist
        save_dir = "UILayer/pages/saved_chats"
        os.makedirs(save_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.json"
        filepath = os.path.join(save_dir, filename)
        
        # Save to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stored_history, f, indent=4, ensure_ascii=False)
        
        reportName = f'Reports/chat_history_{timestamp}.pdf'

            
        # Save to Application Layer for report generation
        report_uri = Send_Chat_To_Report_Generator(stored_history, reportName=reportName)
        print(f"Sending file for download.")
        return (
            dbc.Alert(
                f"Chat saved successfully as {reportName}!",
                color="success",
                duration=4000
            ),
            
            dcc.send_file(report_uri))
    
    return "", dash.no_update


@callback(
    [Output("chat-output", "children", allow_duplicate=True),
     Output("chat-history-store", "data", allow_duplicate=True)],
    Input("btn-clear-chat", "n_clicks"),
    prevent_initial_call=True
)
def clear_chat(n_clicks):
    global chat_history
    
    if n_clicks > 0:
        # Clear global chat history
        chat_history = {
            "Message": []
        }
        
        # Reset display
        return "*Ask a question to begin the conversation.*", []
    
    return dash.no_update, dash.no_update