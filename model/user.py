# model/user.py
from pony.orm import Required, Optional, PrimaryKey, Set
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .database import db

# Define the User entity
class User(db.Entity, UserMixin):
    username = Required(str, unique=True)
    password_hash = Required(str)
    email = Optional(str)
    is_active = Required(bool, default=True)
    is_admin = Required(bool, default=False)
    managed_projects = Set('Project', cascade_delete=True, reverse="manager")
    member_of_projects = Set('Project', reverse="members")
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)