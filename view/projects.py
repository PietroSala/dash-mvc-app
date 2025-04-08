# view/projects.py
from dash import html
import dash_bootstrap_components as dbc
from flask_login import current_user
from datetime import date

def get_projects_layout():
    """Returns the projects page layout"""
    return html.Div([
        html.H1('My Projects'),
        html.P('Create and manage your projects.'),
        
        dbc.Row([
            dbc.Col([
                dbc.Button('Create New Project', id='create-project-button', color='success', className='mb-3'),
                html.Div(id='project-message', className='mb-3'),
            ]),
        ]),
        
        # Projects tabs
        dbc.Tabs([
            dbc.Tab([
                html.Div(id='managed-projects-container', className='mt-3')
            ], label='Projects I Manage'),
            dbc.Tab([
                html.Div(id='member-projects-container', className='mt-3')
            ], label='Projects I\'m a Member Of')
        ])
    ])

def create_project_card(project):
    """Creates a project card component"""
    project_id = project.id
    status = "Active" if not project.end_date else "Completed"
    status_color = "success" if not project.end_date else "secondary"
    
    return dbc.Card([
        dbc.CardHeader([
            html.H4(project.name, className='d-inline'),
            dbc.Badge(status, color=status_color, className='ms-2')
        ]),
        dbc.CardBody([
            html.P(f'Start Date: {project.start_date}'),
            html.P(f'End Date: {project.end_date if project.end_date else "Not set"}'),
            html.H6('Project Manager:'),
            html.P(project.manager.username),
            html.H6('Project Members:'),
            html.Ul([html.Li(member.username) for member in project.members]) if project.members else html.P('No members yet')
        ]),
        dbc.CardFooter([
            dbc.Button('View Details', id={'type': 'view-project', 'index': project_id}, color='primary', className='me-2'),
            dbc.Button('Add Member', id={'type': 'add-member', 'index': project_id}, color='success', className='me-2') 
                if not project.end_date and project.manager.id == current_user.id else html.Div(),
            dbc.Button('Close Project', id={'type': 'close-project', 'index': project_id}, color='warning') 
                if not project.end_date and project.manager.id == current_user.id else html.Div()
        ])
    ], className='mb-3')

def get_project_detail_layout(project_id):
    """Returns the project detail page layout"""
    return html.Div(id="project-detail-content")

def create_project_detail_layout(project):
    """Creates a detailed view of a project"""
    return html.Div([
        html.H2(project.name),
        dbc.Badge("Active" if not project.end_date else "Completed", 
                 color="success" if not project.end_date else "secondary",
                 className="mb-3"),
        
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
                        html.Div(id="project-members-list"),
                        dbc.Button("Add Member", id="add-member-btn", 
                                  color="success", className="mt-3") if project.manager.id == current_user.id and not project.end_date else html.Div()
                    ])
                ])
            ], width=6)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Button("Back to Projects", href="/projects", color="primary", className="mt-3"),
                dbc.Button("Close Project", id="close-project-btn", 
                          color="warning", className="mt-3 ms-2") if project.manager.id == current_user.id and not project.end_date else html.Div()
            ])
        ])
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
        ]) for member in project.members
    ])