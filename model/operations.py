# model/operations.py
from pony.orm import db_session, select, delete, commit
from werkzeug.security import generate_password_hash
from datetime import date

from .user import User
from .project import Project

# Database initialization
@db_session
def initialize_db():
    if User.select().count() == 0:
        User(username='user1', password_hash=generate_password_hash('password1'), is_admin=False)
        User(username='admin', password_hash=generate_password_hash('adminpass'), is_admin=True)
        User(username='a', password_hash=generate_password_hash('a'), is_admin=True)

# User management functions
@db_session
def get_user(user_id):
    """Get a user by ID"""
    try:
        return User[int(user_id)]
    except (ValueError, TypeError):
        return None

@db_session
def get_user_by_username(username):
    """Get a user by username"""
    return User.get(username=username)

@db_session
def add_user(username, password, email=None, is_admin=False):
    """Add a new user to the database"""
    if User.get(username=username):
        return False
    
    User(
        username=username, 
        password_hash=generate_password_hash(password),
        email=email,
        is_admin=is_admin
    )
    return True

@db_session
def validate_user(username, password):
    """Validate user credentials"""
    user = User.get(username=username)
    if user and user.check_password(password):
        return user
    return None

@db_session
def list_all_users():
    """Return a list of all users (for administration)"""
    return select(u for u in User)[:]

@db_session
def promote_user_to_admin(user_id):
    """Promote a regular user to admin"""
    user = get_user(user_id)
    if user and not user.is_admin:
        user.is_admin = True
        return True
    return False

@db_session
def delete_user(user_id):
    """Delete a user and all their projects"""
    user = get_user(user_id)
    if user:
        # Projects managed by this user will be automatically deleted due to cascade_delete
        user.delete()
        return True
    return False

# Project management functions
@db_session
def create_project(name, start_date, manager_id):
    """Create a new project with the given manager"""
    manager = get_user(manager_id)
    if not manager:
        return False
    
    project = Project(
        name=name,
        start_date=start_date,
        manager=manager
    )

    commit()

    return project.id

@db_session
def get_project(project_id):
    """Get a project by ID"""
    try:
        return Project[int(project_id)]
    except (ValueError, TypeError):
        return None

@db_session
def close_project(project_id, end_date):
    """Close a project by setting its end date"""
    project = get_project(project_id)
    if not project:
        return False
    
    if end_date <= project.start_date:
        return False
        
    project.end_date = end_date
    return True

@db_session
def add_member_to_project(project_id, user_id):
    """Add a user as a member to a project"""
    project = get_project(project_id)
    user = get_user(user_id)
    
    if not project or not user:
        return False
    
    if user not in project.members:
        project.members.add(user)
        return True
    
    return False

@db_session
def remove_member_from_project(project_id, user_id):
    """Remove a user from a project's members"""
    project = get_project(project_id)
    user = get_user(user_id)
    
    if not project or not user:
        return False
    
    if user in project.members:
        project.members.remove(user)
        return True
    
    return False

@db_session
def get_user_managed_projects(user_id):
    """Get all projects managed by a user"""
    user = get_user(user_id)
    if not user:
        return []
    
    return list(user.managed_projects)

@db_session
def get_user_member_projects(user_id):
    """Get all projects where the user is a member"""
    user = get_user(user_id)
    if not user:
        return []
    
    return list(user.member_of_projects)