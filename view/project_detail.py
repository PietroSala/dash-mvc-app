# view/project_detail.py

from dash import html
import dash_bootstrap_components as dbc
from flask_login import current_user
from pony.orm import db_session

@db_session
def get_project_detail_layout(project_id):
    """Returns the project detail page layout"""
    from model import get_project
    
    project = get_project(project_id)
    if not project:
        return html.Div([
            html.H2("Project Not Found"),
            dbc.Button("Back to Projects", href="/projects", color="primary")
        ])
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H2(project.name, className="d-inline-block me-2"),
                dbc.Badge("Active" if not project.end_date else "Completed", 
                        color="success" if not project.end_date else "secondary",
                        className="mb-3 align-middle")
            ], width=10),
            dbc.Col([
                dbc.Button("Refresh", id="refresh-project-button", color="secondary", className="float-end")
            ], width=2)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Project Details"),
                    dbc.CardBody([
                        html.P(f"Start Date: {project.start_date}"),
                        html.P(f"End Date: {project.end_date if project.end_date else 'Not set'}"),
                        html.P(f"Manager: {project.manager.username}")
                    ])
                ])
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Project Members"),
                    dbc.CardBody([
                        create_member_list(project),
                        dbc.Button("Add Member", id={"type": "add-member", "index": project_id}, 
                                 color="success", className="mt-3") if project.manager.id == current_user.id and not project.end_date else html.Div()
                    ])
                ])
            ], width=6)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Button("Back to Projects", href="/projects", color="primary", className="mt-3"),
                dbc.Button("Close Project", id={"type": "close-project", "index": project_id}, 
                         color="warning", className="mt-3 ms-2") if project.manager.id == current_user.id and not project.end_date else html.Div(),
                dbc.Button("Delete Project", id={"type": "delete-project", "index": project_id}, 
                         color="danger", className="mt-3 ms-2") if project.manager.id == current_user.id else html.Div()
            ])
        ]),
        
        # Hidden buttons for callback compatibility
        html.Div([
            dbc.Button('Add Member', id='add-member-button', style={'display': 'none'}),
            dbc.Button('Close Project', id='close-project-button', style={'display': 'none'})
        ], style={'display': 'none'}),
        
        html.Div(id='project-message', className='mt-3')
    ])

def create_member_list(project):
    """Creates a list of project members with remove buttons if appropriate"""
    if not project.members:
        return html.P("No members yet")
    
    can_remove = project.manager.id == current_user.id and not project.end_date
    
    return html.Ul([
        html.Li([
            member.username,
            dbc.Button("Remove", id={'type': 'remove-member', 'index': member.id}, 
                     size="sm", color="danger", className="ms-2") if can_remove else html.Div()
        ], className="mb-2") for member in project.members
    ])