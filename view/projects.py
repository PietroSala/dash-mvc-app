# view/projects.py

from dash import html, dash_table
import dash_bootstrap_components as dbc
from flask_login import current_user
from datetime import date

def get_projects_layout():
    """Returns the projects page layout"""
    return html.Div([
        html.H1('My Projects'),
        html.P('Create and manage your projects.'),
        
        # Project message area
        html.Div(id='project-message', className='mb-3'),
        
        # Row for action buttons
        dbc.Row([
            dbc.Col([
                dbc.Button('Create New Project', id='create-project-button', color='success', className='me-2'),
                dbc.Button('View Details', id='view-project-button', color='primary', className='me-2', disabled=True),
                dbc.Button('Add Member', id='add-member-button', color='info', className='me-2', disabled=True),
                dbc.Button('Close Project', id='close-project-button', color='warning', className='me-2', disabled=True),
                dbc.Button('Refresh', id='refresh-projects-button', color='secondary', className='me-2'),
            ], width=12, className='mb-3')
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

def create_projects_table(projects, is_manager=True):
    """Creates a data table for projects with row selection"""
    return dash_table.DataTable(
        id='projects-table' if is_manager else 'member-projects-table',
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Name', 'id': 'name'},
            {'name': 'Start Date', 'id': 'start_date'},
            {'name': 'End Date', 'id': 'end_date'},
            {'name': 'Status', 'id': 'status'},
            {'name': 'Manager', 'id': 'manager'},
            {'name': 'Members', 'id': 'member_count'}
        ],
        data=[
            {
                'id': project.id,
                'name': project.name,
                'start_date': project.start_date.strftime('%Y-%m-%d'),
                'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else 'Not set',
                'status': 'Completed' if project.end_date else 'Active',
                'manager': project.manager.username,
                'member_count': len(project.members)
            }
            for project in projects
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
            },
            {
                'if': {'filter_query': '{status} = "Active"'},
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            },
            {
                'if': {'filter_query': '{status} = "Completed"'},
                'backgroundColor': 'rgba(201, 203, 207, 0.2)',
            }
        ],
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in [
                {
                    'id': project.id,
                    'name': project.name,
                    'start_date': project.start_date,
                    'end_date': project.end_date if project.end_date else 'Not set',
                    'status': 'Completed' if project.end_date else 'Active',
                    'manager': project.manager.username,
                    'member_count': f"**Members:** {', '.join([member.username for member in project.members]) if project.members else 'None'}"
                }
                for project in projects
            ]
        ],
        tooltip_duration=None,
        style_table={'overflowX': 'auto'}
    )