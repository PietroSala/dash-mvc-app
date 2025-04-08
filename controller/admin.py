# controller/admin.py
import dash
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from pony.orm import db_session
import re
import json
from flask_login import current_user

from model import list_all_users, promote_user_to_admin, delete_user
from view import create_users_table

def register_admin_callbacks(app):
    """Register admin panel related callbacks"""
    
    # Callback to populate users table in admin panel
    @app.callback(
        Output('users-table-container', 'children'),
        [Input('url', 'pathname'),
         Input('refresh-users-button', 'n_clicks')]
    )
    @db_session
    def populate_users_table(pathname, n_clicks):
        if pathname == '/admin' and current_user.is_authenticated and current_user.is_admin:
            users = list_all_users()
            return create_users_table(users)
        return ''
    
    # Callback to handle clicks on table actions
    @app.callback(
        [Output('delete-user-modal', 'is_open'),
        Output('selected-user-id', 'data')],
        [Input('users-table', 'active_cell')],
        [State('users-table', 'data')],
        prevent_initial_call=True
    )
    def toggle_delete_modal(active_cell, table_data):
        """Handle clicks on the delete link in the users table"""
        if not active_cell or active_cell['column_id'] != 'actions':
            return False, dash.no_update
        
        row_id = active_cell['row']
        action_text = table_data[row_id]['actions']
        
        # Check if this cell contains a delete link
        delete_match = re.search(r'\[Delete User\]\(delete-(\d+)\)', action_text)
        if delete_match:
            user_id = int(delete_match.group(1))
            return True, user_id
        
        return False, dash.no_update

    @app.callback(
        [Output('promote-user-modal', 'is_open', allow_duplicate=True),
        Output('selected-user-id', 'data', allow_duplicate=True)],
        [Input('users-table', 'active_cell')],
        [State('users-table', 'data')],
        prevent_initial_call=True
    )
    def toggle_promote_modal(active_cell, table_data):
        """Handle clicks on the promote link in the users table"""
        if not active_cell or active_cell['column_id'] != 'actions':
            return False, dash.no_update
        
        row_id = active_cell['row']
        action_text = table_data[row_id]['actions']
        
        # Check if this cell contains a promote link
        promote_match = re.search(r'\[Promote to Admin\]\(promote-(\d+)\)', action_text)
        if promote_match:
            user_id = int(promote_match.group(1))
            return True, user_id
        
        return False, dash.no_update

    # Store selected user ID for delete action
    @app.callback(
        Output('selected-user-id', 'data', allow_duplicate=True),
        Input({'type': 'delete-button', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def store_selected_user_id(delete_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        try:
            button_data = json.loads(button_id)
            return button_data['index']
        except:
            return dash.no_update
    
    # Delete user callback
    @app.callback(
        Output('admin-message', 'children'),
        Input('confirm-delete-user', 'n_clicks'),
        State('selected-user-id', 'data'),
        prevent_initial_call=True
    )
    @db_session
    def delete_user_callback(n_clicks, user_id):
        if not n_clicks or not user_id:
            return dash.no_update
            
        if delete_user(user_id):
            return dbc.Alert('User deleted successfully', color='success')
        else:
            return dbc.Alert('Failed to delete user', color='danger')
    
    # Toggle promote user modal
    @app.callback(
        Output('promote-user-modal', 'is_open'),
        [Input({'type': 'promote-button', 'index': ALL}, 'n_clicks'),
         Input('confirm-promote-user', 'n_clicks'),
         Input('cancel-promote-user', 'n_clicks')],
        [State('promote-user-modal', 'is_open')]
    )
    def toggle_promote_modal(promote_clicks, confirm, cancel, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'confirm-promote-user' or button_id == 'cancel-promote-user':
            return False
            
        if any(promote_clicks):
            return True
            
        return is_open
    
    # Store selected user ID for promote action
    @app.callback(
        Output('selected-user-id', 'data', allow_duplicate=True),
        Input({'type': 'promote-button', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def store_promoted_user_id(promote_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        try:
            button_data = json.loads(button_id)
            return button_data['index']
        except:
            return dash.no_update
    
    # Promote user callback
    @app.callback(
        Output('admin-message', 'children', allow_duplicate=True),
        Input('confirm-promote-user', 'n_clicks'),
        State('selected-user-id', 'data'),
        prevent_initial_call=True
    )
    @db_session
    def promote_user_callback(n_clicks, user_id):
        if not n_clicks or not user_id:
            return dash.no_update
            
        if promote_user_to_admin(user_id):
            return dbc.Alert('User promoted to admin successfully', color='success')
        else:
            return dbc.Alert('Failed to promote user', color='danger')