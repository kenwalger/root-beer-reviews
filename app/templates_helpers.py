"""Shared Jinja2 templates configuration with global functions."""
from fastapi.templating import Jinja2Templates
from datetime import datetime


# Create templates instance with global functions
templates = Jinja2Templates(directory="app/templates")

# Add global function for current year (as a callable)
templates.env.globals["current_year"] = lambda: datetime.now().year

