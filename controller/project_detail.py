# controller/project_detail.py

import dash
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from dash import html
import json
from pony.orm import db_session
from datetime import datetime
from flask_login import current_user

from model import (
    get_project, add_member_to_project,
    remove_member_from_project, close_project, list_all_users,
    delete_project
)

def register_project_detail_callbacks(app):
    """Register callbacks for project detail page"""
    
    # Refresh single project view
    @app.callback(
        Output('page-content', 'children', allow_duplicate=True),
        [Input('refresh-project-button', 'n_clicks')],
        [State('url', 'pathname')],
        prevent_initial_call=True
    )
    @db_session
    def refresh_project_view(n_clicks, pathname):
        if not n_clicks or not pathname or not pathname.startswith('/project/'):
            return dash.no_update
            
        try:
            project_id = int(pathname.split('/')[-1])
            from view.project_detail import get_project_detail_layout
            return get_project_detail_layout(project_id)
        except:
            return dash.no_update
    
    # Toggle add member modal for pattern matching buttons
    @app.callback(
        Output('add-member-modal', 'is_open', allow_duplicate=True),
        [Input({'type': 'add-member', 'index': ALL}, 'n_clicks')],
        [State('add-member-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_add_member_modal_pattern(pattern_clicks, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
            
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if '{' in trigger and '"type":"add-member"' in trigger:
            # For pattern matching, check if any clicks have occurred
            if any(click and click > 0 for click in pattern_clicks):
                return True
                
        return is_open
    
    # Toggle close project modal for pattern matching buttons
    @app.callback(
        Output('close-project-modal', 'is_open', allow_duplicate=True),
        [Input({'type': 'close-project', 'index': ALL}, 'n_clicks')],
        [State('close-project-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_close_project_modal_pattern(pattern_clicks, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
            
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if '{' in trigger and '"type":"close-project"' in trigger:
            # For pattern matching, check if any clicks have occurred
            if any(click and click > 0 for click in pattern_clicks):
                return True
                
        return is_open
    
    # Toggle delete project modal
    @app.callback(
        Output('delete-project-modal', 'is_open'),
        [Input({'type': 'delete-project', 'index': ALL}, 'n_clicks'),
         Input('confirm-delete-project', 'n_clicks'),
         Input('cancel-delete-project', 'n_clicks')],
        [State('delete-project-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_delete_project_modal(delete_clicks, confirm, cancel, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
            
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if '{' in trigger and '"type":"delete-project"' in trigger:
            # For pattern matching, check if any clicks have occurred
            if any(click and click > 0 for click in delete_clicks):
                return True
        elif trigger == 'confirm-delete-project' and confirm:
            return False
        elif trigger == 'cancel-delete-project' and cancel:
            return False
                
        return is_open
    
    # Update selected project ID for pattern matching buttons
    @app.callback(
        Output('selected-project-id', 'data', allow_duplicate=True),
        [Input({'type': 'add-member', 'index': ALL}, 'n_clicks'),
         Input({'type': 'close-project', 'index': ALL}, 'n_clicks'),
         Input({'type': 'delete-project', 'index': ALL}, 'n_clicks'),
         Input({'type': 'remove-member', 'index': ALL}, 'n_clicks')],
        [State('selected-project-id', 'data')],
        prevent_initial_call=True
    )
    def update_selected_project_id(add_clicks, close_clicks, delete_clicks, remove_clicks, current_project_id):
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_project_id
            
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Only process if actually triggered by a click
        if not any(add_clicks) and not any(close_clicks) and not any(delete_clicks) and not any(remove_clicks):
            return current_project_id
        
        # Handle add member buttons from project detail page
        if '{' in trigger and '"type":"add-member"' in trigger:
            try:
                button_data = json.loads(trigger)
                # Find the index of the button that was clicked
                for i, click in enumerate(add_clicks):
                    if click and click > 0:
                        return button_data['index']
            except:
                pass
                
        # Handle close project buttons from project detail page
        if '{' in trigger and '"type":"close-project"' in trigger:
            try:
                button_data = json.loads(trigger)
                # Find the index of the button that was clicked
                for i, click in enumerate(close_clicks):
                    if click and click > 0:
                        return button_data['index']
            except:
                pass
                
        # Handle delete project buttons from project detail page
        if '{' in trigger and '"type":"delete-project"' in trigger:
            try:
                button_data = json.loads(trigger)
                # Find the index of the button that was clicked
                for i, click in enumerate(delete_clicks):
                    if click and click > 0:
                        return button_data['index']
            except:
                pass
        
        # For remove member buttons, we keep the current project ID
        return current_project_id
        
    # Delete project callback
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        [Input('confirm-delete-project', 'n_clicks')],
        [State('selected-project-id', 'data')],
        prevent_initial_call=True
    )
    @db_session
    def delete_project_callback(n_clicks, project_id):
        if not n_clicks or not project_id:
            return dash.no_update
        
        # Delete the project and redirect to projects page
        if delete_project(project_id, current_user.id):
            return '/projects'
        
        return dash.no_update
    
    # Remove member from project
    @app.callback(
        Output('project-message', 'children', allow_duplicate=True),
        [Input({'type': 'remove-member', 'index': ALL}, 'n_clicks')],
        [State('selected-project-id', 'data')],
        prevent_initial_call=True
    )
    @db_session
    def remove_member_callback(remove_clicks, project_id):
        ctx = dash.callback_context
        if not ctx.triggered or not any(remove_clicks) or not project_id:
            return dash.no_update
            
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        try:
            button_data = json.loads(trigger)
            user_id = button_data['index']
            
            # Find the index of the button that was clicked
            for i, click in enumerate(remove_clicks):
                if click and click > 0:
                    if remove_member_from_project(project_id, user_id):
                        return dbc.Alert('Member removed successfully', color='success')
                    else:
                        return dbc.Alert('Failed to remove member', color='danger')
        except:
            return dbc.Alert('An error occurred', color='danger')