# view/admin.py
from dash import html, dash_table
import dash_bootstrap_components as dbc
from flask_login import current_user

def get_admin_layout():
    """Returns the admin panel layout"""
    return html.Div([
        html.H1('Admin Panel'),
        html.P('Manage users and system settings.'),
        
        html.H3('User Management', className='mt-4'),
        html.Div(id='admin-message', className='mb-3'),
        
        # Row for action buttons
        dbc.Row([
            dbc.Col([
                dbc.Button('Refresh User List', id='refresh-users-button', color='primary', className='me-2'),
                dbc.Button('Delete Selected', id='delete-selected-button', color='danger', className='me-2', disabled=True),
                dbc.Button('Promote Selected', id='promote-selected-button', color='success', disabled=True),
            ], width=12, className='mb-3')
        ]),
        
        # User table
        html.Div(id='users-table-container')
    ])

def create_users_table(users):
    """Creates a data table for users with row selection"""
    return dash_table.DataTable(
        id='users-table',
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Username', 'id': 'username'},
            {'name': 'Email', 'id': 'email'},
            {'name': 'Type', 'id': 'type'}
        ],
        data=[
            {
                'id': user.id,
                'username': user.username,
                'email': user.email or 'N/A',
                'type': 'Admin' if user.is_admin else 'User'
            }
            for user in users
        ],
        row_selectable='single',
        selected_rows=[],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ]
    )