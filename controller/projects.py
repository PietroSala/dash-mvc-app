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
from view import create_project_card

def register_project_callbacks(app):
    """Register project management related callbacks"""
    
    # Load projects data
    @app.callback(
        [Output('managed-projects-container', 'children'),
         Output('member-projects-container', 'children')],
        [Input('url', 'pathname')]
    )
    @db_session
    def load_projects(pathname):
        if pathname != '/projects' or not current_user.is_authenticated:
            return dash.no_update, dash.no_update
            
        # Get projects the user manages
        managed_projects = get_user_managed_projects(current_user.id)
        managed_cards = [create_project_card(project) for project in managed_projects]
        
        if not managed_cards:
            managed_content = html.P("You don't have any projects yet. Create one using the button above.")
        else:
            managed_content = html.Div(managed_cards)
            
        # Get projects the user is a member of
        member_projects = get_user_member_projects(current_user.id)
        member_cards = [create_project_card(project) for project in member_projects]
        
        if not member_cards:
            member_content = html.P("You are not a member of any projects yet.")
        else:
            member_content = html.Div(member_cards)
            
        return managed_content, member_content
    
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
        
        if button_id == 'create-project-button':
            return True
        elif button_id == 'confirm-create-project' or button_id == 'cancel-create-project':
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
        
        project_id = create_project(name, start_date_obj, current_user.id)
        if project_id:
            return dbc.Alert('Project created successfully', color='success')
        else:
            return dbc.Alert('Failed to create project', color='danger')
    
    # Toggle add member modal
    @app.callback(
        [Output('add-member-modal', 'is_open'),
         Output('selected-project-id', 'data')],
        [Input({'type': 'add-member', 'index': ALL}, 'n_clicks'),
         Input('confirm-add-member', 'n_clicks'),
         Input('cancel-add-member', 'n_clicks')],
        [State('add-member-modal', 'is_open')]
    )
    def toggle_add_member_modal(add_clicks, confirm, cancel, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open, dash.no_update
            
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger == 'confirm-add-member' or trigger == 'cancel-add-member':
            return False, dash.no_update
            
        if any(add_clicks):
            try:
                button_id = json.loads(trigger)
                return True, button_id['index']
            except:
                pass
                
        return is_open, dash.no_update
    
    # Populate add member form
    @app.callback(
        Output('add-member-content', 'children'),
        [Input('add-member-modal', 'is_open')],
        [State('selected-project-id', 'data')]
    )
    @db_session
    def populate_add_member_form(is_open, project_id):
        if not is_open or not project_id:
            return dash.no_update
            
        # Get all users who aren't already members of this project
        project = get_project(project_id)
        if not project:
            return html.P("Project not found")
            
        all_users = list_all_users()
        available_users = [user for user in all_users 
                          if user.id != current_user.id and user not in project.members]
        
        if not available_users:
            return html.P("No available users to add")
            
        return html.Div([
            html.P(f"Add a member to project: {project.name}"),
            dbc.Label("Select User"),
            dbc.Select(
                id="member-select",
                options=[{"label": user.username, "value": user.id} for user in available_users],
                value=available_users[0].id if available_users else None
            )
        ])
    
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
        [Output('close-project-modal', 'is_open'),
         Output('selected-project-id', 'data', allow_duplicate=True)],
        [Input({'type': 'close-project', 'index': ALL}, 'n_clicks'),
         Input('confirm-close-project', 'n_clicks'),
         Input('cancel-close-project', 'n_clicks')],
        [State('close-project-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_close_project_modal(close_clicks, confirm, cancel, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open, dash.no_update
            
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger == 'confirm-close-project' or trigger == 'cancel-close-project':
            return False, dash.no_update
            
        if any(close_clicks):
            try:
                button_id = json.loads(trigger)
                return True, button_id['index']
            except:
                pass
                
        return is_open, dash.no_update
    
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
            button_id = json.loads(trigger)
            user_id = button_id['index']
            
            if remove_member_from_project(project_id, user_id):
                return dbc.Alert('Member removed successfully', color='success')
            else:
                return dbc.Alert('Failed to remove member', color='danger')
        except:
            return dbc.Alert('An error occurred', color='danger')