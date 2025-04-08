# controller/admin.py
import dash
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from pony.orm import db_session
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
    
    # Callback to enable/disable action buttons based on row selection
    @app.callback(
        [Output('delete-selected-button', 'disabled'),
         Output('promote-selected-button', 'disabled'),
         Output('selected-user-id', 'data')],
        [Input('users-table', 'selected_rows')],
        [State('users-table', 'data')]
    )
    def update_action_buttons(selected_rows, table_data):
        if not selected_rows:
            return True, True, None
        
        selected_row = selected_rows[0]  # Get the first selected row
        selected_user = table_data[selected_row]
        selected_user_id = selected_user['id']
        is_admin = selected_user['type'] == 'Admin'
        is_current_user = current_user.id == selected_user_id
        
        # Both buttons disabled if current user is selected
        if is_current_user:
            return True, True, selected_user_id
            
        # Promote button disabled if user is already admin
        return False, is_admin, selected_user_id
    
    # Delete user callback
    @app.callback(
        [Output('delete-user-modal', 'is_open'),
         Output('admin-message', 'children', allow_duplicate=True)],
        [Input('delete-selected-button', 'n_clicks'),
         Input('confirm-delete-user', 'n_clicks'),
         Input('cancel-delete-user', 'n_clicks')],
        [State('delete-user-modal', 'is_open'),
         State('selected-user-id', 'data')],
        prevent_initial_call=True
    )
    @db_session
    def handle_delete_user(delete_clicks, confirm_clicks, cancel_clicks, is_open, user_id):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open, dash.no_update
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'delete-selected-button' and delete_clicks:
            return True, dash.no_update
            
        if trigger_id == 'cancel-delete-user':
            return False, dash.no_update
            
        if trigger_id == 'confirm-delete-user' and confirm_clicks:
            if user_id and delete_user(user_id):
                return False, dbc.Alert('User deleted successfully', color='success')
            else:
                return False, dbc.Alert('Failed to delete user', color='danger')
                
        return is_open, dash.no_update
    
    # Promote user callback
    @app.callback(
        [Output('promote-user-modal', 'is_open'),
         Output('admin-message', 'children', allow_duplicate=True)],
        [Input('promote-selected-button', 'n_clicks'),
         Input('confirm-promote-user', 'n_clicks'),
         Input('cancel-promote-user', 'n_clicks')],
        [State('promote-user-modal', 'is_open'),
         State('selected-user-id', 'data')],
        prevent_initial_call=True
    )
    @db_session
    def handle_promote_user(promote_clicks, confirm_clicks, cancel_clicks, is_open, user_id):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open, dash.no_update
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'promote-selected-button' and promote_clicks:
            return True, dash.no_update
            
        if trigger_id == 'cancel-promote-user':
            return False, dash.no_update
            
        if trigger_id == 'confirm-promote-user' and confirm_clicks:
            if user_id and promote_user_to_admin(user_id):
                return False, dbc.Alert('User promoted to admin successfully', color='success')
            else:
                return False, dbc.Alert('Failed to promote user', color='danger')
                
        return is_open, dash.no_update