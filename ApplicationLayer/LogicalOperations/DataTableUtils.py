



def Generate_Dash_Table(Col_Dict, data):
    
    
    store_info_cols = [{'name':value, 'id':key, 'editable':False} for key, value in Col_Dict.items()]

    style_data_conditional = []
    
    for col in Col_Dict.keys():
    
        style_data_conditional.append(
        {
        'if': {
            'column_id': col
        },
        'width': '250px'
        })

    
   

    Table_Parts = {
    'Data': data.to_dict('records'),
    'Cols': store_info_cols,
    'StyleCond': style_data_conditional,
    'Style': {
        'style_cell':{
            'fontSize':'25px',
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

    del data

    return Table_Parts