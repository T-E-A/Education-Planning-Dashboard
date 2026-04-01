



def Generate_Dash_Table(Col_Dict, data, *,errorMessage= None):
    try:
        store_info_cols = [
            {'name': value, 'id': key, 'editable': False}
            for key, value in Col_Dict.items()
        ]

        style_data_conditional = [
            {
                'if': {'column_id': col},
                'width': '250px'
            }
            for col in Col_Dict.keys()
        ]

        Table_Parts = {
            'Data': data.to_dict('records'),
            'Cols': store_info_cols,
            'StyleCond': style_data_conditional,
            'Style': {
                'style_cell': {
                    'fontSize': '25px',
                    'textAlign': 'right',
                    'minWidth': '150px',
                    'maxWidth': '150px',
                    'width': '150px',
                },
                'style_header': {
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'right'
                }
            }
        }

        return Table_Parts

    except Exception as e:
        # Fallback structure (must match schema)

        if errorMessage:
            error_message = str(errorMessage)
        else:
            error_message = e

        fallback_cols = [
            {'name': 'Error', 'id': 'Error', 'editable': False}
        ]

        fallback_data = [
            {'Error': f"⚠️ Error generating table: {error_message}"}
        ]

        Table_Parts = {
            'Data': fallback_data,
            'Cols': fallback_cols,
            'StyleCond': [],
            'Style': {
                'style_cell': {
                    'fontSize': '25px',
                    'textAlign': 'left',
                    'color': 'red',
                    'minWidth': '150px',
                    'maxWidth': '500px',
                    'width': '500px',
                },
                'style_header': {
                    'backgroundColor': '#8B0000',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'left'
                }
            }
        }

        return Table_Parts