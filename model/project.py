# model/project.py
from pony.orm import Required, Optional, Set
from datetime import date

from .database import db

# Define the Project entity
class Project(db.Entity):
    name = Required(str)
    start_date = Required(date)
    end_date = Optional(date)
    manager = Required("User", reverse="managed_projects")
    members = Set("User", reverse="member_of_projects")
    dot_graph = Optional(str, default="digraph G {\n  A -> B;\n  B -> C;\n  C -> A;\n}")