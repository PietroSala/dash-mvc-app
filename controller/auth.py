# controller/auth.py
import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import login_user, logout_user, current_user
from pony.orm import db_session

from model import validate_user, add_user, get_user_by_username

def register_auth_callbacks(app):
    """Register authentication-related callbacks"""
    
    # Callback for login form
    @app.callback(
        [Output('login-output', 'children'),
         Output('url', 'pathname', allow_duplicate=True)],
        [Input('login-button', 'n_clicks')],
        [State('login-username', 'value'),
         State('login-password', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def login_callback(n_clicks, username, password):
        if not n_clicks or not username or not password:
            return '', dash.no_update
        
        user = validate_user(username, password)
        if user:
            login_user(user)
            return dbc.Alert('Login successful!', color='success'), '/dashboard'
        else:
            return dbc.Alert('Invalid username or password', color='danger'), dash.no_update
    
    # Callback for register form
    @app.callback(
        [Output('register-output', 'children'),
         Output('url', 'pathname', allow_duplicate=True)],
        [Input('register-button', 'n_clicks')],
        [State('register-username', 'value'),
         State('register-password', 'value'),
         State('register-confirm-password', 'value'),
         State('register-email', 'value')],
        prevent_initial_call=True
    )
    @db_session
    def register_callback(n_clicks, username, password, confirm_password, email):
        if not n_clicks or not username or not password or not confirm_password:
            return '', dash.no_update
        
        if password != confirm_password:
            return dbc.Alert('Passwords do not match', color='danger'), dash.no_update
        
        # Try to add the user with the optional email
        if add_user(username, password, email):
            return dbc.Alert('Registration successful! Please log in.', color='success'), '/login'
        else:
            return dbc.Alert('Username already exists', color='danger'), dash.no_update
    
    # Callback to display user info on profile page
    @app.callback(
        Output('user-info', 'children'),
        Input('url', 'pathname')
    )
    @db_session
    def display_user_info(pathname):
        if pathname == '/profile' and current_user.is_authenticated:
            # Get fresh user data from database
            from view import create_user_info_display
            user = get_user_by_username(current_user.username)
            if user:
                return create_user_info_display(user.username, user.email, user.is_admin)
        return ''