# view/layout.py
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from flask_login import current_user

from .modals import (
    create_delete_user_modal, create_promote_user_modal,
    create_project_modal, create_add_member_modal, create_close_project_modal,
    create_delete_project_modal
)

# Main app layout
def get_app_layout():
    """Returns the main app layout"""
    return html.Div([
        dcc.Location(id='url', refresh=True),
        html.Div(id='navbar-container'),
        html.Div(id='page-content', className='container mt-4'),
        
        # Hidden containers for storing state
        dcc.Store(id='selected-user-id'),
        dcc.Store(id='selected-project-id'),
        
        # Modals for various actions
        create_delete_user_modal(),
        create_promote_user_modal(),
        create_project_modal(),
        create_add_member_modal(),
        create_close_project_modal(),
        create_delete_project_modal()
    ])

# Home page layout
def get_home_layout():
    """Returns the home page layout"""
    return html.Div([
        html.H1('Welcome to the Dash Multi-Page App'),
        html.P('This is a template for a multi-page Dash application with authentication.'),
        html.Ul([
            html.Li('Multiple pages with URL routing'),
            html.Li('User authentication with login/logout'),
            html.Li('Dynamic navigation based on login status'),
            html.Li('Protected routes for authenticated users only'),
            html.Li('Admin capabilities for user management'),
            html.Li('Project management functionality'),
            html.Li('Pony ORM with SQLite database')
        ])
    ])

# Dashboard page layout (protected)
def get_dashboard_layout():
    """Returns the dashboard page layout"""
    return html.Div([
        html.H1('Dashboard'),
        html.P('This is a protected dashboard page. Only logged-in users can see this.'),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader('My Profile'),
                dbc.CardBody([
                    html.H4('Account Overview', className='card-title'),
                    html.P('View and manage your profile information.'),
                    dbc.Button('Go to Profile', href='/profile', color='primary')
                ])
            ]), width=4),
            dbc.Col(dbc.Card([
                dbc.CardHeader('My Projects'),
                dbc.CardBody([
                    html.H4('Project Management', className='card-title'),
                    html.P('View and manage your projects.'),
                    dbc.Button('View Projects', href='/projects', color='primary')
                ])
            ]), width=4),
            dbc.Col(dbc.Card([
                dbc.CardHeader('Admin Panel' if hasattr(current_user, 'is_admin') and current_user.is_admin else 'Notifications'),
                dbc.CardBody([
                    html.H4('Admin Tools' if hasattr(current_user, 'is_admin') and current_user.is_admin else 'System Notifications', className='card-title'),
                    html.P('Manage users and system settings.' if hasattr(current_user, 'is_admin') and current_user.is_admin else 'You have no new notifications.'),
                    dbc.Button('Go to Admin Panel', href='/admin', color='primary') if hasattr(current_user, 'is_admin') and current_user.is_admin else html.Div()
                ])
            ]), width=4)
        ])
    ])

# Profile page layout (protected)
def get_profile_layout():
    """Returns the profile page layout"""
    return html.Div([
        html.H1('User Profile'),
        html.P('This is your profile page. Here you can view your account details.'),
        html.Div(id='user-info')
    ])