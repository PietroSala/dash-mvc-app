# view/components.py
from dash import html
import dash_bootstrap_components as dbc

def create_user_info_display(username, email=None, is_admin=False):
    """Creates the user info display component"""
    email_info = f"Email: {email}" if email else "No email provided"
    user_type = "Administrator" if is_admin else "Regular User"
    
    return html.Div([
        html.H4(f'Username: {username}'),
        html.P(email_info),
        html.P(f'Account Type: {user_type}'),
        dbc.Button('Edit Profile', id='edit-profile-button', color='primary', className='mr-2 me-2'),
        dbc.Button('Change Password', id='change-password-button', color='secondary')
    ])