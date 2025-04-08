# controller/routing.py
import dash
from dash.dependencies import Input, Output
from flask_login import current_user, logout_user

from model import get_project
from view import (
    get_home_layout, get_dashboard_layout, get_login_layout, 
    get_register_layout, get_profile_layout, get_admin_layout, 
    get_projects_layout, get_project_detail_layout
)

def register_routing_callbacks(app):
    """Register page routing callbacks"""
    
    @app.callback(
        [Output('page-content', 'children'),
         Output('url', 'pathname', allow_duplicate=True)],
        [Input('url', 'pathname')],
        prevent_initial_call=True
    )
    def display_page(pathname):
        # Handle logout
        if pathname == '/logout':
            if current_user.is_authenticated:
                logout_user()
            return get_home_layout(), '/'
        
        # Authentication pages
        if pathname == '/login':
            if current_user.is_authenticated:
                return get_dashboard_layout(), '/dashboard'
            return get_login_layout(), dash.no_update
        
        if pathname == '/register':
            if current_user.is_authenticated:
                return get_dashboard_layout(), '/dashboard'
            return get_register_layout(), dash.no_update
        
        # Protected pages
        if pathname == '/dashboard':
            if current_user.is_authenticated:
                return get_dashboard_layout(), dash.no_update
            return get_login_layout(), '/login'
        
        if pathname == '/profile':
            if current_user.is_authenticated:
                return get_profile_layout(), dash.no_update
            return get_login_layout(), '/login'
            
        if pathname == '/admin':
            if current_user.is_authenticated:
                if current_user.is_admin:
                    return get_admin_layout(), dash.no_update
                return get_dashboard_layout(), '/dashboard'
            return get_login_layout(), '/login'
            
        if pathname == '/projects':
            if current_user.is_authenticated:
                return get_projects_layout(), dash.no_update
            return get_login_layout(), '/login'
            
        # Handle project detail pages
        if pathname.startswith('/project/'):
            if not current_user.is_authenticated:
                return get_login_layout(), '/login'
                
            try:
                project_id = int(pathname.split('/')[-1])
                project = get_project(project_id)
                if project:
                    return get_project_detail_layout(project_id), dash.no_update
            except:
                pass
            
            return get_projects_layout(), '/projects'
        
        # Default home page
        return get_home_layout(), dash.no_update