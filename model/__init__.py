# model/__init__.py
# Import and configure database
from .database import db, configure_db

# Import entity classes
from .user import User
from .project import Project

# Import all operations for external use
from .operations import (
    initialize_db, get_user, get_user_by_username, add_user, validate_user,
    list_all_users, promote_user_to_admin, delete_user, create_project,
    get_project, close_project, add_member_to_project, remove_member_from_project,
    get_user_managed_projects, get_user_member_projects, delete_project,
    update_dot_graph
)

# Configure the database when the module is imported
configure_db()

# Initialize the database with default users
initialize_db()

# Export all necessary functions to maintain compatibility with existing imports
__all__ = [
    'db', 'User', 'Project',
    'initialize_db', 'get_user', 'get_user_by_username', 'add_user', 'validate_user',
    'list_all_users', 'promote_user_to_admin', 'delete_user', 'create_project',
    'get_project', 'close_project', 'add_member_to_project', 'remove_member_from_project',
    'get_user_managed_projects', 'get_user_member_projects', 'delete_project',
    'update_dot_graph'
]