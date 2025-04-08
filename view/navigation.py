# view/navigation.py
import dash_bootstrap_components as dbc
from flask_login import current_user

def get_navbar():
    """Returns the appropriate navbar based on user authentication status"""
    if current_user.is_authenticated:
        # Navigation for logged-in users
        nav_items = [
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
            dbc.NavItem(dbc.NavLink("Profile", href="/profile")),
            dbc.NavItem(dbc.NavLink("My Projects", href="/projects")),
        ]
        
        # Add Admin section if user is admin
        if hasattr(current_user, 'is_admin') and current_user.is_admin:
            nav_items.append(dbc.NavItem(dbc.NavLink("Admin Panel", href="/admin")))
            
        nav_items.append(dbc.NavItem(dbc.NavLink("Logout", href="/logout")))
        
        navbar = dbc.NavbarSimple(
            children=nav_items,
            brand="My Dash App",
            brand_href="/",
            color="primary",
            dark=True,
        )
    else:
        # Navigation for guests
        navbar = dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Login", href="/login")),
                dbc.NavItem(dbc.NavLink("Register", href="/register")),
            ],
            brand="My Dash App",
            brand_href="/",
            color="primary",
            dark=True,
        )
    return navbar