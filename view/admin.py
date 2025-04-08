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
        
        dbc.Button('Refresh User List', id='refresh-users-button', color='primary', className='mb-3'),
        
        # User table
        html.Div(id='users-table-container')
    ])

def create_users_table(users):
    """Creates a data table for users using proper Dash approach"""
    return dash_table.DataTable(
        id='users-table',
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Username', 'id': 'username'},
            {'name': 'Email', 'id': 'email'},
            {'name': 'Type', 'id': 'type'},
            # Using clickable links for actions
            {'name': 'Actions', 'id': 'actions', 'presentation': 'markdown'}
        ],
        data=[
            {
                'id': user.id,
                'username': user.username,
                'email': user.email or 'N/A',
                'type': 'Admin' if user.is_admin else 'User',
                'actions': create_action_links(user.id, user.is_admin)
            }
            for user in users
        ],
        markdown_options={'html': True, 'link_target': '_self'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'actions'},
                'minWidth': '200px',
            }
        ]
    )

def create_action_links(user_id, is_admin):
    """Creates markdown links for actions in the DataTable"""
    if current_user.id == user_id:
        return "Cannot modify self"
    
    actions = []
    
    if not is_admin:
        actions.append(f'[Promote to Admin](promote-{user_id})')
    
    actions.append(f'[Delete User](delete-{user_id})')
    
    # Join actions with a separator
    return ' | '.join(actions)