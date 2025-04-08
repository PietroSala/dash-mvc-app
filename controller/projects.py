# controller/projects.py

import dash
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from dash import html
import json
from pony.orm import db_session
from datetime import datetime
from flask_login import current_user

from model import (
    create_project, get_project, get_user_managed_projects, 
    get_user_member_projects, add_member_to_project, 
    remove_member_from_project, close_project, list_all_users
)
from view import create_projects_table

def register_project_callbacks(app):
    """Register project management related callbacks"""
    
    # Load projects data
    # Modify the load_projects callback to include the refresh button as an input
    @app.callback(
        [Output('managed-projects-container', 'children'),
        Output('member-projects-container', 'children')],
        [Input('url', 'pathname'),
        Input('refresh-projects-button', 'n_clicks')]
    )
    @db_session
    def load_projects(pathname, n_clicks):
        # Check if we're on the projects page or a refresh was clicked
        if (pathname != '/projects' and not n_clicks) or not current_user.is_authenticated:
            return dash.no_update, dash.no_update
            
        # Get projects the user manages
        managed_projects = get_user_managed_projects(current_user.id)
        if not managed_projects:
            managed_content = html.P("You don't have any projects yet. Create one using the button above.")
        else:
            managed_content = create_projects_table(managed_projects, True)
            
        # Get projects the user is a member of
        member_projects = get_user_member_projects(current_user.id)
        if not member_projects:
            member_content = html.P("You are not a member of any projects yet.")
        else:
            member_content = create_projects_table(member_projects, False)
            
        return managed_content, member_content
    
    # Enable/disable action buttons based on project selection
    @app.callback(
        [Output('view-project-button', 'disabled'),
         Output('add-member-button', 'disabled'),
         Output('close-project-button', 'disabled'),
         Output('selected-project-id', 'data')],
        [Input('projects-table', 'selected_rows')],
        [State('projects-table', 'data')]
    )
    def update_project_buttons(selected_rows, table_data):
        if not selected_rows or not table_data:
            return True, True, True, None
        
        selected_row = selected_rows[0]
        selected_project = table_data[selected_row]
        project_id = selected_project['id']
        is_active = selected_project['status'] == 'Active'
        
        # View button is always enabled for selected project
        # Add Member and Close Project buttons are only enabled for active projects
        return False, not is_active, not is_active, project_id
    
    # Create project modal toggle
    @app.callback(
        Output('create-project-modal', 'is_open'),
        [Input('create-project-button', 'n_clicks'),
         Input('confirm-create-project', 'n_clicks'),
         Input('cancel-create-project', 'n_clicks')],
        [State('create-project-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_create_project_modal(create_clicks, confirm, cancel, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'create-project-button' and create_clicks:
            return True
        elif button_id == 'confirm-create-project' and confirm:
            return False
        elif button_id == 'cancel-create-project' and cancel:
            return False
            
        return is_open
    
    # Create new project
    @app.callback(
    Output('project-message', 'children'),
    [Input('confirm-create-project', 'n_clicks')],
    [State('project-name', 'value'),
     State('project-start-date', 'value')]
    )
    @db_session
    def create_new_project(n_clicks, name, start_date):
        if not n_clicks or not name or not start_date:
            return dash.no_update
            
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        print(f"Creating project: {name}, {start_date_obj}, {current_user.id}")
        project_id = create_project(name, start_date_obj, current_user.id)
        print(f"Project creation result: {project_id}")
        
        if project_id:
            return dbc.Alert('Project created successfully', color='success')
        else:
            return dbc.Alert('Failed to create project', color='danger')
    
    # Handle view project button
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        [Input('view-project-button', 'n_clicks')],
        [State('selected-project-id', 'data')],
        prevent_initial_call=True
    )
    def navigate_to_project(n_clicks, project_id):
        if n_clicks and project_id:
            return f'/project/{project_id}'
        return dash.no_update
    
    # Toggle add member modal
    @app.callback(
        Output('add-member-modal', 'is_open'),
        [Input('add-member-button', 'n_clicks'),
         Input('confirm-add-member', 'n_clicks'),
         Input('cancel-add-member', 'n_clicks'),
         Input({'type': 'add-member', 'index': ALL}, 'n_clicks')],
        [State('add-member-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_add_member_modal(add_clicks, confirm, cancel, pattern_clicks, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
            
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Check if the click count is actually greater than 0 for the triggered button
        if trigger == 'add-member-button' and add_clicks:
            return True
        elif ('{' in trigger and '"type":"add-member"' in trigger):
            # For pattern matching, check if any clicks have occurred
            if any(click and click > 0 for click in pattern_clicks):
                return True
        elif trigger == 'confirm-add-member' and confirm:
            return False
        elif trigger == 'cancel-add-member' and cancel:
            return False
            
        return is_open
    
    # Populate add member form and update selected project ID for pattern matching buttons
    @app.callback(
        [Output('add-member-content', 'children'),
         Output('selected-project-id', 'data', allow_duplicate=True)],
        [Input('add-member-modal', 'is_open'),
         Input({'type': 'add-member', 'index': ALL}, 'n_clicks')],
        [State('selected-project-id', 'data')],
        prevent_initial_call=True
    )
    @db_session
    def populate_add_member_form(is_open, pattern_clicks, project_id):
        ctx = dash.callback_context
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Handle pattern matching buttons
        if '{' in trigger and '"type":"add-member"' in trigger:
            try:
                button_data = json.loads(trigger)
                project_id = button_data['index']
            except:
                pass
        
        if not is_open or not project_id:
            return dash.no_update, project_id
            
        # Get all users who aren't already members of this project
        project = get_project(project_id)
        if not project:
            return html.P("Project not found"), project_id
            
        all_users = list_all_users()
        available_users = [user for user in all_users 
                          if user.id != current_user.id and user not in project.members]
        
        if not available_users:
            return html.P("No available users to add"), project_id
            
        return html.Div([
            html.P(f"Add a member to project: {project.name}"),
            dbc.Label("Select User"),
            dbc.Select(
                id="member-select",
                options=[{"label": user.username, "value": user.id} for user in available_users],
                value=available_users[0].id if available_users else None
            )
        ]), project_id
    
    # Add member to project
    @app.callback(
        Output('project-message', 'children', allow_duplicate=True),
        [Input('confirm-add-member', 'n_clicks')],
        [State('selected-project-id', 'data'),
         State('member-select', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def add_member_to_project_callback(n_clicks, project_id, user_id):
        if not n_clicks or not project_id or not user_id:
            return dash.no_update
            
        if add_member_to_project(project_id, user_id):
            return dbc.Alert('Member added successfully', color='success')
        else:
            return dbc.Alert('Failed to add member', color='danger')
    
    # Toggle close project modal
    @app.callback(
        Output('close-project-modal', 'is_open'),
        [Input('close-project-button', 'n_clicks'),
         Input('confirm-close-project', 'n_clicks'),
         Input('cancel-close-project', 'n_clicks'),
         Input({'type': 'close-project', 'index': ALL}, 'n_clicks')],
        [State('close-project-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_close_project_modal(close_clicks, confirm, cancel, pattern_clicks, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
            
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger == 'close-project-button' and close_clicks:
            return True
        elif ('{' in trigger and '"type":"close-project"' in trigger):
            # For pattern matching, check if any clicks have occurred
            if any(click and click > 0 for click in pattern_clicks):
                return True
        elif trigger == 'confirm-close-project' and confirm:
            return False
        elif trigger == 'cancel-close-project' and cancel:
            return False
            
        return is_open
    
    # Update selected project ID for pattern matching buttons
    @app.callback(
        Output('selected-project-id', 'data', allow_duplicate=True),
        [Input({'type': 'close-project', 'index': ALL}, 'n_clicks'),
         Input({'type': 'remove-member', 'index': ALL}, 'n_clicks')],
        [State('selected-project-id', 'data')],
        prevent_initial_call=True
    )
    def update_selected_project_id(close_clicks, remove_clicks, current_project_id):
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_project_id
            
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Only process if actually triggered by a click
        if not any(close_clicks) and not any(remove_clicks):
            return current_project_id
        
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
        
        # For remove member buttons, we keep the current project ID
        return current_project_id
    
    # Close project
    @app.callback(
        [Output('project-message', 'children', allow_duplicate=True),
         Output('close-project-error', 'children')],
        [Input('confirm-close-project', 'n_clicks')],
        [State('selected-project-id', 'data'),
         State('project-end-date', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def close_project_callback(n_clicks, project_id, end_date):
        if not n_clicks or not project_id or not end_date:
            return dash.no_update, ""
            
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Check if project exists and user is the manager
        project = get_project(project_id)
        if not project:
            return dbc.Alert('Project not found', color='danger'), ""
            
        if project.manager.id != current_user.id:
            return dbc.Alert('Only the project manager can close a project', color='danger'), ""
            
        # Try to close the project
        if close_project(project_id, end_date_obj):
            return dbc.Alert('Project closed successfully', color='success'), ""
        else:
            return dash.no_update, "End date must be after the start date"
    
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