#!/usr/bin/env python3
"""Entry point for running the DiviTracker Flask application."""

import os
from pathlib import Path

from app.factory import create_app

# Ensure instance folder exists for SQLite database
instance_path = Path(__file__).parent / "instance"
instance_path.mkdir(exist_ok=True)

# Get configuration from environment or default to development
config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True))
