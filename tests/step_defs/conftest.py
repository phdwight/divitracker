"""Conftest for step definitions - registers shared UI steps."""

# Register ui_shared_steps as a pytest plugin so its steps are discovered
pytest_plugins = ["tests.step_defs.ui_shared_steps"]
