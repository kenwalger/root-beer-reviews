"""Shared Jinja2 templates configuration with global functions.

This module initializes the Jinja2 templates instance and registers
global template functions available to all templates.
"""
from fastapi.templating import Jinja2Templates
from datetime import datetime


# Create templates instance with global functions
templates: Jinja2Templates = Jinja2Templates(directory="app/templates")

# Add global function for current year (as a callable)
templates.env.globals["current_year"] = lambda: datetime.now().year

