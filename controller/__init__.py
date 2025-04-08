# controller/__init__.py
from .callbacks import register_callbacks

# Re-export the main functions to maintain compatibility
__all__ = ['register_callbacks']