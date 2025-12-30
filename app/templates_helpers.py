"""Shared Jinja2 templates configuration with global functions."""
from fastapi.templating import Jinja2Templates
from datetime import datetime


def get_current_year() -> int:
    """Get the current year."""
    return datetime.now().year


# Create templates instance with global functions
templates = Jinja2Templates(directory="app/templates")

# Add global function for current year
templates.env.globals["current_year"] = get_current_year

