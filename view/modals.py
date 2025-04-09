# view/modals.py
from dash import html
import dash_bootstrap_components as dbc
from datetime import date

def create_delete_user_modal():
    """Creates a confirmation modal for deleting users"""
    return dbc.Modal([
        dbc.ModalHeader("Confirm Deletion"),
        dbc.ModalBody("Are you sure you want to delete this user? All their projects will also be deleted."),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-delete-user", className="ms-auto", color="secondary"),
            dbc.Button("Delete", id="confirm-delete-user", color="danger"),
        ]),
    ], id="delete-user-modal")

def create_promote_user_modal():
    """Creates a confirmation modal for promoting users to admin"""
    return dbc.Modal([
        dbc.ModalHeader("Confirm Promotion"),
        dbc.ModalBody("Are you sure you want to promote this user to an administrator?"),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-promote-user", className="ms-auto", color="secondary"),
            dbc.Button("Promote", id="confirm-promote-user", color="info"),
        ]),
    ], id="promote-user-modal")

def create_project_modal():
    """Creates a modal for creating a new project"""
    return dbc.Modal([
        dbc.ModalHeader("Create New Project"),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Project Name"),
                        dbc.Input(id="project-name", type="text", placeholder="Enter project name"),
                    ])
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Start Date"),
                        dbc.Input(id="project-start-date", type="date", value=date.today().isoformat()),
                    ])
                ]),
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-create-project", className="ms-auto", color="secondary"),
            dbc.Button("Create", id="confirm-create-project", color="success"),
        ]),
    ], id="create-project-modal")

def create_add_member_modal():
    """Creates a modal for adding members to a project"""
    return dbc.Modal([
        dbc.ModalHeader("Add Member to Project"),
        dbc.ModalBody([
            html.Div(id="add-member-content"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-add-member", className="ms-auto", color="secondary"),
            dbc.Button("Add", id="confirm-add-member", color="success"),
        ]),
    ], id="add-member-modal")

def create_close_project_modal():
    """Creates a modal for closing a project"""
    return dbc.Modal([
        dbc.ModalHeader("Close Project"),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("End Date"),
                        dbc.Input(id="project-end-date", type="date", value=date.today().isoformat()),
                    ])
                ]),
                html.Div(id="close-project-error", className="text-danger mt-2")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-close-project", className="ms-auto", color="secondary"),
            dbc.Button("Close Project", id="confirm-close-project", color="warning"),
        ]),
    ], id="close-project-modal")

def create_delete_project_modal():
    """Creates a confirmation modal for deleting a project"""
    return dbc.Modal([
        dbc.ModalHeader("Confirm Project Deletion"),
        dbc.ModalBody("Are you sure you want to delete this project? This action cannot be undone and all project data will be permanently lost."),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-delete-project", className="ms-auto", color="secondary"),
            dbc.Button("Delete", id="confirm-delete-project", color="danger"),
        ]),
    ], id="delete-project-modal")